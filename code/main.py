"""
MAIN GAME - InForHell
Vampire Survivor-inspired game dengan OOP architecture
"""
from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from ui import GameUI, GameOverScreen, LevelUpNotification
from game_managers import GameState, SpawnManager, CollisionManager

from random import choice


class Game:
    def __init__(self):
        # Setup pygame
        pygame.init()
        self.__display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('InForHell - Vampire Survivor Clone')
        self.__clock = pygame.time.Clock()
        
        # Game state
        self.__game_state = GameState()
        
        # Groups 
        self.__all_sprites = AllSprites()
        self.__collision_sprites = pygame.sprite.Group()
        self.__bullet_sprites = pygame.sprite.Group()
        self.__enemy_sprites = pygame.sprite.Group()
        
        # Gun timer (auto-shoot)
        self.__can_shoot = True
        self.__shoot_time = 0 
        
        # UI
        self.__ui = GameUI(self.__display_surface)
        self.__game_over_screen = GameOverScreen(self.__display_surface)
        self.__level_up_notification = LevelUpNotification()
        
        # Audio 
        try:
            self.__shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
            self.__shoot_sound.set_volume(0.2)
            self.__impact_sound = pygame.mixer.Sound(join('audio', 'impact.ogg'))
            self.__music = pygame.mixer.Sound(join('audio', 'music.wav'))
            self.__music.set_volume(0.5)
            # self.__music.play(loops = -1)
        except:
            # If audio files don't exist, create dummy sounds
            self.__shoot_sound = None
            self.__impact_sound = None
            self.__music = None
        
        # Setup
        self.__load_images()
        self.__setup()
        
        # Managers - gunakan class dari game_managers.py
        self.__spawn_manager = SpawnManager(self.__spawn_positions, self.__enemy_frames)
        self.__collision_manager = CollisionManager(self.__impact_sound)

    def __load_images(self):
        """Load all game images"""
        self.__bullet_surf = pygame.image.load(join('images', 'gun', 'bullet.png')).convert_alpha()

        folders = list(walk(join('images', 'enemies')))[0][1]
        self.__enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                self.__enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.__enemy_frames[folder].append(surf)

    def __auto_shoot(self):
        """Auto-shoot dengan cooldown"""
        if self.__can_shoot and self.__player.stats.is_alive:
            if self.__shoot_sound:
                self.__shoot_sound.play()
            
            pos = self.__gun.rect.center + self.__gun.player_direction * 50
            damage = self.__player.current_damage
            Bullet(self.__bullet_surf, pos, self.__gun.player_direction, 
                   (self.__all_sprites, self.__bullet_sprites), damage)
            
            self.__can_shoot = False
            self.__shoot_time = pygame.time.get_ticks()

    def __gun_timer(self):
        """Update gun cooldown timer"""
        if not self.__can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.__shoot_time >= GUN_COOLDOWN:
                self.__can_shoot = True

    def __setup(self):
        """Setup game world dari TMX map"""
        map = load_pygame(join('data', 'maps', 'world.tmx'))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.__all_sprites)
        
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.__all_sprites, self.__collision_sprites))
        
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.__collision_sprites)

        self.__spawn_positions = []
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.__player = Player((obj.x, obj.y), self.__all_sprites, self.__collision_sprites)
                self.__gun = Gun(self.__player, self.__all_sprites)
            else:
                self.__spawn_positions.append((obj.x, obj.y))

    def __bullet_collision(self):
        """Handle collision antara bullet dan enemy - menggunakan CollisionManager"""
        result = self.__collision_manager.check_bullet_enemy(
            self.__bullet_sprites,
            self.__enemy_sprites,
            self.__player
        )
        
        # Show level up notification jika ada
        if result['level_up']:
            self.__level_up_notification.trigger(self.__player.stats.level)

    def __player_collision(self):
        """Handle collision antara player dan enemy - menggunakan CollisionManager"""
        took_damage = self.__collision_manager.check_player_enemy(
            self.__player,
            self.__enemy_sprites
        )
        
        # Check if player died
        if took_damage and not self.__player.stats.is_alive:
            self.__game_state.set_game_over()

    def __handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__game_state.stop_game()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__game_state.stop_game()
                
                # Restart game when game over
                if self.__game_state.is_game_over:
                    if event.key == pygame.K_r:
                        self.__restart_game()
    
    def __restart_game(self):
        """Restart game dengan state baru"""
        self.__init__()
    
    def __update_game(self, dt):
        """Update game logic"""
        if not self.__game_state.is_game_over and not self.__game_state.is_paused:
            # Update timers
            self.__gun_timer()
            
            # Auto-shoot
            self.__auto_shoot()
            
            # Update sprites
            self.__all_sprites.update(dt)
            
            # Update collisions
            self.__bullet_collision()
            self.__player_collision()
            
            # Update enemy spawning
            elapsed_time = self.__game_state.elapsed_time
            self.__spawn_manager.update_difficulty(elapsed_time)
            
            if self.__spawn_manager.should_spawn():
                self.__spawn_manager.spawn_enemy(
                    (self.__all_sprites, self.__enemy_sprites),
                    self.__player,
                    self.__collision_sprites,
                    EnemyFactory
                )
            
            # Update UI
            self.__ui.update_player_stats(self.__player.stats)
            self.__ui.update_time(elapsed_time)
            
            # Calculate and update score
            score = self.__game_state.calculate_score(self.__player.stats)
            self.__ui.update_score(score)
            
            # Update level up notification
            self.__level_up_notification.update()
    
    def __draw_game(self):
        """Draw everything"""
        # Clear screen
        self.__display_surface.fill('black')
        
        # Draw sprites
        self.__all_sprites.draw(self.__player.rect.center)
        
        # Draw UI
        self.__ui.draw()
        
        # Draw level up notification
        self.__level_up_notification.draw(self.__display_surface)
        
        # Draw game over screen if game over
        if self.__game_state.is_game_over:
            final_stats = {
                'score': self.__game_state.score,
                'level': self.__player.stats.level,
                'kills': self.__player.stats.kills,
                'time': f"{int(self.__game_state.elapsed_time // 60)}:{int(self.__game_state.elapsed_time % 60):02d}"
            }
            self.__game_over_screen.draw(final_stats)
        
        pygame.display.update()
    
    def run(self):
        """Main game loop"""
        while self.__game_state.is_running:
            # Delta time
            dt = self.__clock.tick(FPS) / 1000
            
            # Handle events
            self.__handle_events()
            
            # Update
            self.__update_game(dt)
            
            # Draw
            self.__draw_game()
        
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()