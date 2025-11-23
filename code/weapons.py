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


class ProjectileShadow(pygame.sprite.Sprite):
    """
    Bayangan untuk proyektil jatuh.
    """
    def __init__(self, pos: tuple[int, int], size: tuple[int, int], groups: tuple[pygame.sprite.Group, ...]):
        super().__init__(groups)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        # Gambar elips hitam transparan sebagai bayangan
        pygame.draw.ellipse(self.image, (0, 0, 0, 100), (0, 0, size[0], size[1]))
        self.rect = self.image.get_frect(center=pos)

class KeyboardProjectile(pygame.sprite.Sprite):
    """
    Proyektil untuk skill Keyboard Rain.
    Jatuh dari langit ke posisi target.
    """
    def __init__(self, target_pos: tuple[int, int], groups: tuple[pygame.sprite.Group, ...], damage: int = 100):
        super().__init__(groups)
        
        # Visual: Persegi panjang 120x60
        self.image = pygame.Surface((120, 60))
        self.image.fill((200, 200, 200)) # Abu-abu terang
        # Tambahkan border agar terlihat lebih jelas
        pygame.draw.rect(self.image, (50, 50, 50), (0, 0, 120, 60), 2)
        
        # Posisi Target (Tanah)
        self.__target_pos = pygame.Vector2(target_pos)
        self.rect = self.image.get_frect(center=target_pos)
        
        # Mekanisme Jatuh (Z-axis simulation)
        self.__height = 1000.0 # Mulai dari ketinggian 1000 piksel
        self.__fall_speed = 1000.0 # Kecepatan jatuh piksel/detik
        
        # Update posisi awal berdasarkan ketinggian
        self.rect.centery = self.__target_pos.y - self.__height
        
        # Shadow
        self.__shadow = ProjectileShadow(target_pos, (120, 60), groups)
        
        # Logic
        self.__damage = damage
        self.__has_landed = False
        self.__impact_time = 0
        self.__linger_duration = 200 # Durasi ada di tanah sebelum hilang
    
    @property
    def damage(self) -> int:
        # Berikan damage baik saat jatuh maupun saat mendarat
        return self.__damage
        
    def update(self, dt: float) -> None:
        """Update posisi jatuh"""
        if not self.__has_landed:
            # Kurangi ketinggian
            self.__height -= self.__fall_speed * dt
            
            # Update posisi Y visual
            self.rect.centery = self.__target_pos.y - self.__height
            
            # Cek jika sudah menyentuh tanah
            if self.__height <= 0:
                self.__height = 0
                self.rect.centery = self.__target_pos.y
                self.__has_landed = True
                self.__impact_time = pygame.time.get_ticks()
                # Hapus bayangan saat mendarat (opsional, atau biarkan sampai hilang)
                self.__shadow.kill()
        else:
            # Jika sudah mendarat, diam sebentar lalu hilang
            if pygame.time.get_ticks() - self.__impact_time >= self.__linger_duration:
                self.kill()
    
    def kill(self):
        # Pastikan shadow juga terhapus jika proyektil dihapus
        if self.__shadow.alive():
            self.__shadow.kill()
        super().kill()
