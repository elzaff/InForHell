"""
UI PARTICLES MODULE
Partikel efek api untuk background menu.
"""
import pygame


class FireParticle:
    """Partikel efek api untuk background menu"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = pygame.math.Vector2(
            (pygame.math.Vector2(0, 0).x - 0.5) * 2,
            -abs(pygame.math.Vector2(0, 0).y - 1) * 3 - 1
        )
        self.vy = -abs(pygame.math.Vector2(0, 0).y - 1) * 3 - 1
        self.lifetime = pygame.math.Vector2(0, 0).x * 60 + 30  # 30-90 frames
        self.age = 0
        self.size = pygame.math.Vector2(0, 0).x * 4 + 2  # 2-6 pixels
        
        # Warna api: merah -> oranye -> kuning
        r = int(255)
        g = int(pygame.math.Vector2(0, 0).x * 100)
        b = 0
        self.color = (r, g, b)
    
    def update(self):
        self.x += (pygame.math.Vector2(0, 0).x - 0.5) * 0.5
        self.y += self.vy
        self.age += 1
        
        # Fade out
        alpha = 1 - (self.age / self.lifetime)
        if alpha < 0:
            alpha = 0
        self.alpha = alpha
        
        return self.age < self.lifetime
    
    def draw(self, surface):
        if self.alpha > 0:
            # Buat surface dengan alpha
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            alpha_val = int(self.alpha * 255)
            color = (*self.color, alpha_val)
            pygame.draw.circle(s, color, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)), special_flags=pygame.BLEND_RGBA_ADD)
