"""
Skills Module
Implementasi skill aktif seperti Keyboard Rain.
"""
import pygame
from random import randint, choice
from os.path import join
from os import listdir
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


# Cache untuk keyboard images
_keyboard_images_cache = None

def _load_keyboard_images():
    """Load dan cache semua keyboard images dari folder."""
    global _keyboard_images_cache
    if _keyboard_images_cache is not None:
        return _keyboard_images_cache
    
    _keyboard_images_cache = []
    keyboard_folder = join('images', 'keyboard')
    try:
        for filename in listdir(keyboard_folder):
            if filename.endswith('.png'):
                img = pygame.image.load(join(keyboard_folder, filename)).convert_alpha()
                # Scale 5x untuk visibility
                orig_w, orig_h = img.get_size()
                img = pygame.transform.scale(img, (orig_w * 5, orig_h * 5))
                _keyboard_images_cache.append(img)
    except:
        # Fallback jika folder tidak ada
        fallback = pygame.Surface((60, 60))
        fallback.fill((200, 200, 200))
        _keyboard_images_cache = [fallback]
    
    return _keyboard_images_cache


class ProjectileShadow(pygame.sprite.Sprite):
    """Bayangan untuk proyektil jatuh."""
    def __init__(self, pos: tuple[int, int], size: tuple[int, int], groups):
        super().__init__(groups)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (0, 0, 0, 100), (0, 0, size[0], size[1]))
        self.rect = self.image.get_frect(center=pos)


class KeyboardProjectile(pygame.sprite.Sprite):
    """Proyektil keyboard yang jatuh dari atas."""
    def __init__(self, target_pos: tuple[int, int], groups, damage: int = 100):
        super().__init__(groups)
        
        # Load random keyboard image
        keyboard_images = _load_keyboard_images()
        self.image = choice(keyboard_images)
        
        img_w, img_h = self.image.get_size()
        
        self.__target_pos = pygame.Vector2(target_pos)
        self.rect = self.image.get_frect(center=target_pos)
        
        # Simulasi jatuh dari atas
        self.__height = 1000.0 
        self.__fall_speed = 1000.0 
        self.rect.centery = self.__target_pos.y - self.__height
        
        # Shadow
        self.__shadow = ProjectileShadow(target_pos, (img_w, img_h // 2), groups)
        self.__damage = damage
        self.__has_landed = False
        self.__impact_time = 0
        self.__linger_duration = 200 
    
    @property
    def damage(self) -> int:
        return self.__damage
        
    def update(self, dt: float) -> None:
        if not self.__has_landed:
            self.__height -= self.__fall_speed * dt
            self.rect.centery = self.__target_pos.y - self.__height
            
            if self.__height <= 0:
                self.__height = 0
                self.rect.centery = self.__target_pos.y
                self.__has_landed = True
                self.__impact_time = pygame.time.get_ticks()
                self.__shadow.kill()
        else:
            if pygame.time.get_ticks() - self.__impact_time >= self.__linger_duration:
                self.kill()
    
    def kill(self):
        if self.__shadow.alive():
            self.__shadow.kill()
        super().kill()


class KeyboardRain:
    """Skill Keyboard Rain - hujan keyboard dari langit."""
    
    def __init__(self, groups):
        self.__groups = groups
        self.__spawn_timer = 0
        self.__spawn_interval = 100 
        self.player = None
        
        self.__name = "Keyboard Rain"
        self.__base_cooldown = 20000  # 20 detik
        self.__damage = 100
        self.__timer = 10000  # Ready di awal
        self.__cooldown_modifier = 1.0
        
        self.__is_active = False
        self.__active_timer = 0
        self.__duration = 3000  # 3 detik aktif
        
    @property
    def name(self): 
        return self.__name
    
    @property
    def cooldown(self):
        return self.__base_cooldown * self.__cooldown_modifier
    
    @property
    def damage(self): 
        return self.__damage
    
    @property
    def cooldown_progress(self) -> float:
        """Progress cooldown dari 0.0 sampai 1.0."""
        actual_cooldown = self.cooldown
        if actual_cooldown == 0: 
            return 1.0
        return min(1.0, self.__timer / actual_cooldown)
    
    @property
    def is_active(self): 
        return self.__is_active
    
    def can_attack(self) -> bool:
        """Cek apakah skill sudah ready."""
        return self.__timer >= self.cooldown

    @property
    def is_ready(self) -> bool:
        """Alias untuk can_attack()."""
        return self.can_attack()
    
    def set_cooldown_modifier(self, modifier: float):
        """Set modifier cooldown dari upgrade."""
        self.__cooldown_modifier = modifier
    
    def set_player(self, player):
        """Set referensi ke player."""
        self.player = player
    
    def activate(self):
        """Aktivasi skill jika ready."""
        if self.can_attack():
            self.__is_active = True
            self.__active_timer = pygame.time.get_ticks()
            self.__timer = 0
            return True
        return False
    
    def update_active(self, current_time):
        """Update status aktif skill."""
        if self.__is_active:
            if current_time - self.__active_timer >= self.__duration:
                self.__is_active = False
        
    def update(self, dt):
        """Update skill setiap frame."""
        self.__timer += dt * 1000 
        current_time = pygame.time.get_ticks()
        self.update_active(current_time)
        
        # Spawn keyboard saat aktif
        if self.__is_active:
            if current_time - self.__spawn_timer >= self.__spawn_interval:
                self.attack()
                self.__spawn_timer = current_time
                
    def attack(self):
        """Spawn keyboard projectile di sekitar player."""
        if self.player:
            offset_x = randint(-WINDOW_WIDTH // 2, WINDOW_WIDTH // 2)
            offset_y = randint(-WINDOW_HEIGHT // 2, WINDOW_HEIGHT // 2)
            spawn_pos = (self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y)
            KeyboardProjectile(spawn_pos, self.__groups, self.__damage)