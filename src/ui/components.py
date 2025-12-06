"""
UI COMPONENTS MODULE
Button, HealthBar, ExperienceBar, TextLabel, UpgradeCardUI
"""
import pygame
from typing import Tuple, List, Dict, Any
from settings import WHITE, BLACK, RED, GREEN, YELLOW, BLUE, DARK_GRAY


class UIElement:
    """Base class untuk elemen UI dengan encapsulation"""
    
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int]):
        self.__pos = pos
        self.__size = size
        self.__visible = True
    
    @property
    def pos(self) -> Tuple[int, int]:
        return self.__pos
    
    @property
    def size(self) -> Tuple[int, int]:
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
        """Override method ini di subclass"""
        pass


class HealthBar(UIElement):
    """Health bar dengan border dan gradasi warna"""
    
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int], max_health: int):
        super().__init__(pos, size)
        self.__max_health = max_health
        self.__current_health = max_health
        self.__border_width = 2
    
    def update_health(self, current_health: int) -> None:
        self.__current_health = max(0, min(current_health, self.__max_health))
    
    def _render(self, surface: pygame.Surface) -> None:
        x, y = self.pos
        width, height = self.size
        
        # Border
        border_rect = pygame.Rect(x - self.__border_width, y - self.__border_width,
                                  width + self.__border_width * 2, 
                                  height + self.__border_width * 2)
        pygame.draw.rect(surface, WHITE, border_rect, self.__border_width)
        
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, DARK_GRAY, bg_rect)
        
        # Health fill
        health_percentage = self.__current_health / self.__max_health
        health_width = int(width * health_percentage)
        
        if health_width > 0:
            health_rect = pygame.Rect(x, y, health_width, height)
            
            # Gradasi warna berdasarkan health
            if health_percentage > 0.5:
                color = GREEN
            elif health_percentage > 0.25:
                color = YELLOW
            else:
                color = RED
            
            pygame.draw.rect(surface, color, health_rect)


class ExperienceBar(UIElement):
    """Experience bar untuk menunjukkan progress ke level berikutnya"""
    
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int]):
        super().__init__(pos, size)
        self.__current_exp = 0
        self.__exp_to_next = 100
        self.__border_width = 2
    
    def update_exp(self, current_exp: int, exp_to_next: int) -> None:
        self.__current_exp = current_exp
        self.__exp_to_next = exp_to_next
    
    def _render(self, surface: pygame.Surface) -> None:
        x, y = self.pos
        width, height = self.size
        
        # Border
        border_rect = pygame.Rect(x - self.__border_width, y - self.__border_width,
                                  width + self.__border_width * 2, 
                                  height + self.__border_width * 2)
        pygame.draw.rect(surface, WHITE, border_rect, self.__border_width)
        
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, DARK_GRAY, bg_rect)
        
        # EXP fill
        exp_percentage = self.__current_exp / self.__exp_to_next
        exp_width = int(width * exp_percentage)
        
        if exp_width > 0:
            exp_rect = pygame.Rect(x, y, exp_width, height)
            pygame.draw.rect(surface, BLUE, exp_rect)


class TextLabel(UIElement):
    """Label untuk menampilkan teks"""
    
    def __init__(self, pos: Tuple[int, int], text: str, font_size: int = 24, color: Tuple[int, int, int] = WHITE):
        super().__init__(pos, (0, 0))
        self.__text = text
        self.__font_size = font_size
        self.__color = color
        self.__font = pygame.font.Font(None, font_size)
    
    def set_text(self, text: str) -> None:
        self.__text = text
    
    def set_color(self, color: Tuple[int, int, int]) -> None:
        self.__color = color
    
    def _render(self, surface: pygame.Surface) -> None:
        text_surf = self.__font.render(self.__text, True, self.__color)
        surface.blit(text_surf, self.pos)


