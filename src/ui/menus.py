"""
UI MENUS MODULE
MainMenu, PauseMenu, GameOverScreen, LevelUpNotification, LevelUpSelectionMenu
"""
import pygame
import math
from typing import List, Optional, Any
from os.path import join
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, RED, YELLOW, BLACK
from .components import Button, UpgradeCardUI


class MainMenu:
    """Main Menu dengan tema neraka yang lebih keren"""
    def __init__(self, display_surface, score_manager=None):
        self.display_surface = display_surface
        self.score_manager = score_manager

        # Load Font
        try:
            self.font_button = pygame.font.Font(None, 40)
            self.font_subtitle = pygame.font.Font(None, 24)
            self.font_score = pygame.font.Font(None, 36)
        except:
            self.font_button = pygame.font.SysFont(None, 40)
            self.font_subtitle = pygame.font.SysFont(None, 24)
            self.font_score = pygame.font.SysFont(None, 36)
        
        # Load Logo InForHell
        self.logo = None
        try:
            logo_path = join('images', 'ui', 'inforhell.png')
            self.logo = pygame.image.load(logo_path).convert_alpha()
            logo_size = 450
            self.logo = pygame.transform.scale(self.logo, (logo_size, logo_size))
            
            # Setup for animation
            self.logo_original = self.logo
            # Create yellow shadow silhouette
            mask = pygame.mask.from_surface(self.logo)
            self.logo_shadow = mask.to_surface(setcolor=(240, 150, 55), unsetcolor=(0,0,0,0))
            
            print("Logo InForHell berhasil dimuat!")
        except Exception as e:
            print(f"Logo tidak ditemukan: {e}")
            self.logo = None
            self.logo_original = None
            self.logo_shadow = None

        # Load Background
        self.background = None
        try:
            bg_path = join('images', 'ui', 'menu_bg.png')
            self.background = pygame.image.load(bg_path).convert()
            bg_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
            self.background = pygame.transform.scale(self.background, bg_size)
            print("Background berhasil dimuat!")
        except Exception as e:
            print(f"Background tidak ditemukan: {e}")
            self.background = None

        # Posisi Tombol
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80
        
        self.btn_start = Button("START GAME", (cx, cy), 300, 60, self.font_button)
        self.btn_leaderboard = Button("LEADERBOARD", (cx, cy + 80), 300, 60, self.font_button)
        self.btn_exit = Button("EXIT", (cx, cy + 160), 300, 60, self.font_button)
        
        self.show_leaderboard = False

    def draw(self):
        # 1. Background
        if self.background:
            self.display_surface.blit(self.background, (0, 0))
        else:
            self.display_surface.fill((15, 5, 5))
        
        if not self.show_leaderboard:
            # 2. Logo
            # 2. Logo (Animated)
            if self.logo_original:
                # Pulsing animation logic
                time_now = pygame.time.get_ticks()
                pulse = math.sin(time_now * 0.003) # Speed
                scale = 1.0 + 0.05 * pulse # Amplitude +/- 5%
                
                orig_rect = self.logo_original.get_rect()
                new_w = int(orig_rect.width * scale)
                new_h = int(orig_rect.height * scale)
                
                # Scale logo and shadow
                logo_surf = pygame.transform.scale(self.logo_original, (new_w, new_h))
                shadow_surf = pygame.transform.scale(self.logo_shadow, (new_w, new_h))
                
                # Position (keep centered at original center)
                center_x = WINDOW_WIDTH // 2
                center_y = 50 + orig_rect.height // 2
                
                logo_rect = logo_surf.get_rect(center=(center_x, center_y))
                
                # Draw Outline (8 directions)
                offsets = [
                    (-3, -3), (0, -3), (3, -3),
                    (-3, 0),           (3, 0),
                    (-3, 3),  (0, 3),  (3, 3)
                ]
                
                for dx, dy in offsets:
                    outline_rect = logo_rect.copy()
                    outline_rect.x += dx
                    outline_rect.y += dy
                    self.display_surface.blit(shadow_surf, outline_rect)
                
                # Draw Logo
                self.display_surface.blit(logo_surf, logo_rect)

            # 3. Buttons
            self.btn_start.draw(self.display_surface)
            self.btn_leaderboard.draw(self.display_surface)
            self.btn_exit.draw(self.display_surface)
        
        else:
            self._draw_leaderboard()

    def _draw_leaderboard(self):
        """Draw leaderboard screen dengan top 5 + player rank"""
        # Title
        try:
            title_font = pygame.font.Font(join('data', 'fonts', 'Oxanium-Bold.ttf'), 70)
        except:
            title_font = pygame.font.SysFont(None, 70)
        
        title_surf = title_font.render("LEADERBOARD", True, (255, 150, 0))
        title_rect = title_surf.get_frect(center=(WINDOW_WIDTH // 2, 80))
        self.display_surface.blit(title_surf, title_rect)
        
        # Get scores from manager
        if self.score_manager:
            top_scores = self.score_manager.get_leaderboard(5)
            last_player = self.score_manager.get_last_player_entry()
        else:
            top_scores = []
            last_player = None
        
        # Draw top 5
        y_start = 160
        y_spacing = 55
        
        # Header
        header_surf = self.font_subtitle.render("RANK    NAME    SCORE", True, (150, 120, 100))
        header_rect = header_surf.get_frect(center=(WINDOW_WIDTH // 2, y_start))
        self.display_surface.blit(header_surf, header_rect)
        
        y_offset = y_start + 40
        
        if not top_scores:
            # No scores yet
            empty_surf = self.font_score.render("No scores yet!", True, (100, 80, 60))
            empty_rect = empty_surf.get_frect(center=(WINDOW_WIDTH // 2, y_offset + 60))
            self.display_surface.blit(empty_surf, empty_rect)
        else:
            # Draw each score
            for entry in top_scores:
                # Color: gold for #1, silver for #2, bronze for #3
                if entry['rank'] == 1:
                    color = (255, 215, 0)  # Gold
                elif entry['rank'] == 2:
                    color = (192, 192, 192)  # Silver
                elif entry['rank'] == 3:
                    color = (205, 127, 50)  # Bronze
                else:
                    color = (255, 220, 180)
                
                # Highlight if this is the last player
                is_last_player = (last_player and 
                                  entry['rank'] == last_player['rank'] and 
                                  entry['name'] == last_player['name'])
                if is_last_player:
                    # Draw highlight background
                    highlight_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, y_offset - 15, 400, 45)
                    pygame.draw.rect(self.display_surface, (80, 40, 20), highlight_rect)
                    pygame.draw.rect(self.display_surface, (255, 150, 0), highlight_rect, 2)
                
                score_text = f"{entry['rank']:2d}.  {entry['name']}  -  {entry['score']:,}"
                score_surf = self.font_score.render(score_text, True, color)
                score_rect = score_surf.get_frect(center=(WINDOW_WIDTH // 2, y_offset))
                self.display_surface.blit(score_surf, score_rect)
                
                y_offset += y_spacing
            
            # Draw player rank if outside top 5
            if last_player and last_player['rank'] > 5:
                # Draw separator
                y_offset += 10
                dots_surf = self.font_score.render(". . .", True, (100, 80, 60))
                dots_rect = dots_surf.get_frect(center=(WINDOW_WIDTH // 2, y_offset))
                self.display_surface.blit(dots_surf, dots_rect)
                
                y_offset += y_spacing
                
                # Draw player's entry with highlight
                highlight_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, y_offset - 15, 400, 45)
                pygame.draw.rect(self.display_surface, (80, 40, 20), highlight_rect)
                pygame.draw.rect(self.display_surface, (255, 150, 0), highlight_rect, 2)
                
                player_text = f"{last_player['rank']:2d}.  {last_player['name']}  -  {last_player['score']:,}"
                player_surf = self.font_score.render(player_text, True, (255, 200, 100))
                player_rect = player_surf.get_frect(center=(WINDOW_WIDTH // 2, y_offset))
                self.display_surface.blit(player_surf, player_rect)
        
        # Back instruction
        back_surf = self.font_button.render("[ ESC to Back ]", True, (150, 100, 80))
        back_rect = back_surf.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
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


class NameInputScreen:
    """Screen untuk input 3-letter name setelah game over"""
    
    def __init__(self, display_surface: pygame.Surface):
        self.__display_surface = display_surface
        self.__active = False
        self.__letters = ['A', 'A', 'A']
        self.__current_index = 0
        self.__final_score = 0
        self.__final_stats = {}
        
        # Fonts
        self.__font_title = pygame.font.Font(None, 64)
        self.__font_letter = pygame.font.Font(None, 100)
        self.__font_info = pygame.font.Font(None, 36)
        self.__font_hint = pygame.font.Font(None, 28)
        
        # Colors
        self.__selected_color = (255, 200, 50)  # Gold
        self.__unselected_color = (150, 130, 110)
        self.__bg_color = (30, 15, 15)
    
    def show(self, score: int, stats: dict) -> None:
        """Tampilkan input screen"""
        self.__active = True
        self.__letters = ['A', 'A', 'A']
        self.__current_index = 0
        self.__final_score = score
        self.__final_stats = stats
    
    def hide(self) -> None:
        """Sembunyikan input screen"""
        self.__active = False
    
    @property
    def is_active(self) -> bool:
        return self.__active
    
    def get_name(self) -> str:
        """Get 3-letter name"""
        return ''.join(self.__letters)
    
    def get_score(self) -> int:
        """Get final score"""
        return self.__final_score
    
    def draw(self) -> None:
        """Draw name input screen"""
        if not self.__active:
            return
        
        # Dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(self.__bg_color)
        self.__display_surface.blit(overlay, (0, 0))
        
        # Title
        title_text = self.__font_title.render("ENTER YOUR NAME", False, (255, 150, 0))
        title_rect = title_text.get_frect(center=(WINDOW_WIDTH // 2, 120))
        self.__display_surface.blit(title_text, title_rect)
        
        # Score display
        score_text = self.__font_info.render(f"Final Score: {self.__final_score:,}", False, WHITE)
        score_rect = score_text.get_frect(center=(WINDOW_WIDTH // 2, 180))
        self.__display_surface.blit(score_text, score_rect)
        
        # Stats
        if self.__final_stats:
            stats_text = f"Level {self.__final_stats.get('level', 1)} | {self.__final_stats.get('kills', 0)} Kills | {self.__final_stats.get('time', '0:00')}"
            stats_surf = self.__font_hint.render(stats_text, False, (150, 130, 110))
            stats_rect = stats_surf.get_frect(center=(WINDOW_WIDTH // 2, 220))
            self.__display_surface.blit(stats_surf, stats_rect)
        
        # Letter boxes
        box_size = 100
        box_spacing = 30
        total_width = box_size * 3 + box_spacing * 2
        start_x = WINDOW_WIDTH // 2 - total_width // 2
        box_y = WINDOW_HEIGHT // 2 - 50
        
        for i, letter in enumerate(self.__letters):
            box_x = start_x + i * (box_size + box_spacing)
            box_rect = pygame.Rect(box_x, box_y, box_size, box_size)
            
            # Box color based on selection
            if i == self.__current_index:
                box_color = self.__selected_color
                border_width = 4
            else:
                box_color = self.__unselected_color
                border_width = 2
            
            # Draw box
            pygame.draw.rect(self.__display_surface, (40, 20, 20), box_rect)
            pygame.draw.rect(self.__display_surface, box_color, box_rect, border_width)
            
            # Draw letter
            letter_surf = self.__font_letter.render(letter, False, box_color)
            letter_rect = letter_surf.get_frect(center=box_rect.center)
            self.__display_surface.blit(letter_surf, letter_rect)
            
            # Draw arrows for selected box
            if i == self.__current_index:
                arrow_color = self.__selected_color
                # Up arrow
                up_points = [
                    (box_rect.centerx, box_rect.top - 20),
                    (box_rect.centerx - 15, box_rect.top - 5),
                    (box_rect.centerx + 15, box_rect.top - 5)
                ]
                pygame.draw.polygon(self.__display_surface, arrow_color, up_points)
                
                # Down arrow
                down_points = [
                    (box_rect.centerx, box_rect.bottom + 20),
                    (box_rect.centerx - 15, box_rect.bottom + 5),
                    (box_rect.centerx + 15, box_rect.bottom + 5)
                ]
                pygame.draw.polygon(self.__display_surface, arrow_color, down_points)
        
        # Instructions
        hint1 = self.__font_hint.render("↑↓ Change Letter  |  ←→ Move  |  ENTER Confirm", False, (120, 100, 80))
        hint1_rect = hint1.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
        self.__display_surface.blit(hint1, hint1_rect)
    
    def update(self, event_list) -> Optional[str]:
        """
        Handle input untuk name entry.
        Returns: 'confirm' jika enter ditekan, None otherwise
        """
        if not self.__active:
            return None
        
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                # Move selection
                if event.key == pygame.K_LEFT:
                    self.__current_index = max(0, self.__current_index - 1)
                elif event.key == pygame.K_RIGHT:
                    self.__current_index = min(2, self.__current_index + 1)
                
                # Change letter
                elif event.key == pygame.K_UP:
                    current_letter = self.__letters[self.__current_index]
                    # A-Z cycle
                    if current_letter == 'Z':
                        self.__letters[self.__current_index] = 'A'
                    else:
                        self.__letters[self.__current_index] = chr(ord(current_letter) + 1)
                
                elif event.key == pygame.K_DOWN:
                    current_letter = self.__letters[self.__current_index]
                    # Z-A cycle
                    if current_letter == 'A':
                        self.__letters[self.__current_index] = 'Z'
                    else:
                        self.__letters[self.__current_index] = chr(ord(current_letter) - 1)
                
                # Direct letter input
                elif event.key >= pygame.K_a and event.key <= pygame.K_z:
                    letter = chr(event.key).upper()
                    self.__letters[self.__current_index] = letter
                    # Auto-advance
                    if self.__current_index < 2:
                        self.__current_index += 1
                
                # Confirm
                elif event.key == pygame.K_RETURN:
                    return 'confirm'
        
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
