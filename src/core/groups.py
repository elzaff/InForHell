"""
GROUPS MODULE
Custom sprite group untuk rendering dengan camera offset
"""
import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        self.map_width = 0
        self.map_height = 0
    
    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)

        # Camera constraints
        if self.map_width and self.map_height:
            if self.offset.x > 0: self.offset.x = 0
            if self.offset.x < -(self.map_width - WINDOW_WIDTH): self.offset.x = -(self.map_width - WINDOW_WIDTH)
            if self.offset.y > 0: self.offset.y = 0
            if self.offset.y < -(self.map_height - WINDOW_HEIGHT): self.offset.y = -(self.map_height - WINDOW_HEIGHT)

        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')] 
        object_sprites = [sprite for sprite in self if not hasattr(sprite, 'ground')] 
        
        for layer in [ground_sprites, object_sprites]:
            for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery):
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