class Button:
    """Button dengan tema Molten Rock & Lava"""
    
    def __init__(self, text, pos, width, height, font):
        # Hitbox utama
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = pos
        self.text = text
        self.font = pygame.font.Font(None, 36)
        
        # --- MOLTEN ROCK & LAVA THEME PALETTE ---
        self.stone_surface_dark = (62, 40, 40)
        self.stone_highlight = (80, 55, 50)
        self.lava_glow_highlight = (255, 140, 0)
        self.lava_bright = (255, 200, 80)
        self.magma_crust_outline = (26, 15, 15)
        self.text_hot_glow = (255, 229, 180)
        self.heat_shadow = (102, 34, 0)
        
        self.is_hovered = False
        
        self.shadow_rect = self.rect.copy()
        self.shadow_rect.y += 4
        self.shadow_rect.x += 4
        self.lava_shadow = (180, 80, 0)

    def draw(self, surface):
        import random
        
        # 1. Shadow
        pygame.draw.rect(surface, self.lava_shadow, self.shadow_rect)
        
        # 2. Base stone surface
        pygame.draw.rect(surface, self.stone_surface_dark, self.rect)
        
        # Stone texture
        random.seed(hash(self.text))
        for _ in range(15):
            x = self.rect.left + random.randint(5, self.rect.width - 5)
            y = self.rect.top + random.randint(5, self.rect.height - 5)
            pygame.draw.rect(surface, self.stone_highlight, (x, y, 2, 2))
        
        # 3. Lava crack pattern
        if self.is_hovered:
            crack_color = self.lava_bright
        else:
            crack_color = self.lava_glow_highlight
        
        # Horizontal cracks
        num_horizontal = 4
        for i in range(num_horizontal):
            y_pos = self.rect.top + 10 + (i * (self.rect.height - 20) // (num_horizontal - 1))
            for x_offset in range(0, self.rect.width - 20, 3):
                x_pos = self.rect.left + 10 + x_offset
                thickness = 2 if (x_offset // 3) % 3 == 0 else 3
                pygame.draw.rect(surface, crack_color, (x_pos, y_pos, thickness, 2))
        
        # Vertical cracks
        num_vertical = 6
        for i in range(num_vertical):
            x_pos = self.rect.left + 15 + (i * (self.rect.width - 30) // (num_vertical - 1))
            for y_offset in range(0, self.rect.height - 25, 4):
                y_pos = self.rect.top + 10 + y_offset
                if (y_offset // 4) % 3 != 2:
                    pygame.draw.rect(surface, crack_color, (x_pos, y_pos, 2, 3))
        
        # 4. Border
        pygame.draw.rect(surface, self.magma_crust_outline, self.rect, 4)
        
        if self.is_hovered:
            inner_rect = self.rect.inflate(-8, -8)
            pygame.draw.rect(surface, self.lava_glow_highlight, inner_rect, 2)
        
        # 5. Text with shadow layers
        shadow_surf1 = self.font.render(self.text, False, (0, 0, 0))
        shadow_rect1 = shadow_surf1.get_frect(center=(self.rect.centerx + 3, self.rect.centery + 3))
        surface.blit(shadow_surf1, shadow_rect1)
        
        shadow_surf2 = self.font.render(self.text, False, self.magma_crust_outline)
        shadow_rect2 = shadow_surf2.get_frect(center=(self.rect.centerx + 2, self.rect.centery + 2))
        surface.blit(shadow_surf2, shadow_rect2)
        
        shadow_surf3 = self.font.render(self.text, False, self.heat_shadow)
        shadow_rect3 = shadow_surf3.get_frect(center=(self.rect.centerx + 1, self.rect.centery + 1))
        surface.blit(shadow_surf3, shadow_rect3)
        
        text_surf = self.font.render(self.text, False, self.text_hot_glow)
        text_rect = text_surf.get_frect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False


class UpgradeCardUI:
    """UI Kartu Upgrade dengan tema 'Cursed Technology'"""
    
    def __init__(self, card_data, pos: tuple, size: tuple):
        self.card = card_data
        self.base_rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.rect = self.base_rect.copy()
        self.is_hovered = False
        
        # Cursed Technology Color Palette
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
        
        # Animation variables
        self.shake_offset = 0
        self.shake_timer = 0
        self.glow_intensity = 0
        self.noise_offset = 0
        
        # Generate noise pattern
        import random
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
        import random
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
        import random
        
        # 1. Background
        pygame.draw.rect(surface, self.dark_red, self.rect)
        
        # Digital noise
        for i, (x, y, sz) in enumerate(self.noise_pattern):
            animated_offset = (self.noise_offset + i * 10) % 255
            noise_val = (animated_offset % 40)
            noise_color = (80 + noise_val, 10 + noise_val // 4, 10 + noise_val // 4)
            pygame.draw.rect(surface, noise_color, (self.rect.left + x, self.rect.top + y, sz, sz))
        
        # 2. Border
        border_color = self.fire_orange if self.is_hovered else self.blood_red
        pygame.draw.rect(surface, border_color, self.rect, 5)
        inner_rect = self.rect.inflate(-10, -10)
        pygame.draw.rect(surface, self.hell_black, inner_rect, 2)
        
        # 3. Icon slot
        icon_size = 70
        icon_x = self.rect.left + 20
        icon_y = self.rect.centery - icon_size // 2
        icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
        pygame.draw.rect(surface, self.hell_black, icon_rect)
        inner_icon = icon_rect.inflate(-8, -8)
        pygame.draw.rect(surface, self.card.icon_color, inner_icon)
        pygame.draw.rect(surface, border_color, icon_rect, 3)
        
        # 4. Label
        label_text = self.card.get_label()
        label_color = self.neon_yellow if self.card.is_new else self.matrix_green
        label_surf = self.font_label.render(label_text, False, label_color)
        label_rect = label_surf.get_frect(topright=(self.rect.right - 15, self.rect.top + 15))
        stamp_bg = label_rect.inflate(12, 8)
        pygame.draw.rect(surface, self.hell_black, stamp_bg)
        pygame.draw.rect(surface, label_color, stamp_bg, 2)
        surface.blit(label_surf, label_rect)
        
        # 5. Title
        title_x = self.rect.left + 105
        title_y = self.rect.top + 30
        shadow_title = self.font_title.render(self.card.name, False, (0, 0, 0))
        surface.blit(shadow_title, (title_x + 2, title_y + 2))
        title_surf = self.font_title.render(self.card.name, False, self.glitch_white)
        surface.blit(title_surf, (title_x, title_y))
        
        # 6. Description
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
