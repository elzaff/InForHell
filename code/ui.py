"""
Module untuk UI System dengan encapsulation
"""
from settings import *
import pygame


class UIElement:
    """Base class untuk UI elements dengan encapsulation"""
    
    def __init__(self, pos, size):
        self.__pos = pos
        self.__size = size
        self.__visible = True
    
    @property
    def pos(self):
        return self.__pos
    
    @property
    def size(self):
        return self.__size
    
    @property
    def visible(self):
        return self.__visible
    
    def set_visible(self, visible: bool):
        self.__visible = visible
    
    def draw(self, surface):
        if self.__visible:
            self._render(surface)
    
    def _render(self, surface):
        """Override this in subclasses"""
        pass


class HealthBar(UIElement):
    """Health bar dengan border dan color gradient"""
    
    def __init__(self, pos, size, max_health):
        super().__init__(pos, size)
        self.__max_health = max_health
        self.__current_health = max_health
        self.__border_width = 2
    
    def update_health(self, current_health):
        self.__current_health = max(0, min(current_health, self.__max_health))
    
    def _render(self, surface):
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
            
            # Color gradient based on health
            if health_percentage > 0.5:
                color = GREEN
            elif health_percentage > 0.25:
                color = YELLOW
            else:
                color = RED
            
            pygame.draw.rect(surface, color, health_rect)


class ExperienceBar(UIElement):
    """Experience bar untuk menunjukkan progress ke level berikutnya"""
    
    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.__current_exp = 0
        self.__exp_to_next = 100
        self.__border_width = 2
    
    def update_exp(self, current_exp, exp_to_next):
        self.__current_exp = current_exp
        self.__exp_to_next = exp_to_next
    
    def _render(self, surface):
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
    """Label untuk menampilkan text"""
    
    def __init__(self, pos, text, font_size=24, color=WHITE):
        super().__init__(pos, (0, 0))
        self.__text = text
        self.__font_size = font_size
        self.__color = color
        self.__font = pygame.font.Font(None, font_size)
    
    def set_text(self, text):
        self.__text = text
    
    def set_color(self, color):
        self.__color = color
    
    def _render(self, surface):
        text_surf = self.__font.render(self.__text, True, self.__color)
        surface.blit(text_surf, self.pos)


class GameUI:
    """Main UI Manager yang mengkoordinasi semua UI elements"""
    
    def __init__(self, display_surface):
        self.__display_surface = display_surface
        self.__ui_elements = []
        
        # Create UI components
        self.__setup_ui()
    
    def __setup_ui(self):
        """Setup semua UI elements dengan encapsulation"""
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
    
    def update_player_stats(self, player_stats):
        """Update UI berdasarkan player stats"""
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
    
    def update_time(self, seconds):
        """Update time display"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        self.__time_label.set_text(f"Time: {minutes}:{secs:02d}")
    
    def update_score(self, score):
        """Update score display"""
        self.__score_label.set_text(f"Score: {score}")
    
    def draw(self):
        """Draw all UI elements"""
        for element in self.__ui_elements:
            element.draw(self.__display_surface)


class GameOverScreen:
    """Game Over screen dengan final statistics"""
    
    def __init__(self, display_surface):
        self.__display_surface = display_surface
        self.__font_large = pygame.font.Font(None, 72)
        self.__font_medium = pygame.font.Font(None, 48)
        self.__font_small = pygame.font.Font(None, 32)
    
    def draw(self, final_stats):
        """Draw game over screen dengan statistics"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.__display_surface.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.__font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.__display_surface.blit(game_over_text, game_over_rect)
        
        # Final statistics
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
    """Notification yang muncul saat level up"""
    
    def __init__(self):
        self.__active = False
        self.__start_time = 0
        self.__duration = 2000  # 2 seconds
        self.__font = pygame.font.Font(None, 64)
    
    def trigger(self, level):
        """Trigger notification"""
        self.__active = True
        self.__level = level
        self.__start_time = pygame.time.get_ticks()
    
    def update(self):
        """Update notification state"""
        if self.__active:
            if pygame.time.get_ticks() - self.__start_time >= self.__duration:
                self.__active = False
    
    def draw(self, surface):
        """Draw notification"""
        if self.__active:
            # Fade effect
            elapsed = pygame.time.get_ticks() - self.__start_time
            alpha = 255
            if elapsed > self.__duration - 500:
                alpha = int(255 * (1 - (elapsed - (self.__duration - 500)) / 500))
            
            text = self.__font.render(f"LEVEL UP! Level {self.__level}", True, YELLOW)
            text.set_alpha(alpha)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            surface.blit(text, text_rect)
