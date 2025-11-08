"""
LAYER 3: Combat System - Upgrade, AttackMechanism, WeaponDefault, Skill, PassiveItem
Implementasi sesuai class diagram
"""
from abc import ABC, abstractmethod
from settings import *
import pygame


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
        if self.can_attack():
            self.attack()
            self.__timer = 0  # Reset timer
    
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
    Senjata default player (gun)
    Extends: AttackMechanism
    """
    
    def __init__(self, player, bullet_sprite, groups, gun_sprite):
        super().__init__(
            name="Default Gun",
            description="Basic weapon that shoots bullets",
            cooldown=GUN_COOLDOWN,
            damage=PLAYER_BASE_DAMAGE,
            max_level=10
        )
        self.__player = player
        self.__bullet_sprite = bullet_sprite
        self.__groups = groups
        self.__gun_sprite = gun_sprite
    
    def attack(self):
        """Shoot bullet from gun"""
        # Implementation akan dipanggil dari game manager
        pass
    
    def _on_level_up(self):
        """Increase damage and reduce cooldown"""
        self._modify_damage(5)  # +5 damage per level
        self._modify_cooldown(-10)  # -10ms cooldown per level
    
    def get_shoot_info(self):
        """Return info needed to spawn bullet"""
        return {
            'damage': self.damage,
            'position': self.__gun_sprite.rect.center if self.__gun_sprite else self.__player.rect.center,
            'direction': self.__gun_sprite.player_direction if self.__gun_sprite else pygame.Vector2(1, 0)
        }


# ==================== SKILL ====================

class Skill(AttackMechanism):
    """
    Active skill yang dikumpulkan saat level up
    Extends: AttackMechanism
    """
    
    def __init__(self, name: str, description: str, cooldown: float, damage: float):
        super().__init__(name, description, cooldown, damage, max_level=5)
        self.__projectile_count = 1
    
    @property
    def projectile_count(self):
        return self.__projectile_count
    
    def attack(self):
        """Execute skill attack"""
        # Implementation akan dipanggil dari game manager
        pass
    
    def _on_level_up(self):
        """Increase damage and projectile count"""
        self._modify_damage(10)  # +10 damage per level
        if self.level % 2 == 0:  # Every 2 levels
            self.__projectile_count += 1


# Concrete Skill Implementations (placeholder untuk future implementation)
class FireballSkill(Skill):
    """Skill: Fireball yang menembak projectile"""
    
    def __init__(self):
        super().__init__(
            name="Fireball",
            description="Shoot fireball projectiles",
            cooldown=2000,
            damage=25
        )
    
    def attack(self):
        pass


class LightningSkill(Skill):
    """Skill: Lightning strike area damage"""
    
    def __init__(self):
        super().__init__(
            name="Lightning Strike",
            description="Strike enemies with lightning",
            cooldown=3000,
            damage=40
        )
    
    def attack(self):
        pass


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
        # Will be implemented
        pass


class SpeedBoostPassive(PassiveItem):
    """Passive: Increase movement speed"""
    
    def __init__(self):
        super().__init__(
            name="Speed Boost",
            description="Increase movement speed",
            stat_type='speed',
            value=1.1,  # 10% multiplier
            max_level=5
        )
    
    def apply_stat(self, player):
        """Increase player speed"""
        # Will be implemented
        pass


class DamageBoostPassive(PassiveItem):
    """Passive: Increase damage"""
    
    def __init__(self):
        super().__init__(
            name="Damage Boost",
            description="Increase damage dealt",
            stat_type='damage',
            value=1.15,  # 15% multiplier
            max_level=5
        )
    
    def apply_stat(self, player):
        """Increase player damage"""
        # Will be implemented
        pass


class HealthRegenPassive(PassiveItem):
    """Passive: Regenerate HP over time"""
    
    def __init__(self):
        super().__init__(
            name="Health Regeneration",
            description="Regenerate HP over time",
            stat_type='regen',
            value=2,  # HP per second
            max_level=5
        )
        self.__last_regen = 0
        self.__regen_interval = 1000  # 1 second
    
    def apply_stat(self, player):
        """Apply HP regeneration"""
        current_time = pygame.time.get_ticks()
        if current_time - self.__last_regen >= self.__regen_interval:
            # player.heal(self.value * self.level)
            self.__last_regen = current_time
