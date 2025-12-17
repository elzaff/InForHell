"""
UI HUD Module
GameUI Overlay untuk tampilan gameplay.
"""
import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_MAX_HEALTH, WHITE, YELLOW, DARK_GRAY
from .components import HealthBar, ExperienceBar, TextLabel


class GameUI:
    """Manager UI utama untuk HUD gameplay."""
    
    def __init__(self, display_surface: pygame.Surface):
        self.__display_surface = display_surface
        self.__ui_elements = []
        self.__setup_ui()
    
    def __setup_ui(self) -> None:
        """Setup semua elemen UI."""
        # Health bar
        self.__health_bar = HealthBar((10, 10), (264, 40), PLAYER_MAX_HEALTH)
        self.__ui_elements.append(self.__health_bar)
        
        # Experience bar
        self.__exp_bar = ExperienceBar((10, 55), (264, 40))
        self.__ui_elements.append(self.__exp_bar)
        
        # Info di kanan atas
        self.__level_label = TextLabel((WINDOW_WIDTH - 150, 20), "Level: 1", 32, YELLOW)
        self.__ui_elements.append(self.__level_label)
        
        self.__kill_label = TextLabel((WINDOW_WIDTH - 150, 60), "Kills: 0", 28, WHITE)
        self.__ui_elements.append(self.__kill_label)
        
        self.__time_label = TextLabel((WINDOW_WIDTH - 150, 95), "Time: 0:00", 28, WHITE)
        self.__ui_elements.append(self.__time_label)
        
        self.__score_label = TextLabel((WINDOW_WIDTH - 150, 130), "Score: 0", 28, (0, 255, 0))
        self.__ui_elements.append(self.__score_label)
    
    def update_player_stats(self, player_stats) -> None:
        """Update UI berdasarkan stats player."""
        self.__health_bar.update_max_health(player_stats.max_health)
        self.__health_bar.update_health(player_stats.current_health)
        self.__exp_bar.update_exp(player_stats.current_exp, player_stats.exp_to_next_level)
        self.__level_label.set_text(f"Level: {player_stats.level}")
        self.__kill_label.set_text(f"Kills: {player_stats.kills}")
    
    def update_time(self, seconds: float) -> None:
        """Update tampilan waktu."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        self.__time_label.set_text(f"Time: {minutes}:{secs:02d}")
    
    def update_score(self, score: int) -> None:
        """Update tampilan skor."""
        self.__score_label.set_text(f"Score: {score}")
        
    def draw_skill_icon(self, skill) -> None:
        """Gambar icon skill dengan cooldown."""
        if not skill: 
            return
        
        # Load overlay (cached)
        if not hasattr(self, '_skill_overlay'):
            try:
                from os.path import join
                self._skill_overlay = pygame.image.load(join('images', 'ui', 'skillbutton.png')).convert_alpha()
            except:
                self._skill_overlay = None
        
        x, y = 10, 100
        
        if self._skill_overlay:
            overlay_w, overlay_h = self._skill_overlay.get_size()
            rect = pygame.Rect(x, y, overlay_w, overlay_h)
            
            self.__display_surface.blit(self._skill_overlay, (x, y))
            
            progress = skill.cooldown_progress
            if progress < 1.0:
                # Tampilkan countdown
                remaining_time = (skill.cooldown * (1 - progress)) / 1000
                timer_font = pygame.font.Font(None, 28)
                timer_text = timer_font.render(f"{remaining_time:.1f}s", True, WHITE)
                timer_rect = timer_text.get_rect(center=rect.center)
                self.__display_surface.blit(timer_text, timer_rect)
            else:
                # Text Ready berkedip
                pulse = (pygame.time.get_ticks() // 400) % 2
                if pulse:
                    ready_font = pygame.font.Font(None, 24)
                    ready_text = ready_font.render("Ready", True, YELLOW)
                    ready_rect = ready_text.get_rect(center=rect.center)
                    self.__display_surface.blit(ready_text, ready_rect)
        else:
            # Fallback tanpa overlay
            size = 40
            rect = pygame.Rect(x, y, size, size)
            pygame.draw.rect(self.__display_surface, DARK_GRAY, rect)
            
            progress = skill.cooldown_progress
            if progress < 1.0:
                remaining_time = (skill.cooldown * (1 - progress)) / 1000
                timer_font = pygame.font.Font(None, 24)
                timer_text = timer_font.render(f"{remaining_time:.1f}", True, WHITE)
                timer_rect = timer_text.get_rect(center=rect.center)
                self.__display_surface.blit(timer_text, timer_rect)
            else:
                pulse = (pygame.time.get_ticks() // 400) % 2
                if pulse:
                    ready_font = pygame.font.Font(None, 18)
                    ready_text = ready_font.render("Ready", True, YELLOW)
                    ready_rect = ready_text.get_rect(center=rect.center)
                    self.__display_surface.blit(ready_text, ready_rect)
    
    def draw_boss_health(self, boss_sprite) -> None:
        """Gambar health bar boss di bawah layar."""
        if not boss_sprite or boss_sprite.health_percentage <= 0:
            return

        bar_width = WINDOW_WIDTH - 400
        bar_height = 25
        x = 200
        y = WINDOW_HEIGHT - 50
        
        # Background
        pygame.draw.rect(self.__display_surface, DARK_GRAY, (x, y, bar_width, bar_height), border_radius=5)
        
        # Health fill
        fill_width = int(bar_width * boss_sprite.health_percentage)
        pygame.draw.rect(self.__display_surface, (200, 0, 0), (x, y, fill_width, bar_height), border_radius=5)
        
        # Border
        pygame.draw.rect(self.__display_surface, YELLOW, (x, y, bar_width, bar_height), 2, border_radius=5)
        
        # Label BOSS
        font = pygame.font.Font(None, 30)
        text = font.render("BOSS", True, YELLOW)
        text_rect = text.get_rect(center=(x + bar_width // 2, y - 15))
        self.__display_surface.blit(text, text_rect)

    def draw(self) -> None:
        """Gambar semua elemen UI."""
        for element in self.__ui_elements:
            element.draw(self.__display_surface)