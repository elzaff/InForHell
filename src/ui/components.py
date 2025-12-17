"""
UI Components Module
Komponen UI seperti Button, HealthBar, ExperienceBar, TextLabel, dan UpgradeCardUI.
"""
import pygame
import random
from settings import WHITE, BLACK, RED, GREEN, YELLOW, BLUE, DARK_GRAY


class UIElement:
    """Base class untuk semua elemen UI."""
    
    def __init__(self, pos: tuple, size: tuple):
        self.__pos = pos
        self.__size = size
        self.__visible = True
    
    @property
    def pos(self) -> tuple:
        return self.__pos
    
    @property
    def size(self) -> tuple:
        return self.__size
    
    @property
    def visible(self) -> bool:
        return self.__visible
    
    def set_visible(self, visible: bool) -> None:
        self.__visible = visible
    
    def draw(self, surface: pygame.Surface) -> None:
        if self.__visible:
            self._render(surface)
    
    def _render(self, surface: pygame.Surface) -> None:
        """Method yang di-override oleh subclass."""
        pass


class HealthBar(UIElement):
    """Health bar dengan overlay image."""
    
    _overlay_cache = None
    
    def __init__(self, pos: tuple, size: tuple, max_health: int):
        super().__init__(pos, size)
        self.__max_health = max_health
        self.__current_health = max_health
        
        # Load overlay image (cached) dan scale 2x
        if HealthBar._overlay_cache is None:
            try:
                from os.path import join
                img = pygame.image.load(join('images', 'ui', 'healthoverlay.png')).convert_alpha()
                orig_w, orig_h = img.get_size()
                HealthBar._overlay_cache = pygame.transform.scale(img, (orig_w * 2, orig_h * 2))
            except:
                HealthBar._overlay_cache = None
        
        self.__overlay = HealthBar._overlay_cache
        
        # Area bar fill dalam overlay (scaled 2x)
        self.__bar_offset_x = 16
        self.__bar_width = 224
        self.__bar_height = 18
        self.__bar_offset_y = 0
    
    def update_health(self, current_health: int) -> None:
        self.__current_health = max(0, min(current_health, self.__max_health))
    
    def update_max_health(self, max_health: int) -> None:
        """Update max health untuk level up."""
        self.__max_health = max_health
    
    def _render(self, surface: pygame.Surface) -> None:
        x, y = self.pos
        
        if self.__overlay:
            # Posisi bar fill
            overlay_height = self.__overlay.get_height()
            bar_y = y + (overlay_height - self.__bar_height) // 2
            
            # Health percentage
            health_percentage = self.__current_health / self.__max_health if self.__max_health > 0 else 0
            fill_width = int(self.__bar_width * health_percentage)
            
            if fill_width > 0:
                # Warna berdasarkan health
                if health_percentage > 0.5:
                    color = GREEN
                elif health_percentage > 0.25:
                    color = YELLOW
                else:
                    color = RED
                
                fill_rect = pygame.Rect(x + self.__bar_offset_x, bar_y, fill_width, self.__bar_height)
                pygame.draw.rect(surface, color, fill_rect)
            
            # Draw overlay
            surface.blit(self.__overlay, (x, y))
            
            # Text di dalam bar
            font = pygame.font.Font(None, 20)
            text = f"{self.__current_health}/{self.__max_health}"
            text_surf = font.render(text, True, WHITE)
            text_rect = text_surf.get_rect(center=(x + self.__bar_offset_x + self.__bar_width // 2, 
                                                    y + overlay_height // 2))
            surface.blit(text_surf, text_rect)
        else:
            # Fallback tanpa overlay
            width, height = self.size
            pygame.draw.rect(surface, DARK_GRAY, pygame.Rect(x, y, width, height))
            health_percentage = self.__current_health / self.__max_health if self.__max_health > 0 else 0
            health_width = int(width * health_percentage)
            if health_width > 0:
                color = GREEN if health_percentage > 0.5 else YELLOW if health_percentage > 0.25 else RED
                pygame.draw.rect(surface, color, pygame.Rect(x, y, health_width, height))


class ExperienceBar(UIElement):
    """Experience bar dengan overlay image."""
    
    _overlay_cache = None
    
    def __init__(self, pos: tuple, size: tuple):
        super().__init__(pos, size)
        self.__current_exp = 0
        self.__exp_to_next = 100
        
        # Load overlay image (cached) dan scale 2x
        if ExperienceBar._overlay_cache is None:
            try:
                from os.path import join
                img = pygame.image.load(join('images', 'ui', 'expoverlay.png')).convert_alpha()
                orig_w, orig_h = img.get_size()
                ExperienceBar._overlay_cache = pygame.transform.scale(img, (orig_w * 2, orig_h * 2))
            except:
                ExperienceBar._overlay_cache = None
        
        self.__overlay = ExperienceBar._overlay_cache
        
        # Area bar fill dalam overlay (scaled 2x)
        self.__bar_offset_x = 16
        self.__bar_width = 224
        self.__bar_height = 18
    
    def update_exp(self, current_exp: int, exp_to_next: int) -> None:
        self.__current_exp = current_exp
        self.__exp_to_next = exp_to_next
    
    def _render(self, surface: pygame.Surface) -> None:
        x, y = self.pos
        
        if self.__overlay:
            overlay_height = self.__overlay.get_height()
            bar_y = y + (overlay_height - self.__bar_height) // 2
            
            # EXP percentage
            exp_percentage = self.__current_exp / self.__exp_to_next if self.__exp_to_next > 0 else 0
            fill_width = int(self.__bar_width * exp_percentage)
            
            if fill_width > 0:
                fill_rect = pygame.Rect(x + self.__bar_offset_x, bar_y, fill_width, self.__bar_height)
                pygame.draw.rect(surface, BLUE, fill_rect)
            
            # Draw overlay
            surface.blit(self.__overlay, (x, y))
            
            # Text di dalam bar
            font = pygame.font.Font(None, 20)
            text = f"{self.__current_exp}/{self.__exp_to_next}"
            text_surf = font.render(text, True, WHITE)
            text_rect = text_surf.get_rect(center=(x + self.__bar_offset_x + self.__bar_width // 2, 
                                                    y + overlay_height // 2))
            surface.blit(text_surf, text_rect)
        else:
            # Fallback tanpa overlay
            width, height = self.size
            pygame.draw.rect(surface, DARK_GRAY, pygame.Rect(x, y, width, height))
            exp_percentage = self.__current_exp / self.__exp_to_next if self.__exp_to_next > 0 else 0
            exp_width = int(width * exp_percentage)
            if exp_width > 0:
                pygame.draw.rect(surface, BLUE, pygame.Rect(x, y, exp_width, height))


class TextLabel(UIElement):
    """Label untuk menampilkan teks."""
    
    def __init__(self, pos: tuple, text: str, font_size: int = 24, color: tuple = WHITE):
        super().__init__(pos, (0, 0))
        self.__text = text
        self.__font_size = font_size
        self.__color = color
        self.__font = pygame.font.Font(None, font_size)
    
    def set_text(self, text: str) -> None:
        self.__text = text
    
    def set_color(self, color: tuple) -> None:
        self.__color = color
    
    def _render(self, surface: pygame.Surface) -> None:
        text_surf = self.__font.render(self.__text, True, self.__color)
        surface.blit(text_surf, self.pos)


class Button:
    """Button dengan image asset dan hover outline."""
    
    _button_image_cache = None
    
    def __init__(self, text, pos, width, height, font):
        # Load image (cached)
        if Button._button_image_cache is None:
            try:
                Button._button_image_cache = pygame.image.load('images/ui/button.png').convert_alpha()
            except:
                Button._button_image_cache = None
        
        # Scale dengan aspect ratio
        if Button._button_image_cache:
            orig_w, orig_h = Button._button_image_cache.get_size()
            aspect_ratio = orig_h / orig_w
            new_height = int(width * aspect_ratio)
            self.image = pygame.transform.scale(Button._button_image_cache, (width, new_height))
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill((60, 40, 40))
        
        self.rect = self.image.get_rect(center=pos)
        self.text = text
        self.font = pygame.font.Font(None, 36)
        
        self.is_hovered = False
        self.text_color = (255, 229, 180)
        self.shadow_color = (0, 0, 0)
        self.outline_color = (255, 255, 255)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        # Outline saat hover
        if self.is_hovered:
            pygame.draw.rect(surface, self.outline_color, self.rect, 3)
        
        # Text dengan shadow
        shadow_surf = self.font.render(self.text, False, self.shadow_color)
        shadow_rect = shadow_surf.get_frect(center=(self.rect.centerx + 2, self.rect.centery + 2))
        surface.blit(shadow_surf, shadow_rect)
        
        text_surf = self.font.render(self.text, False, self.text_color)
        text_rect = text_surf.get_frect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False


class UpgradeCardUI:
    """UI Kartu Upgrade dengan efek visual."""
    
    def __init__(self, card_data, pos: tuple, size: tuple):
        self.card = card_data
        self.base_rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.rect = self.base_rect.copy()
        self.is_hovered = False
        
        # Warna tema
        self.dark_red = (80, 10, 10)
        self.hell_black = (20, 5, 5)
        self.fire_orange = (255, 100, 20)
        self.blood_red = (200, 20, 20)
        self.neon_yellow = (255, 255, 100)
        self.matrix_green = (100, 255, 100)
        self.glitch_white = (255, 240, 220)
        
        # Fonts
        self.font_title = pygame.font.Font(None, 36)
        self.font_desc = pygame.font.Font(None, 24)
        self.font_label = pygame.font.Font(None, 28)
        
        # Animasi
        self.shake_offset = 0
        self.shake_timer = 0
        self.glow_intensity = 0
        self.noise_offset = 0
        
        # Noise pattern
        random.seed(hash(self.card.name))
        self.noise_pattern = []
        for _ in range(30):
            x = random.randint(0, size[0])
            y = random.randint(0, size[1])
            size_noise = random.randint(1, 3)
            self.noise_pattern.append((x, y, size_noise))
    
    def check_hover(self, mouse_pos: tuple) -> bool:
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def is_clicked(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False
    
    def update(self):
        if self.is_hovered:
            self.shake_timer += 1
            if self.shake_timer % 3 == 0:
                self.shake_offset = random.choice([-3, -2, -1, 0, 1, 2, 3])
            self.glow_intensity = min(255, self.glow_intensity + 15)
        else:
            self.shake_offset = 0
            self.shake_timer = 0
            self.glow_intensity = max(0, self.glow_intensity - 20)
        
        self.rect.x = self.base_rect.x + self.shake_offset
        self.rect.y = self.base_rect.y
        self.noise_offset += 1
    
    def draw(self, surface: pygame.Surface):
        # Background
        pygame.draw.rect(surface, self.dark_red, self.rect)
        
        # Digital noise
        for i, (x, y, sz) in enumerate(self.noise_pattern):
            animated_offset = (self.noise_offset + i * 10) % 255
            noise_val = (animated_offset % 40)
            noise_color = (80 + noise_val, 10 + noise_val // 4, 10 + noise_val // 4)
            pygame.draw.rect(surface, noise_color, (self.rect.left + x, self.rect.top + y, sz, sz))
        
        # Border
        border_color = self.fire_orange if self.is_hovered else self.blood_red
        pygame.draw.rect(surface, border_color, self.rect, 5)
        inner_rect = self.rect.inflate(-10, -10)
        pygame.draw.rect(surface, self.hell_black, inner_rect, 2)
        
        # Icon
        icon_size = 70
        icon_x = self.rect.left + 20
        icon_y = self.rect.centery - icon_size // 2
        icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
        pygame.draw.rect(surface, self.hell_black, icon_rect)
        inner_icon = icon_rect.inflate(-8, -8)
        pygame.draw.rect(surface, self.card.icon_color, inner_icon)
        pygame.draw.rect(surface, border_color, icon_rect, 3)
        
        # Label
        label_text = self.card.get_label()
        label_color = self.neon_yellow if self.card.is_new else self.matrix_green
        label_surf = self.font_label.render(label_text, False, label_color)
        label_rect = label_surf.get_frect(topright=(self.rect.right - 15, self.rect.top + 15))
        stamp_bg = label_rect.inflate(12, 8)
        pygame.draw.rect(surface, self.hell_black, stamp_bg)
        pygame.draw.rect(surface, label_color, stamp_bg, 2)
        surface.blit(label_surf, label_rect)
        
        # Title
        title_x = self.rect.left + 105
        title_y = self.rect.top + 30
        shadow_title = self.font_title.render(self.card.name, False, (0, 0, 0))
        surface.blit(shadow_title, (title_x + 2, title_y + 2))
        title_surf = self.font_title.render(self.card.name, False, self.glitch_white)
        surface.blit(title_surf, (title_x, title_y))
        
        # Description dengan word wrap
        desc_x = self.rect.left + 105
        desc_y = self.rect.top + 65
        words = self.card.description.split(' ')
        lines = []
        current_line = []
        max_width = self.rect.width - 115
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = self.font_desc.render(test_line, False, (255, 255, 255))
            if test_surf.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines[:3]):
            shadow_desc = self.font_desc.render(line, False, (0, 0, 0))
            surface.blit(shadow_desc, (desc_x + 1, desc_y + i * 25 + 1))
            desc_surf = self.font_desc.render(line, False, (200, 180, 160))
            surface.blit(desc_surf, (desc_x, desc_y + i * 25))
