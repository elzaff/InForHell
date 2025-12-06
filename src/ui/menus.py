"""
UI MENUS MODULE
MainMenu, PauseMenu, GameOverScreen, LevelUpNotification, LevelUpSelectionMenu
"""
import pygame
from typing import List, Optional, Any
from os.path import join
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, RED, YELLOW, BLACK
from .components import Button, UpgradeCardUI


class MainMenu:
    """Main Menu dengan tema neraka yang lebih keren"""
    def __init__(self, display_surface):
        self.display_surface = display_surface

        # Load Font
        try:
            self.font_button = pygame.font.Font(None, 40)
            self.font_subtitle = pygame.font.Font(None, 24)
        except:
            self.font_button = pygame.font.SysFont(None, 40)
            self.font_subtitle = pygame.font.SysFont(None, 24)
        
        # Load Logo InForHell
        self.logo = None
        try:
            logo_path = join('images', 'ui', 'inforhell.png')
            self.logo = pygame.image.load(logo_path).convert_alpha()
            logo_size = 450
            self.logo = pygame.transform.scale(self.logo, (logo_size, logo_size))
            print("Logo InForHell berhasil dimuat!")
        except Exception as e:
            print(f"Logo tidak ditemukan: {e}")
            self.logo = None

        # Posisi Tombol
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80
        
        self.btn_start = Button("START GAME", (cx, cy), 300, 60, self.font_button)
        self.btn_leaderboard = Button("LEADERBOARD", (cx, cy + 80), 300, 60, self.font_button)
        self.btn_exit = Button("EXIT", (cx, cy + 160), 300, 60, self.font_button)
        
        self.show_leaderboard = False

    def draw(self):
        # 1. Background
        self.display_surface.fill((15, 5, 5))
        
        if not self.show_leaderboard:
            # 2. Logo
            if self.logo:
                logo_x = WINDOW_WIDTH // 2 - self.logo.get_width() // 2
                logo_y = 50
                self.display_surface.blit(self.logo, (logo_x, logo_y))

            # 3. Buttons
            self.btn_start.draw(self.display_surface)
            self.btn_leaderboard.draw(self.display_surface)
            self.btn_exit.draw(self.display_surface)
        
        else:
            # Leaderboard screen
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


