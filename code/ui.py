"""
Module untuk Sistem UI dengan encapsulation.
"""
from settings import *
import pygame
from typing import Tuple, Any

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
    def __init__(self, text, pos, width, height, font):
        # Hitbox utama
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = pos
        self.text = text
        # Gunakan font pixel art style
        self.font = pygame.font.Font(None, 36)  # None = default pixel font pygame
        
        # --- MOLTEN ROCK & LAVA THEME PALETTE ---
        self.stone_surface_dark = (62, 40, 40)      # #3E2828 - Batu gelap/hangus
        self.stone_highlight = (80, 55, 50)         # Highlight batu
        self.lava_glow_highlight = (255, 140, 0)    # #FF8C00 - Oranye terang retakan lahar
        self.lava_bright = (255, 200, 80)           # Lava sangat terang
        self.magma_crust_outline = (26, 15, 15)     # #1A0F0F - Outline kerak magma
        self.text_hot_glow = (255, 229, 180)        # #FFE5B4 - Teks kuning pucat panas
        self.heat_shadow = (102, 34, 0)             # #662200 - Bayangan merah tua panas
        
        self.is_hovered = False
        
        # Pixel art shadow - lebih blocky dengan warna lava
        self.shadow_rect = self.rect.copy()
        self.shadow_rect.y += 4
        self.shadow_rect.x += 4
        self.lava_shadow = (180, 80, 0)  # Oranye seperti lava untuk shadow

    def _draw_pixel_cracks(self, surface, base_x, base_y, color, scale=1):
        """Gambar pola retakan lava pixel art"""
        # Pattern retakan dalam bentuk pixel art (zigzag dan cabang)
        pixels = [
            # Main crack horizontal
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0),
            # Branch 1 (ke atas)
            (2, -1), (2, -2),
            # Branch 2 (ke bawah)
            (5, 1), (5, 2), (6, 2),
            # Branch 3 (ke atas)
            (7, -1),
            # Small cracks
            (3, 1), (8, -1)
        ]
        
        for px, py in pixels:
            x = base_x + (px * scale * 3)
            y = base_y + (py * scale * 3)
            pygame.draw.rect(surface, color, (x, y, scale * 3, scale * 3))

    def draw(self, surface):
        # 1. Pixel art shadow (blocky, tidak rounded) - warna oranye lava
        pygame.draw.rect(surface, self.lava_shadow, self.shadow_rect)
        
        # 2. Base stone surface dengan pixel art texture
        pygame.draw.rect(surface, self.stone_surface_dark, self.rect)
        
        # Tambah texture stone pixel art (dots/noise)
        import random
        random.seed(hash(self.text))  # Konsisten untuk setiap button
        for _ in range(15):
            x = self.rect.left + random.randint(5, self.rect.width - 5)
            y = self.rect.top + random.randint(5, self.rect.height - 5)
            pygame.draw.rect(surface, self.stone_highlight, (x, y, 2, 2))
        
        # 3. Lava crack pattern - MENYEBAR KE SELURUH BUTTON
        if self.is_hovered:
            crack_color = self.lava_bright
            crack_glow = self.lava_glow_highlight
        else:
            crack_color = self.lava_glow_highlight
            crack_glow = self.heat_shadow
        
        # Retakan horizontal yang menyebar dari kiri ke kanan
        num_horizontal = 4
        for i in range(num_horizontal):
            y_pos = self.rect.top + 10 + (i * (self.rect.height - 20) // (num_horizontal - 1))
            # Main horizontal crack
            for x_offset in range(0, self.rect.width - 20, 3):
                x_pos = self.rect.left + 10 + x_offset
                # Variasi ketebalan retakan
                thickness = 2 if (x_offset // 3) % 3 == 0 else 3
                pygame.draw.rect(surface, crack_color, (x_pos, y_pos, thickness, 2))
        
        # Retakan vertikal yang menyambung
        num_vertical = 6
        for i in range(num_vertical):
            x_pos = self.rect.left + 15 + (i * (self.rect.width - 30) // (num_vertical - 1))
            # Main vertical crack dengan variasi
            for y_offset in range(0, self.rect.height - 25, 4):
                y_pos = self.rect.top + 10 + y_offset
                # Skip beberapa pixel untuk efek putus-putus
                if (y_offset // 4) % 3 != 2:
                    pygame.draw.rect(surface, crack_color, (x_pos, y_pos, 2, 3))
        
        # Retakan diagonal untuk variasi
        # Diagonal kiri atas ke kanan bawah
        for i in range(0, min(self.rect.width, self.rect.height) - 20, 5):
            x_pos = self.rect.left + 10 + i
            y_pos = self.rect.top + 5 + (i * self.rect.height // self.rect.width)
            if i % 10 < 7:  # Putus-putus
                pygame.draw.rect(surface, crack_color, (x_pos, y_pos, 2, 2))
        
        # Diagonal kanan atas ke kiri bawah
        for i in range(0, min(self.rect.width, self.rect.height) - 20, 5):
            x_pos = self.rect.right - 10 - i
            y_pos = self.rect.top + 5 + (i * self.rect.height // self.rect.width)
            if i % 10 < 7:  # Putus-putus
                pygame.draw.rect(surface, crack_color, (x_pos, y_pos, 2, 2))
        
        # Retakan cabang kecil-kecil (detail)
        random.seed(hash(self.text) + 1)
        for _ in range(25):
            x = self.rect.left + random.randint(10, self.rect.width - 10)
            y = self.rect.top + random.randint(10, self.rect.height - 10)
            # Mini retakan 3-5 pixel
            length = random.randint(2, 4)
            direction = random.choice(['h', 'v'])
            if direction == 'h':
                for dx in range(length):
                    pygame.draw.rect(surface, crack_color, (x + dx * 2, y, 2, 2))
            else:
                for dy in range(length):
                    pygame.draw.rect(surface, crack_color, (x, y + dy * 2, 2, 2))
        
        # Glow effect di sekitar retakan saat hover
        if self.is_hovered:
            # Glow di sepanjang tepi button
            glow_positions = [
                (self.rect.left + 5, self.rect.top + 5),
                (self.rect.centerx, self.rect.top + 5),
                (self.rect.right - 5, self.rect.top + 5),
                (self.rect.left + 5, self.rect.centery),
                (self.rect.right - 5, self.rect.centery),
                (self.rect.left + 5, self.rect.bottom - 5),
                (self.rect.centerx, self.rect.bottom - 5),
                (self.rect.right - 5, self.rect.bottom - 5),
            ]
            for gx, gy in glow_positions:
                pygame.draw.rect(surface, crack_glow, (gx, gy, 3, 3))
        
        # 4. Pixel art border (thick, blocky)
        # Outer border (very dark)
        pygame.draw.rect(surface, self.magma_crust_outline, self.rect, 4)
        
        # Inner border highlight (lava glow saat hover)
        if self.is_hovered:
            inner_rect = self.rect.inflate(-8, -8)
            pygame.draw.rect(surface, self.lava_glow_highlight, inner_rect, 2)
        
        # 5. Text dengan shadow berlayer untuk keterbacaan maksimal
        # Shadow layer 1 (paling gelap, paling jauh)
        shadow_surf1 = self.font.render(self.text, False, (0, 0, 0))
        shadow_rect1 = shadow_surf1.get_frect(center=(self.rect.centerx + 3, self.rect.centery + 3))
        surface.blit(shadow_surf1, shadow_rect1)
        
        # Shadow layer 2 (medium dark)
        shadow_surf2 = self.font.render(self.text, False, self.magma_crust_outline)
        shadow_rect2 = shadow_surf2.get_frect(center=(self.rect.centerx + 2, self.rect.centery + 2))
        surface.blit(shadow_surf2, shadow_rect2)
        
        # Shadow layer 3 (heat shadow - oranye gelap)
        shadow_surf3 = self.font.render(self.text, False, self.heat_shadow)
        shadow_rect3 = shadow_surf3.get_frect(center=(self.rect.centerx + 1, self.rect.centery + 1))
        surface.blit(shadow_surf3, shadow_rect3)
        
        # Main text (hot glow - sangat terang)
        text_surf = self.font.render(self.text, False, self.text_hot_glow)
        text_rect = text_surf.get_frect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

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


class MainMenu:
    """Main Menu dengan tema neraka yang lebih keren"""
    def __init__(self, display_surface):
        self.display_surface = display_surface

        # Load Font - Pixel Art Style
        try:
            # Coba load font pixel art jika ada
            self.font_button = pygame.font.Font(None, 40)  # Default pygame font lebih pixel-like
            self.font_subtitle = pygame.font.Font(None, 24)
        except:
            self.font_button = pygame.font.SysFont(None, 40)
            self.font_subtitle = pygame.font.SysFont(None, 24)
        
        # Load Logo InForHell (Static, tanpa teks judul)
        self.logo = None
        try:
            logo_path = join('images', 'ui', 'inforhell.png')
            self.logo = pygame.image.load(logo_path).convert_alpha()
            # Resize logo lebih besar
            logo_size = 450  # ukuran logo diperbesar
            self.logo = pygame.transform.scale(self.logo, (logo_size, logo_size))
            print("Logo InForHell berhasil dimuat!")
        except Exception as e:
            print(f"Logo tidak ditemukan: {e}")
            self.logo = None

        # Posisi Tombol (Tengah Layar, lebih ke bawah untuk kasih ruang logo)
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80
        
        self.btn_start = Button("START GAME", (cx, cy), 300, 60, self.font_button)
        self.btn_leaderboard = Button("LEADERBOARD", (cx, cy + 80), 300, 60, self.font_button)
        self.btn_exit = Button("EXIT", (cx, cy + 160), 300, 60, self.font_button)
        
        self.show_leaderboard = False

    def draw(self):
        # 1. BACKGROUND - Hitam kemerahan solid (siap diganti dengan video/animated bg)
        self.display_surface.fill((15, 5, 5))  # Hitam dengan sedikit merah
        
        if not self.show_leaderboard:
            # 2. LOGO INFORHELL - Static, sebagai judul utama
            if self.logo:
                logo_x = WINDOW_WIDTH // 2 - self.logo.get_width() // 2
                logo_y = 50  # posisi di bagian atas
                self.display_surface.blit(self.logo, (logo_x, logo_y))

            # 3. TOMBOL-TOMBOL
            self.btn_start.draw(self.display_surface)
            self.btn_leaderboard.draw(self.display_surface)
            self.btn_exit.draw(self.display_surface)
        
        else:
            # Tampilan Leaderboard dengan tema neraka
            try:
                title_font = pygame.font.Font(join('data', 'fonts', 'Oxanium-Bold.ttf'), 80)
            except:
                title_font = pygame.font.SysFont(None, 80)
            
            title_surf = title_font.render("LEADERBOARD", True, (255, 150, 0))
            title_rect = title_surf.get_frect(center=(WINDOW_WIDTH // 2, 100))
            self.display_surface.blit(title_surf, title_rect)
            
            scores = ["1. PLAYER - 9999", "2. ??? - 0000"]
            for i, score in enumerate(scores):
                score_surf = self.font_button.render(score, True, (255, 220, 180))
                score_rect = score_surf.get_frect(center=(WINDOW_WIDTH // 2, 250 + i * 60))
                self.display_surface.blit(score_surf, score_rect)
                
            back_surf = self.font_button.render("[ ESC to Back ]", True, (150, 100, 80))
            back_rect = back_surf.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
            self.display_surface.blit(back_surf, back_rect)

    def update(self, event_list):
        # Handle input
        mouse_pos = pygame.mouse.get_pos()
        
        if not self.show_leaderboard:
            self.btn_start.check_hover(mouse_pos)
            self.btn_leaderboard.check_hover(mouse_pos)
            self.btn_exit.check_hover(mouse_pos)
            
            for event in event_list:
                if self.btn_start.is_clicked(event): return "start"
                if self.btn_leaderboard.is_clicked(event): self.show_leaderboard = True
                if self.btn_exit.is_clicked(event): return "exit"
        else:
            for event in event_list:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_leaderboard = False
        return None

class GameUI:
    """Manager UI Utama yang mengkoordinasi semua elemen UI"""
    
    def __init__(self, display_surface: pygame.Surface):
        self.__display_surface = display_surface
        self.__ui_elements = []
        
        # Buat komponen UI
        self.__setup_ui()
    
    def __setup_ui(self) -> None:
        """Setup semua elemen UI dengan encapsulation"""
        # Health bar
        self.__health_bar = HealthBar((20, 20), (300, 30), PLAYER_MAX_HEALTH)
        self.__ui_elements.append(self.__health_bar)
        
        # Health label
        self.__health_label = TextLabel((20, 5), "HP", 20, WHITE)
        self.__ui_elements.append(self.__health_label)
        
        # Experience bar
        self.__exp_bar = ExperienceBar((20, 60), (300, 20))
        self.__ui_elements.append(self.__exp_bar)
        
        # EXP label
        self.__exp_label = TextLabel((20, 45), "EXP", 20, WHITE)
        self.__ui_elements.append(self.__exp_label)
        
        # Level display
        self.__level_label = TextLabel((WINDOW_WIDTH - 150, 20), "Level: 1", 32, YELLOW)
        self.__ui_elements.append(self.__level_label)
        
        # Kill counter
        self.__kill_label = TextLabel((WINDOW_WIDTH - 150, 60), "Kills: 0", 28, WHITE)
        self.__ui_elements.append(self.__kill_label)
        
        # Time survived
        self.__time_label = TextLabel((WINDOW_WIDTH - 150, 95), "Time: 0:00", 28, WHITE)
        self.__ui_elements.append(self.__time_label)
        
        # Score
        self.__score_label = TextLabel((WINDOW_WIDTH - 150, 130), "Score: 0", 28, GREEN)
        self.__ui_elements.append(self.__score_label)
    
    def update_player_stats(self, player_stats: Any) -> None:
        """Update UI berdasarkan statistik player"""
        # Update health
        self.__health_bar.update_health(player_stats.current_health)
        self.__health_label.set_text(f"HP: {player_stats.current_health}/{player_stats.max_health}")
        
        # Update exp
        self.__exp_bar.update_exp(player_stats.current_exp, player_stats.exp_to_next_level)
        self.__exp_label.set_text(f"EXP: {player_stats.current_exp}/{player_stats.exp_to_next_level}")
        
        # Update level
        self.__level_label.set_text(f"Level: {player_stats.level}")
        
        # Update kills
        self.__kill_label.set_text(f"Kills: {player_stats.kills}")
    
    def update_time(self, seconds: float) -> None:
        """Update tampilan waktu"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        self.__time_label.set_text(f"Time: {minutes}:{secs:02d}")
    
    def update_score(self, score: int) -> None:
        """Update tampilan skor"""
        self.__score_label.set_text(f"Score: {score}")
        
    def draw_skill_icon(self, skill: Any) -> None:
        """Gambar icon skill dengan cooldown overlay"""
        if not skill: return
        
        # Posisi Icon (Bottom Left, di bawah EXP bar)
        x, y = 20, 90
        size = 50
        rect = pygame.Rect(x, y, size, size)
        
        # Background
        pygame.draw.rect(self.__display_surface, DARK_GRAY, rect)
        
        # Cooldown Overlay
        progress = skill.cooldown_progress
        if progress < 1.0:
            # Calculate height of overlay (inverse of progress)
            overlay_height = int(size * (1 - progress))
            overlay_rect = pygame.Rect(x, y + size - overlay_height, size, overlay_height)
            
            # Semi-transparent overlay
            s = pygame.Surface((size, overlay_height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            self.__display_surface.blit(s, (x, y + size - overlay_height))
            
            # Timer Text
            remaining_time = (skill.cooldown * (1 - progress)) / 1000
            timer_font = pygame.font.Font(None, 30)
            timer_text = timer_font.render(f"{remaining_time:.1f}", True, WHITE)
            timer_rect = timer_text.get_rect(center=rect.center)
            self.__display_surface.blit(timer_text, timer_rect)
        else:
            # Glow Effect (Ready)
            # Simple pulsing effect based on time
            pulse = (pygame.time.get_ticks() // 200) % 2
            color = YELLOW if pulse else (255, 215, 0) # Gold
            pygame.draw.rect(self.__display_surface, color, rect, 3) # Border tebal
            
            # Ready Text
            font = pygame.font.Font(None, 20)
            text = font.render("Ready", True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.__display_surface.blit(text, text_rect)
    
    def draw(self) -> None:
        """Gambar semua elemen UI"""
        for element in self.__ui_elements:
            element.draw(self.__display_surface)


class GameOverScreen:
    """Layar Game Over dengan statistik akhir"""
    
    def __init__(self, display_surface: pygame.Surface):
        self.__display_surface = display_surface
        self.__font_large = pygame.font.Font(None, 72)
        self.__font_medium = pygame.font.Font(None, 48)
        self.__font_small = pygame.font.Font(None, 32)
    
    def draw(self, final_stats: dict) -> None:
        """Gambar layar game over dengan statistik"""
        # Overlay semi-transparan
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.__display_surface.blit(overlay, (0, 0))
        
        # Teks Game Over
        game_over_text = self.__font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.__display_surface.blit(game_over_text, game_over_rect)
        
        # Statistik Akhir
        y_offset = 250
        stats_to_show = [
            f"Final Score: {final_stats['score']}",
            f"Level Reached: {final_stats['level']}",
            f"Enemies Killed: {final_stats['kills']}",
            f"Time Survived: {final_stats['time']}",
        ]
        
        for stat_text in stats_to_show:
            stat_surf = self.__font_medium.render(stat_text, True, WHITE)
            stat_rect = stat_surf.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.__display_surface.blit(stat_surf, stat_rect)
            y_offset += 60
        
        # Instruksi Restart
        restart_text = self.__font_small.render("Press R to Restart or ESC to Quit", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
        self.__display_surface.blit(restart_text, restart_rect)


class LevelUpNotification:
    """Notifikasi yang muncul saat level up"""
    
    def __init__(self):
        self.__active = False
        self.__start_time = 0
        self.__duration = 2000  # 2 detik
        self.__font = pygame.font.Font(None, 64)
    
    def trigger(self, level: int) -> None:
        """Memicu notifikasi"""
        self.__active = True
        self.__level = level
        self.__start_time = pygame.time.get_ticks()
    
    def update(self) -> None:
        """Update status notifikasi"""
        if self.__active:
            if pygame.time.get_ticks() - self.__start_time >= self.__duration:
                self.__active = False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Gambar notifikasi"""
        if self.__active:
            # Efek pudar (fade)
            elapsed = pygame.time.get_ticks() - self.__start_time
            alpha = 255
            if elapsed > self.__duration - 500:
                alpha = int(255 * (1 - (elapsed - (self.__duration - 500)) / 500))
            
            text = self.__font.render(f"LEVEL UP! Level {self.__level}", True, YELLOW)
            text.set_alpha(alpha)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            surface.blit(text, text_rect)
