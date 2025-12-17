"""
Combat Mechanics Module
Base classes untuk upgrade, weapon, skill, dan passive items.
"""
import pygame
import math
from abc import ABC, abstractmethod
from settings import GUN_COOLDOWN, PLAYER_BASE_DAMAGE, WINDOW_WIDTH, WINDOW_HEIGHT


class Upgrade(ABC):
    """Abstract base class untuk semua item yang bisa di-upgrade."""
    
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
        """Cek apakah bisa di-upgrade."""
        return self.__level < self.__max_level
    
    def level_up(self):
        """Naikkan level upgrade."""
        if self.can_level_up():
            self.__level += 1
            self._on_level_up()
    
    @abstractmethod
    def _on_level_up(self):
        """Hook untuk behavior saat level up."""
        pass


class AttackMechanism(Upgrade, ABC):
    """Abstract base class untuk weapon dan skill."""
    
    def __init__(self, name: str, description: str, cooldown: float, damage: float, max_level: int = 5):
        super().__init__(name, description, max_level)
        self.__base_cooldown = cooldown
        self.__timer = 0
        self.__damage = damage
        self.__cooldown_modifier = 1.0
    
    @property
    def cooldown(self):
        """Cooldown dengan modifier."""
        return self.__base_cooldown * self.__cooldown_modifier
    
    @property
    def damage(self):
        return self.__damage
    
    @property
    def cooldown_progress(self) -> float:
        """Progress cooldown dari 0.0 sampai 1.0."""
        actual_cooldown = self.cooldown
        if actual_cooldown == 0: return 1.0
        return min(1.0, self.__timer / actual_cooldown)
    
    def can_attack(self) -> bool:
        """Cek apakah attack ready."""
        return self.__timer >= self.cooldown
    
    def set_cooldown_modifier(self, modifier: float):
        """Set modifier cooldown dari player."""
        self.__cooldown_modifier = modifier
    
    def update(self, dt: float):
        """Update timer cooldown."""
        self.__timer += dt * 1000
    
    def reset_timer(self):
        """Reset timer setelah attack."""
        self.__timer = 0
        
    def _modify_cooldown(self, amount: float):
        """Modify base cooldown (internal)."""
        self.__base_cooldown = max(50, self.__base_cooldown + amount)
    
    def _modify_damage(self, amount: float):
        """Modify damage (internal)."""
        self.__damage += amount
    
    @abstractmethod
    def attack(self):
        """Execute attack logic."""
        pass
    
    @abstractmethod
    def _on_level_up(self):
        """Level up behavior."""
        pass


class WeaponDefault(AttackMechanism):
    """Senjata default player (auto-shoot)."""
    
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
        """Tembak peluru ke arah mouse. Supports multi-shot."""
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        base_direction = pygame.Vector2(1, 0)
        
        if (mouse_pos - player_pos).length() > 0:
            base_direction = (mouse_pos - player_pos).normalize()
        
        multi_shot = getattr(self.__player, 'multi_shot_count', 1)
        
        # Single shot
        if multi_shot <= 1:
            return {
                'damage': self.damage,
                'position': self.__player.rect.center,
                'direction': base_direction
            }
        
        # Multi-shot dengan spread
        spread_angle = 30
        bullets = []
        
        if multi_shot == 2:
            angles = [-spread_angle/4, spread_angle/4]
        elif multi_shot == 3:
            angles = [-spread_angle/2, 0, spread_angle/2]
        else:
            step = spread_angle / (multi_shot - 1)
            angles = [(-spread_angle/2) + (i * step) for i in range(multi_shot)]
        
        for angle_offset in angles:
            radians = math.radians(angle_offset)
            cos_a = math.cos(radians)
            sin_a = math.sin(radians)
            
            new_dir = pygame.Vector2(
                base_direction.x * cos_a - base_direction.y * sin_a,
                base_direction.x * sin_a + base_direction.y * cos_a
            )
            
            bullets.append({
                'damage': self.damage,
                'position': self.__player.rect.center,
                'direction': new_dir
            })
        
        return {'multi': True, 'bullets': bullets}
    
    def _on_level_up(self) -> None:
        """Bonus per level: +5 damage, -10ms cooldown."""
        self._modify_damage(5)
        self._modify_cooldown(-10)


class Skill(AttackMechanism):
    """Active skill yang dikumpulkan saat level up."""
    
    def __init__(self, name: str, description: str, cooldown: float, damage: float):
        super().__init__(name, description, cooldown, damage, max_level=5)
        self.__projectile_count = 1
        self.__duration = 3000
        self.__is_active = False
        self.__active_timer = 0
    
    @property
    def projectile_count(self):
        return self.__projectile_count
        
    @property
    def is_active(self):
        return self.__is_active
    
    def activate(self):
        """Aktivasi skill jika ready."""
        if self.can_attack():
            self.__is_active = True
            self.__active_timer = pygame.time.get_ticks()
            self.reset_timer()
            return True
        return False
            
    def update_active(self, current_time):
        """Cek apakah durasi skill sudah habis."""
        if self.__is_active:
            if current_time - self.__active_timer >= self.__duration:
                self.__is_active = False

    def attack(self):
        """Execute skill attack logic."""
        pass
    
    def _on_level_up(self):
        """Bonus per level: +10 damage, +1 projectile setiap 2 level."""
        self._modify_damage(10)
        if self.level % 2 == 0:
            self.__projectile_count += 1


class PassiveItem(Upgrade):
    """Passive item yang memberikan stat boost."""
    
    def __init__(self, name: str, description: str, stat_type: str, value: float, max_level: int = 5):
        super().__init__(name, description, max_level)
        self.__stat_type = stat_type
        self.__value = value
    
    @property
    def stat_type(self):
        return self.__stat_type
    
    @property
    def value(self):
        return self.__value
    
    def apply_stat(self, player):
        """Apply passive stat bonus ke player."""
        pass
    
    def _on_level_up(self):
        """Increase stat value 20% per level."""
        self.__value *= 1.2


class VitalityPassive(PassiveItem):
    """Passive: Increase max HP."""
    
    def __init__(self):
        super().__init__(
            name="Vitality",
            description="Increase maximum health",
            stat_type='hp',
            value=20,
            max_level=5
        )
    
    def apply_stat(self, player):
        player.stats.increase_max_health(self.value)


class SpeedBoostPassive(PassiveItem):
    """Passive: Increase movement speed."""
    
    def __init__(self):
        super().__init__(
            name="Speed Boost",
            description="Increase movement speed",
            stat_type='speed',
            value=0.1,
            max_level=5
        )
    
    def apply_stat(self, player):
        player.stat_modifiers['speed'] += self.value


class DamageBoostPassive(PassiveItem):
    """Passive: Increase damage."""
    
    def __init__(self):
        super().__init__(
            name="Damage Boost",
            description="Increase damage dealt",
            stat_type='damage',
            value=0.15,
            max_level=5
        )
    
    def apply_stat(self, player):
        player.stat_modifiers['damage'] += self.value


class HealthRegenPassive(PassiveItem):
    """Passive: Regenerate HP over time."""
    
    def __init__(self):
        super().__init__(
            name="Health Regeneration",
            description="Regenerate HP over time",
            stat_type='regen',
            value=1,
            max_level=5
        )
    
    def apply_stat(self, player):
        if hasattr(player, 'increase_regen_rate'):
            player.increase_regen_rate(self.value)
