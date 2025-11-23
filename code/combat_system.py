"""
LAYER 3: Combat System - Upgrade, AttackMechanism, WeaponDefault, Skill, PassiveItem
Implementasi sesuai class diagram
"""
from abc import ABC, abstractmethod
from settings import *
import pygame
from random import randint, choice

# ==================== UPGRADE BASE CLASS ====================

class Upgrade(ABC):
    """
    Abstract Base Class untuk semua upgradeable items
    Properties: __name, __desc, __level, __max_level
    Methods: level_up() (abstract), can_level_up()
    """
    
    def __init__(self, name: str, description: str, max_level: int = 5):
        self.__name = name
        self.__description = description
        self.__level = 1
        self.__max_level = max_level
    
    @property
    def name(self):
        return self.__name
    
    @property
    def description(self):
        return self.__description
    
    @property
    def level(self):
        return self.__level
    
    @property
    def max_level(self):
        return self.__max_level
    
    def can_level_up(self) -> bool:
        """Check if upgrade can be leveled up"""
        return self.__level < self.__max_level
    
    def level_up(self):
        """Level up upgrade"""
        if self.can_level_up():
            self.__level += 1
            self._on_level_up()
    
    @abstractmethod
    def _on_level_up(self):
        """Hook untuk behavior saat level up - must be implemented"""
        pass


# ==================== ATTACK MECHANISM BASE CLASS ====================

class AttackMechanism(Upgrade, ABC):
    """
    Abstract Base Class untuk semua attack mechanisms (weapons & skills)
    Extends: Upgrade
    Properties: __cooldown, __timer, __damage
    Methods: update(dt), attack() (abstract), can_attack()
    """
    
    def __init__(self, name: str, description: str, cooldown: float, damage: float, max_level: int = 5):
        super().__init__(name, description, max_level)
        self.__cooldown = cooldown
        self.__timer = 0
        self.__damage = damage
    
    @property
    def cooldown(self):
        return self.__cooldown
    
    @property
    def damage(self):
        return self.__damage
    
    def can_attack(self) -> bool:
        """Check if attack is ready (cooldown elapsed)"""
        return self.__timer >= self.__cooldown
    
    def update(self, dt: float):
        """Update timer"""
        self.__timer += dt * 1000  # Convert to milliseconds
        
        # If ready to attack, execute attack
        # Note: Untuk skill aktif, attack() dipanggil manual via input
        # Untuk passive/auto weapon, bisa dipanggil di sini jika diinginkan
    
    def reset_timer(self):
        """Reset timer setelah attack"""
        self.__timer = 0
        
    def _modify_cooldown(self, amount: float):
        """Protected method untuk modify cooldown"""
        self.__cooldown = max(50, self.__cooldown + amount)  # Min 50ms cooldown
    
    def _modify_damage(self, amount: float):
        """Protected method untuk modify damage"""
        self.__damage += amount
    
    @abstractmethod
    def attack(self):
        """Execute attack logic - must be implemented by subclass"""
        pass
    
    @abstractmethod
    def _on_level_up(self):
        """Level up behavior - must be implemented by subclass"""
        pass


# ==================== WEAPON DEFAULT ====================

class WeaponDefault(AttackMechanism):
    """
    Senjata default player (pistol).
    Extends: AttackMechanism
    """
    
    def __init__(self, player, groups):
        super().__init__(
            name="Default Gun",
            description="Senjata dasar yang menembakkan peluru",
            cooldown=GUN_COOLDOWN,
            damage=PLAYER_BASE_DAMAGE,
            max_level=10
        )
        self.__player = player
        self.__groups = groups
    
    def attack(self) -> dict:
        """
        Menembakkan peluru.
        Returns: Dictionary berisi info untuk spawn bullet di main loop.
        """
        # Hitung arah ke mouse
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        direction = pygame.Vector2(1, 0)
        
        if (mouse_pos - player_pos).length() > 0:
            direction = (mouse_pos - player_pos).normalize()
            
        return {
            'damage': self.damage,
            'position': self.__player.rect.center,
            'direction': direction
        }
    
    def _on_level_up(self) -> None:
        """Meningkatkan damage dan mengurangi cooldown saat level up"""
        self._modify_damage(5)  # +5 damage per level
        self._modify_cooldown(-10)  # -10ms cooldown per level


# ==================== SKILL ====================

class Skill(AttackMechanism):
    """
    Active skill yang dikumpulkan saat level up
    Extends: AttackMechanism
    """
    
    def __init__(self, name: str, description: str, cooldown: float, damage: float):
        super().__init__(name, description, cooldown, damage, max_level=5)
        self.__projectile_count = 1
        self.__duration = 3000 # Default 3 seconds
        self.__is_active = False
        self.__active_timer = 0
    
    @property
    def projectile_count(self):
        return self.__projectile_count
        
    @property
    def is_active(self):
        return self.__is_active
    
    def activate(self):
        """Activate skill if cooldown ready"""
        if self.can_attack():
            self.__is_active = True
            self.__active_timer = pygame.time.get_ticks()
            self.reset_timer()
            return True
        return False
            
    def update_active(self, current_time):
        """Check if skill duration ended"""
        if self.__is_active:
            if current_time - self.__active_timer >= self.__duration:
                self.__is_active = False

    def attack(self):
        """Execute skill attack logic"""
        pass
    
    def _on_level_up(self):
        """Increase damage and projectile count"""
        self._modify_damage(10)  # +10 damage per level
        if self.level % 2 == 0:  # Every 2 levels
            self.__projectile_count += 1


