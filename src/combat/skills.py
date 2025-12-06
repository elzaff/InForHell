"""
SKILLS MODULE
Implementasi skill aktif (KeyboardRain, dll).
"""
import pygame
from random import randint
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


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


class KeyboardRain:
    """
    Skill: Keyboard Rain
    Menjatuhkan objek 'keyboard' secara acak di layar.
    """
    
    def __init__(self, groups):
        self.__groups = groups
        self.__spawn_timer = 0
        self.__spawn_interval = 100 # Spawn setiap 100ms saat aktif
        self.player = None
        
        # Skill properties
        self.__name = "Keyboard Rain"
        self.__description = "Hujan keyboard yang melukai musuh"
        self.__base_cooldown = 10000 # 10 detik cooldown
        self.__damage = 100
        self.__timer = 0
        self.__cooldown_modifier = 1.0
        
        # Active state
        self.__is_active = False
        self.__active_timer = 0
        self.__duration = 3000  # 3 seconds
        
    @property
    def name(self):
        return self.__name
    
    @property
    def cooldown(self):
        """Get actual cooldown with modifier applied"""
        return self.__base_cooldown * self.__cooldown_modifier
    
    @property
    def damage(self):
        return self.__damage
    
    @property
    def cooldown_progress(self) -> float:
        """Return progress 0.0 to 1.0"""
        actual_cooldown = self.cooldown
        if actual_cooldown == 0: return 1.0
        return min(1.0, self.__timer / actual_cooldown)
    
    @property
    def is_active(self):
        return self.__is_active
    
    def can_attack(self) -> bool:
        """Check if attack is ready (cooldown elapsed)"""
        return self.__timer >= self.cooldown
    
    def set_cooldown_modifier(self, modifier: float):
        """Set cooldown modifier from player stat_modifiers"""
        self.__cooldown_modifier = modifier
    
    def set_player(self, player):
        """Set player reference"""
        self.player = player
    
    def activate(self):
        """Activate skill if cooldown ready"""
        if self.can_attack():
            self.__is_active = True
            self.__active_timer = pygame.time.get_ticks()
            self.__timer = 0  # Reset timer
            return True
        return False
    
    def update_active(self, current_time):
        """Check if skill duration ended"""
        if self.__is_active:
            if current_time - self.__active_timer >= self.__duration:
                self.__is_active = False
        
    def update(self, dt):
        """Update timer and spawn projectiles when active"""
        self.__timer += dt * 1000  # Convert to milliseconds
        current_time = pygame.time.get_ticks()
        self.update_active(current_time)
        
        if self.__is_active:
            if current_time - self.__spawn_timer >= self.__spawn_interval:
                self.attack()
                self.__spawn_timer = current_time
                
    def attack(self):
        """Spawn keyboard projectile"""
        if self.player:
            # Spawn area: Full screen (camera view)
            # Menggunakan posisi player sebagai pusat, tapi area sebesar layar
            offset_x = randint(-WINDOW_WIDTH // 2, WINDOW_WIDTH // 2)
            offset_y = randint(-WINDOW_HEIGHT // 2, WINDOW_HEIGHT // 2)
            spawn_pos = (self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y)
            
            KeyboardProjectile(spawn_pos, self.__groups, self.__damage)