class PauseMenu:
    """Pause Menu dengan warning tooltip"""
    
    def __init__(self, display_surface: pygame.Surface):
        self.__display_surface = display_surface
        
        try:
            self.font_title = pygame.font.Font(None, 80)
            self.font_button = pygame.font.Font(None, 36)
            self.font_warning = pygame.font.Font(None, 24)
        except:
            self.font_title = pygame.font.SysFont(None, 80)
            self.font_button = pygame.font.SysFont(None, 36)
            self.font_warning = pygame.font.SysFont(None, 24)
        
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        
        self.btn_continue = Button("CONTINUE", (cx, cy), 300, 60, self.font_button)
        self.btn_main_menu = Button("MAIN MENU", (cx, cy + 80), 300, 60, self.font_button)
        
        self.__show_warning = False
        self.__warning_text = "Progress tidak akan di save"
        self.__warning_color = (255, 80, 80)
    
    def draw(self):
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.__display_surface.blit(overlay, (0, 0))
        
        # Title
        paused_text = self.font_title.render("PAUSED", False, (255, 229, 180))
        paused_rect = paused_text.get_frect(center=(WINDOW_WIDTH // 2, 150))
        
        shadow_text = self.font_title.render("PAUSED", False, (0, 0, 0))
        shadow_rect = shadow_text.get_frect(center=(WINDOW_WIDTH // 2 + 3, 150 + 3))
        self.__display_surface.blit(shadow_text, shadow_rect)
        self.__display_surface.blit(paused_text, paused_rect)
        
        # Buttons
        self.btn_continue.draw(self.__display_surface)
        self.btn_main_menu.draw(self.__display_surface)
        
        # Warning Tooltip
        if self.__show_warning:
            warning_x = WINDOW_WIDTH // 2
            warning_y = self.btn_main_menu.rect.bottom + 20
            
            warning_surf_text = self.font_warning.render(self.__warning_text, False, self.__warning_color)
            warning_rect = warning_surf_text.get_rect(center=(warning_x, warning_y))
            
            box_padding = 10
            box_rect = warning_rect.inflate(box_padding * 2, box_padding * 2)
            box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            box_surf.fill((80, 0, 0, 180))
            self.__display_surface.blit(box_surf, box_rect.topleft)
            
            pygame.draw.rect(self.__display_surface, self.__warning_color, box_rect, 2)
            self.__display_surface.blit(warning_surf_text, warning_rect)
    
    def update(self, event_list) -> str:
        mouse_pos = pygame.mouse.get_pos()
        
        self.btn_continue.check_hover(mouse_pos)
        self.btn_main_menu.check_hover(mouse_pos)
        
        self.__show_warning = self.btn_main_menu.is_hovered
        
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "continue"
            
            if self.btn_continue.is_clicked(event):
                return "continue"
            
            if self.btn_main_menu.is_clicked(event):
                return "main_menu"
        
        return None


class GameOverScreen:
    """Layar Game Over dengan statistik akhir"""
    
    def __init__(self, display_surface: pygame.Surface):
        self.__display_surface = display_surface
        self.__font_large = pygame.font.Font(None, 72)
        self.__font_medium = pygame.font.Font(None, 48)
        self.__font_small = pygame.font.Font(None, 32)
    
    def draw(self, final_stats: dict) -> None:
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.__display_surface.blit(overlay, (0, 0))
        
        # Title
        game_over_text = self.__font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.__display_surface.blit(game_over_text, game_over_rect)
        
        # Stats
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
        
        # Restart instruction
        restart_text = self.__font_small.render("Press R to Restart or ESC to Quit", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
        self.__display_surface.blit(restart_text, restart_rect)


class LevelUpNotification:
    """Notifikasi yang muncul saat level up"""
    
    def __init__(self):
        self.__active = False
        self.__start_time = 0
        self.__duration = 2000
        self.__font = pygame.font.Font(None, 64)
    
    def trigger(self, level: int) -> None:
        self.__active = True
        self.__level = level
        self.__start_time = pygame.time.get_ticks()
    
    def update(self) -> None:
        if self.__active:
            if pygame.time.get_ticks() - self.__start_time >= self.__duration:
                self.__active = False
    
    def draw(self, surface: pygame.Surface) -> None:
        if self.__active:
            elapsed = pygame.time.get_ticks() - self.__start_time
            alpha = 255
            if elapsed > self.__duration - 500:
                alpha = int(255 * (1 - (elapsed - (self.__duration - 500)) / 500))
            
            text = self.__font.render(f"LEVEL UP! Level {self.__level}", True, YELLOW)
            text.set_alpha(alpha)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            surface.blit(text, text_rect)


class LevelUpSelectionMenu:
    """Menu pemilihan upgrade saat level up"""
    
    def __init__(self, display_surface: pygame.Surface):
        self.__display_surface = display_surface
        self.__active = False
        self.__cards: List[UpgradeCardUI] = []
        self.__selected_card = None
        
        self.font_title = pygame.font.Font(None, 64)
        
        self.card_width = 450
        self.card_height = 140
        self.card_spacing = 20
    
    def show(self, upgrade_cards: List):
        self.__active = True
        self.__selected_card = None
        self.__cards = []
        
        start_y = (WINDOW_HEIGHT - (self.card_height * 3 + self.card_spacing * 2)) // 2
        center_x = WINDOW_WIDTH // 2 - self.card_width // 2
        
        for i, card in enumerate(upgrade_cards):
            y_pos = start_y + (self.card_height + self.card_spacing) * i
            card_ui = UpgradeCardUI(card, (center_x, y_pos), 
                                   (self.card_width, self.card_height))
            self.__cards.append(card_ui)
    
    def hide(self):
        self.__active = False
        self.__cards = []
    
    @property
    def is_active(self) -> bool:
        return self.__active
    
    def draw(self):
        if not self.__active:
            return
        
        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.__display_surface.blit(overlay, (0, 0))
        
        # Title
        title_text = self.font_title.render("LEVEL UP!", False, (255, 220, 100))
        title_rect = title_text.get_frect(center=(WINDOW_WIDTH // 2, 80))
        
        shadow_text = self.font_title.render("LEVEL UP!", False, (0, 0, 0))
        shadow_rect = shadow_text.get_frect(center=(WINDOW_WIDTH // 2 + 3, 83))
        self.__display_surface.blit(shadow_text, shadow_rect)
        self.__display_surface.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 28)
        subtitle_text = subtitle_font.render("Choose an upgrade", False, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 130))
        self.__display_surface.blit(subtitle_text, subtitle_rect)
        
        # Cards
        for card in self.__cards:
            card.draw(self.__display_surface)
    
    def update(self, event_list) -> Optional[str]:
        if not self.__active:
            return None
        
        mouse_pos = pygame.mouse.get_pos()
        
        for card in self.__cards:
            card.check_hover(mouse_pos)
        
        for event in event_list:
            for card in self.__cards:
                if card.is_clicked(event):
                    return card.card.id
        
        return None
