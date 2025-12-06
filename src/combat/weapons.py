"""
WEAPONS MODULE
Implementasi visualisasi proyektil (Bullet).
"""
import pygame
from settings import BULLET_SPEED, BULLET_LIFETIME


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