# Concrete Skill Implementations
class KeyboardRain(Skill):
    """
    Skill: Keyboard Rain
    Menjatuhkan objek 'keyboard' secara acak di layar.
    """
    
    def __init__(self, groups):
        super().__init__(
            name="Keyboard Rain",
            description="Hujan keyboard yang melukai musuh",
            cooldown=5000, # 5 detik cooldown
            damage=20
        )
        self.__groups = groups
        self.__spawn_timer = 0
        self.__spawn_interval = 100 # Spawn setiap 100ms saat aktif
        
    def update(self, dt):
        super().update(dt)
        current_time = pygame.time.get_ticks()
        self.update_active(current_time)
        
        if self.is_active:
            if current_time - self.__spawn_timer >= self.__spawn_interval:
                self.attack()
                self.__spawn_timer = current_time
                
    def attack(self):
        """Spawn keyboard projectile"""
        # Import di sini untuk menghindari circular import jika ada
        from weapons import KeyboardProjectile
        
        # Spawn area: 800x600 box around player
        # Karena kita tidak punya akses langsung ke player position di sini (kecuali kita simpan di init),
        # kita akan spawn random di layar (asumsi camera center = player center).
        # Tapi tunggu, kita butuh posisi absolut di world.
        # Solusi: Kita tambahkan player ke __init__ Skill atau pass player position ke update/attack.
        # Untuk saat ini, kita spawn di sekitar (0,0) jika tidak ada info, TAPI ini buruk.
        # LEBIH BAIK: Kita update __init__ KeyboardRain untuk menerima player object juga.
        
        # Namun, mengubah signature init akan merusak inheritance jika tidak hati-hati.
        # Mari kita gunakan spawn random di sekitar camera view (yang kita tidak tahu).
        # ALTERNATIF: Kita spawn di random position di map? Tidak efisien.
        
        # FIX: Kita ubah __init__ KeyboardRain di main.py untuk menerima player, 
        # dan simpan self.player.
        pass 
        
    def set_player(self, player):
        """Set player reference"""
        self.player = player
        
    def attack(self):
        """Spawn keyboard projectile"""
        from weapons import KeyboardProjectile
        
        if hasattr(self, 'player'):
            # Spawn area: 800x600 box around player
            offset_x = randint(-400, 400)
            offset_y = randint(-300, 300)
            spawn_pos = (self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y)
            
            KeyboardProjectile(spawn_pos, self.__groups, self.damage)


# ==================== PASSIVE ITEM ====================

class PassiveItem(Upgrade):
    """
    Passive item yang memberikan stat boost
    Extends: Upgrade
    Properties: __stat_type, __value
    Methods: apply_stat(player), level_up()
    """
    
    def __init__(self, name: str, description: str, stat_type: str, value: float, max_level: int = 5):
        super().__init__(name, description, max_level)
        self.__stat_type = stat_type  # 'hp', 'speed', 'damage', 'regen'
        self.__value = value
    
    @property
    def stat_type(self):
        return self.__stat_type
    
    @property
    def value(self):
        return self.__value
    
    def apply_stat(self, player):
        """Apply passive stat bonus to player"""
        # Implementation tergantung stat_type
        if self.__stat_type == 'hp':
            # Increase max HP
            pass
        elif self.__stat_type == 'speed':
            # Increase speed multiplier
            pass
        elif self.__stat_type == 'damage':
            # Increase damage multiplier
            pass
        elif self.__stat_type == 'regen':
            # Add HP regeneration
            pass
    
    def _on_level_up(self):
        """Increase stat value"""
        self.__value *= 1.2  # 20% increase per level


# Concrete Passive Item Implementations
class VitalityPassive(PassiveItem):
    """Passive: Increase max HP"""
    
    def __init__(self):
        super().__init__(
            name="Vitality",
            description="Increase maximum health",
            stat_type='hp',
            value=20,
            max_level=5
        )
    
    def apply_stat(self, player):
        """Increase player max HP"""
        player.stats.increase_max_health(self.value)


class SpeedBoostPassive(PassiveItem):
    """Passive: Increase movement speed"""
    
    def __init__(self):
        super().__init__(
            name="Speed Boost",
            description="Increase movement speed",
            stat_type='speed',
            value=0.1,  # +10% multiplier (additive)
            max_level=5
        )
    
    def apply_stat(self, player):
        """Increase player speed"""
        player.stat_modifiers['speed'] += self.value


class DamageBoostPassive(PassiveItem):
    """Passive: Increase damage"""
    
    def __init__(self):
        super().__init__(
            name="Damage Boost",
            description="Increase damage dealt",
            stat_type='damage',
            value=0.15,  # +15% multiplier (additive)
            max_level=5
        )
    
    def apply_stat(self, player):
        """Increase player damage"""
        player.stat_modifiers['damage'] += self.value


class HealthRegenPassive(PassiveItem):
    """Passive: Regenerate HP over time"""
    
    def __init__(self):
        super().__init__(
            name="Health Regeneration",
            description="Regenerate HP over time",
            stat_type='regen',
            value=1,  # +1 HP per second
            max_level=5
        )
    
    def apply_stat(self, player):
        """Apply HP regeneration"""
        player.increase_regen_rate(self.value)
