"""
WEAPONS MODULE
Implementasi visualisasi proyektil (Bullet, KeyboardProjectile).
"""
from settings import *
import pygame
from math import degrees, atan2
from os.path import join
from random import randint

class Bullet(pygame.sprite.Sprite):
    """
    Kelas untuk proyektil peluru.
    """
    def __init__(self, surf: pygame.Surface, pos: tuple[int, int], direction: pygame.Vector2, 
                 groups: tuple[pygame.sprite.Group, ...], damage: int = 10):
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_frect(center = pos)
        
        # Atribut Privat
        self.__spawn_time = pygame.time.get_ticks()
        self.__lifetime = BULLET_LIFETIME
        self.__direction = direction 
        self.__speed = BULLET_SPEED
        self.__damage = damage
    
    @property
    def damage(self) -> int:
        """Mengembalikan damage peluru"""
        return self.__damage
    
    def update(self, dt: float) -> None:
        """Update posisi peluru dan cek lifetime"""
        self.rect.center += self.__direction * self.__speed * dt

        if pygame.time.get_ticks() - self.__spawn_time >= self.__lifetime:
            self.kill()


class KeyboardProjectile(pygame.sprite.Sprite):
    """
    Proyektil untuk skill Keyboard Rain.
    Bentuk kotak sederhana (prototype).
    """
    def __init__(self, pos: tuple[int, int], groups: tuple[pygame.sprite.Group, ...], damage: int = 20):
        super().__init__(groups)
        
        # Visual Prototype: Kotak putih/abu-abu
        size = randint(20, 40)
        self.image = pygame.Surface((size, size))
        color_val = randint(150, 255)
        self.image.fill((color_val, color_val, color_val))
        
        self.rect = self.image.get_frect(center = pos)
        
        # Logic
        self.__spawn_time = pygame.time.get_ticks()
        self.__lifetime = 500 # 0.5 detik
        self.__damage = damage
        
        # Efek jatuh sedikit
        self.__fall_speed = randint(100, 300)
    
    @property
    def damage(self) -> int:
        return self.__damage
        
    def update(self, dt: float) -> None:
        """Update posisi (jatuh) dan lifetime"""
        self.rect.y += self.__fall_speed * dt
        
        if pygame.time.get_ticks() - self.__spawn_time >= self.__lifetime:
            self.kill()
