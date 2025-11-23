"""
SPRITES MODULE
Implementasi sprite dasar untuk objek game static.
Objek dinamis (Enemy, Weapon) dipindahkan ke modul terpisah.
"""
from settings import * 
import pygame

# ==================== BASIC SPRITES ====================

class Sprite(pygame.sprite.Sprite):
    """
    Sprite dasar untuk objek visual (misal: tanah, dekorasi).
    """
    def __init__(self, pos: tuple[int, int], surf: pygame.Surface, groups: tuple[pygame.sprite.Group, ...]):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    """
    Sprite untuk objek yang memiliki collision (misal: tembok, obstacle).
    """
    def __init__(self, pos: tuple[int, int], surf: pygame.Surface, groups: tuple[pygame.sprite.Group, ...]):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)