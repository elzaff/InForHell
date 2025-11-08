"""
LAYER 1: Base Classes - GameEntity & Actor
Implementasi sesuai class diagram dengan encapsulation penuh
"""
from abc import ABC, abstractmethod
from settings import *
import pygame


# ==================== LAYER 1: BASE CLASSES ====================

class GameEntity(pygame.sprite.Sprite, ABC):
    """
    Abstract Base Class untuk semua objek game
    Properties: __position, __sprite, __rect, __is_active
    Methods: update(dt), kill()
    """
    
    def __init__(self, pos, groups):
        super().__init__(groups)
        self._GameEntity__position = pygame.Vector2(pos)
        self._GameEntity__is_active = True
    
    @property
    def position(self):
        """Get position"""
        return self._GameEntity__position
    
    @property
    def is_active(self):
        """Check if entity is active"""
        return self._GameEntity__is_active
    
    def deactivate(self):
        """Deactivate entity"""
        self._GameEntity__is_active = False
        self.kill()
    
    @abstractmethod
    def update(self, dt):
        """Update logic setiap frame - must be implemented by subclass"""
        pass


class Actor(GameEntity, ABC):
    """
    Abstract Base Class untuk entitas yang hidup (Player & Enemy)
    Extends: GameEntity
    Properties: __hp_max, __hp_current, __speed
    Methods: take_damage(), heal(), die(), is_alive()
    """
    
    def __init__(self, pos, groups, hp_max, speed):
        super().__init__(pos, groups)
        self.__hp_max = hp_max
        self.__hp_current = hp_max
        self.__speed = speed
    
    # Getters
    @property
    def hp_max(self):
        return self.__hp_max
    
    @property
    def hp_current(self):
        return self.__hp_current
    
    @property
    def speed(self):
        return self.__speed
    
    @property
    def health_percentage(self):
        return self.__hp_current / self.__hp_max if self.__hp_max > 0 else 0
    
    def is_alive(self) -> bool:
        """Check if actor is still alive"""
        return self.__hp_current > 0
    
    def take_damage(self, amount: float) -> bool:
        """
        Kurangi HP
        Returns: True jika baru mati, False jika masih hidup atau sudah mati
        """
        if self.is_alive():
            self.__hp_current = max(0, self.__hp_current - amount)
            if self.__hp_current <= 0:
                self.die()
                return True
        return False
    
    def heal(self, amount: float):
        """Tambah HP (tidak bisa melebihi max)"""
        if self.is_alive():
            self.__hp_current = min(self.__hp_max, self.__hp_current + amount)
    
    def _increase_max_hp(self, amount: float):
        """Protected method untuk increase max HP"""
        self.__hp_max += amount
        self.__hp_current += amount  # Heal sebesar kenaikan
    
    def _increase_speed(self, amount: float):
        """Protected method untuk increase speed"""
        self.__speed += amount
    
    @abstractmethod
    def die(self):
        """Logic saat actor mati - must be implemented by subclass"""
        pass
    
    @abstractmethod
    def update(self, dt):
        """Update logic - must be implemented by subclass"""
        pass


# ==================== PROJECTILE BASE CLASS ====================

class Projectile(GameEntity, ABC):
    """
    Abstract Base Class untuk semua projectiles
    Extends: GameEntity
    Properties: __damage, __direction, __speed, __pierce, __max_range, __distance_traveled
    Methods: update(dt), is_expired()
    """
    
    def __init__(self, pos, groups, damage, direction, speed, pierce=1, max_range=1000):
        super().__init__(pos, groups)
        self.__damage = damage
        self.__direction = pygame.Vector2(direction).normalize()
        self.__speed = speed
        self.__pierce = pierce
        self.__max_range = max_range
        self.__distance_traveled = 0
        self.__enemies_hit = 0
    
    @property
    def damage(self):
        return self.__damage
    
    @property
    def direction(self):
        return self.__direction
    
    @property
    def pierce(self):
        return self.__pierce
    
    def hit_enemy(self) -> bool:
        """
        Call saat projectile hit enemy
        Returns: True jika projectile masih bisa hit lagi, False jika harus destroyed
        """
        self.__enemies_hit += 1
        return self.__enemies_hit < self.__pierce
    
    def is_expired(self) -> bool:
        """Check if projectile should be removed"""
        return (self.__distance_traveled >= self.__max_range or 
                self.__enemies_hit >= self.__pierce or
                not self.is_active)
    
    def update(self, dt):
        """Update projectile position"""
        if self.is_active:
            # Move projectile
            distance_this_frame = self.__speed * dt
            self._GameEntity__position += self.__direction * distance_this_frame
            self.__distance_traveled += distance_this_frame
            
            # Update rect position
            self.rect.center = self._GameEntity__position
            
            # Check expiration
            if self.is_expired():
                self.deactivate()


# ==================== ITEM DROP BASE CLASS ====================

class ItemDrop(GameEntity, ABC):
    """
    Abstract Base Class untuk item yang jatuh di map
    Extends: GameEntity
    Properties: __attraction_radius, __value
    Methods: on_pickup(player)
    """
    
    def __init__(self, pos, groups, value, attraction_radius=100):
        super().__init__(pos, groups)
        self.__value = value
        self.__attraction_radius = attraction_radius
        self.__is_attracted = False
    
    @property
    def value(self):
        return self.__value
    
    @property
    def attraction_radius(self):
        return self.__attraction_radius
    
    def check_attraction(self, player_pos: pygame.Vector2):
        """Check if item should be attracted to player"""
        distance = (player_pos - self._GameEntity__position).length()
        if distance <= self.__attraction_radius:
            self.__is_attracted = True
            return True
        return False
    
    def move_towards_player(self, player_pos: pygame.Vector2, dt: float, speed: float = 400):
        """Move item towards player"""
        if self.__is_attracted:
            direction = (player_pos - self._GameEntity__position).normalize()
            self._GameEntity__position += direction * speed * dt
            self.rect.center = self._GameEntity__position
    
    @abstractmethod
    def on_pickup(self, player):
        """Logic saat player pickup item - must be implemented by subclass"""
        pass
    
    def update(self, dt):
        """Default update - can be overridden"""
        pass
