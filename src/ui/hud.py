"""
UI HUD MODULE
GameUI Overlay untuk gameplay.
"""
import pygame
from typing import Any
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_MAX_HEALTH, WHITE, YELLOW, DARK_GRAY
from .components import HealthBar, ExperienceBar, TextLabel


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
        self.__score_label = TextLabel((WINDOW_WIDTH - 150, 130), "Score: 0", 28, (0, 255, 0))
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
            pulse = (pygame.time.get_ticks() // 200) % 2
            color = YELLOW if pulse else (255, 215, 0)
            pygame.draw.rect(self.__display_surface, color, rect, 3)
            
            # Ready Text
            font = pygame.font.Font(None, 20)
            text = font.render("Ready", True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.__display_surface.blit(text, text_rect)
    
    def draw(self) -> None:
        """Gambar semua elemen UI"""
        for element in self.__ui_elements:
            element.draw(self.__display_surface)
