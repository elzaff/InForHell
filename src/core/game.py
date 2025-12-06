"""
CORE GAME MODULE
Class Game utama yang mengatur game loop.
"""
import pygame
from os.path import join
from pytmx.util_pygame import load_pygame

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TILE_SIZE, GUN_COOLDOWN
)
from src.core.groups import AllSprites
from src.core.pathfinding import Pathfinder
from src.entities.player import Player
from src.entities.sprites import Sprite, CollisionSprite
from src.entities.enemies import EnemyFactory
from src.combat.weapons import Bullet
from src.combat.skills import KeyboardRain
from src.combat.mechanics import WeaponDefault
from src.systems.spawn_manager import SpawnManager
from src.systems.collision_manager import CollisionManager
from src.systems.upgrade_manager import UpgradeDatabase, GameState
from src.systems.score_manager import ScoreManager
from src.ui.hud import GameUI
from src.ui.menus import MainMenu, PauseMenu, GameOverScreen, LevelUpNotification, LevelUpSelectionMenu, NameInputScreen


class Game:
    """
    Class Utama Game.
    Mengatur inisialisasi, game loop, dan manajemen state.
    """
    def __init__(self):
        # Setup pygame
        pygame.init()
        self.__display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('InForHell - Vampire Survivor Clone')
        self.__clock = pygame.time.Clock()
        
        # --- SCORE SYSTEM ---
        self.__score_manager = ScoreManager()
        
        # --- MENU SYSTEM ---
        self.__in_menu = True  # Game mulai di Menu
        self.__main_menu = MainMenu(self.__display_surface, self.__score_manager)
        self.__name_input_screen = NameInputScreen(self.__display_surface)
        self.__awaiting_name_input = False
        
        # Load aset dan komponen game tapi belum dimainkan
        self.__setup_game_components()

    def __setup_game_components(self):
        """Fungsi helper untuk reset/setup ulang game saat Start/Restart"""
        self.__game_state = GameState()
        
        # Groups 
        self.__all_sprites = AllSprites()
        self.__collision_sprites = pygame.sprite.Group()
        self.__bullet_sprites = pygame.sprite.Group()
        self.__enemy_sprites = pygame.sprite.Group()
        
        # Timer Senjata
        self.__can_shoot = True
        self.__shoot_time = 0 
        
        # UI Gameplay
        self.__ui = GameUI(self.__display_surface)
        self.__game_over_screen = GameOverScreen(self.__display_surface)
        self.__level_up_notification = LevelUpNotification()
        self.__pause_menu = PauseMenu(self.__display_surface)
        self.__level_up_menu = LevelUpSelectionMenu(self.__display_surface)
        
        # Upgrade System
        self.__upgrade_db = UpgradeDatabase()
        
        # Audio 
        try:
            self.__shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
            self.__shoot_sound.set_volume(0.2)
            self.__impact_sound = pygame.mixer.Sound(join('audio', 'impact.ogg'))
            self.__music = pygame.mixer.Sound(join('audio', 'music.wav'))
            self.__music.set_volume(0.5)
        except:
            self.__shoot_sound = None
            self.__impact_sound = None
            self.__music = None
        
        # Setup Aset & Map
        self.__load_images()
        self.__setup()
        
        # Managers
        self.__spawn_manager = SpawnManager(
            self.__spawn_positions, 
            self.__enemy_frames, 
            self.__pathfinder 
        )
        self.__collision_manager = CollisionManager(self.__impact_sound)

    def __load_images(self) -> None:
        """Memuat gambar dengan aman"""
        from os import walk
        
        self.__bullet_surf = pygame.image.load(join('images', 'gun', 'bullet.png')).convert_alpha()

        enemies_path = join('images', 'enemies')
        self.__enemy_frames = {}

        if not list(walk(enemies_path)):
            return
        
        folders = list(walk(enemies_path))[0][1]

        for folder in folders:
            folder_path = join(enemies_path, folder)
            self.__enemy_frames[folder] = []
            
            for _, __, file_names in walk(folder_path):
                png_files = [f for f in file_names if f.endswith('.png')]
                try:
                    png_files.sort(key=lambda name: int(name.split('.')[0]))
                except ValueError:
                    png_files.sort()

                for file_name in png_files:
                    full_path = join(folder_path, file_name)
                    try:
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.__enemy_frames[folder].append(surf)
                    except:
                        pass

    def __setup(self) -> None:
        """Setup dunia game dari TMX map"""
        map = load_pygame(join('data', 'maps', 'world.tmx'))
        
        # Init Pathfinder
        self.__pathfinder = Pathfinder(map)

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
                
                self.__player.weapon = WeaponDefault(
                    player=self.__player,
                    groups=(self.__all_sprites, self.__bullet_sprites)
                )
                
                self.__player.active_skill = KeyboardRain(
                    groups=(self.__all_sprites, self.__bullet_sprites)
                )
                self.__player.active_skill.set_player(self.__player)
            else:
                self.__spawn_positions.append((obj.x, obj.y))

    def __handle_events(self) -> None:
        """Handle input: Membedakan saat di Menu vs Gameplay vs Pause vs Level Up"""
        event_list = pygame.event.get()
        
        # Handle QUIT event
        for event in event_list:
            if event.type == pygame.QUIT:
                self.__game_state.stop_game()
                return

        # --- INPUT LEVEL UP SELECTION (prioritas tertinggi) ---
        if self.__level_up_menu.is_active:
            selected_upgrade_id = self.__level_up_menu.update(event_list)
            if selected_upgrade_id:
                self.__upgrade_db.apply_upgrade(selected_upgrade_id, self.__player)
                self.__level_up_menu.hide()
                self.__game_state.resume()
            return

        # --- INPUT NAME INPUT (setelah game over) ---
        if self.__name_input_screen.is_active:
            action = self.__name_input_screen.update(event_list)
            if action == 'confirm':
                # Save score
                player_name = self.__name_input_screen.get_name()
                player_score = self.__name_input_screen.get_score()
                self.__score_manager.save_score(player_name, player_score)
                self.__name_input_screen.hide()
                # Go to main menu
                self.__in_menu = True
                if self.__music: self.__music.stop()
            return

        # --- INPUT PAUSE MENU ---
        if not self.__in_menu and self.__game_state.is_paused:
            action = self.__pause_menu.update(event_list)
            if action == "continue":
                self.__game_state.resume()
            elif action == "main_menu":
                self.__game_state.resume()
                self.__in_menu = True
                if self.__music: self.__music.stop()
            return

        # --- INPUT GAMEPLAY ---
        if not self.__in_menu and not self.__game_state.is_paused:
            for event in event_list:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.__game_state.is_game_over:
                            # Langsung ke name input
                            self.__trigger_name_input()
                        else:
                            self.__game_state.pause()
                    
                    if self.__game_state.is_game_over:
                        if event.key == pygame.K_r:
                            self.__restart_game()
                        elif event.key == pygame.K_RETURN:
                            # ENTER juga trigger name input
                            self.__trigger_name_input()
            return

        # --- INPUT MAIN MENU ---
        if self.__in_menu:
            action = self.__main_menu.update(event_list)
            if action == "start":
                self.__in_menu = False
                self.__restart_game()
            elif action == "exit":
                self.__game_state.stop_game()

    def __restart_game(self) -> None:
        """Restart game total"""
        self.__score_manager.clear_last_player()  # Clear last player tracking
        # Stop music dulu sebelum restart
        if self.__music:
            self.__music.stop()
        self.__setup_game_components()
        if self.__music: 
            self.__music.play(loops=-1)
    
    def __trigger_name_input(self) -> None:
        """Trigger name input screen setelah game over"""
        final_stats = {
            'score': self.__game_state.score,
            'level': self.__player.stats.level,
            'kills': self.__player.stats.kills,
            'time': f"{int(self.__game_state.elapsed_time // 60)}:{int(self.__game_state.elapsed_time % 60):02d}"
        }
        self.__name_input_screen.show(self.__game_state.score, final_stats)

    def __update_game(self, dt: float) -> None:
        """Update game logic"""
        if self.__in_menu or self.__game_state.is_paused or self.__level_up_menu.is_active:
            return

        if not self.__game_state.is_game_over:
            self.__gun_timer()
            self.__auto_shoot()
            
            if self.__player.active_skill:
                self.__player.active_skill.set_cooldown_modifier(self.__player.stat_modifiers['cooldown'])
                self.__player.active_skill.update(dt)
            
            self.__all_sprites.update(dt)
            self.__bullet_collision()
            self.__player_collision()
            
            elapsed_time = self.__game_state.elapsed_time
            self.__spawn_manager.update_difficulty(elapsed_time)
            
            if self.__spawn_manager.should_spawn():
                self.__spawn_manager.spawn_enemy(
                    (self.__all_sprites, self.__enemy_sprites),
                    self.__player,
                    self.__collision_sprites,
                    EnemyFactory
                )
            
            self.__ui.update_player_stats(self.__player.stats)
            self.__ui.update_time(elapsed_time)
            
            score = self.__game_state.calculate_score(self.__player.stats)
            self.__ui.update_score(score)
            
            self.__level_up_notification.update()
    
    def __gun_timer(self) -> None:
        if not self.__can_shoot:
            current_time = pygame.time.get_ticks()
            cooldown = self.__player.weapon.cooldown if self.__player.weapon else GUN_COOLDOWN
            if current_time - self.__shoot_time >= cooldown:
                self.__can_shoot = True

    def __auto_shoot(self) -> None:
        if self.__can_shoot and self.__player.stats.is_alive:
            if self.__shoot_sound: self.__shoot_sound.play()
            if self.__player.weapon:
                shoot_info = self.__player.weapon.attack()
                
                if isinstance(shoot_info, dict) and shoot_info.get('multi'):
                    for bullet_data in shoot_info['bullets']:
                        Bullet(
                            surf=self.__bullet_surf,
                            pos=bullet_data['position'],
                            direction=bullet_data['direction'],
                            groups=(self.__all_sprites, self.__bullet_sprites),
                            damage=bullet_data['damage']
                        )
                else:
                    Bullet(
                        surf=self.__bullet_surf,
                        pos=shoot_info['position'],
                        direction=shoot_info['direction'],
                        groups=(self.__all_sprites, self.__bullet_sprites),
                        damage=shoot_info['damage']
                    )
            self.__can_shoot = False
            self.__shoot_time = pygame.time.get_ticks()

    def __bullet_collision(self) -> None:
        result = self.__collision_manager.check_bullet_enemy(
            self.__bullet_sprites, self.__enemy_sprites, self.__player
        )
        if result['level_up']:
            self.__trigger_level_up()
    
    def __trigger_level_up(self) -> None:
        """Trigger level up selection menu"""
        self.__game_state.pause()
        upgrade_cards = self.__upgrade_db.get_available_upgrades(count=3)
        self.__level_up_menu.show(upgrade_cards)
        self.__level_up_notification.trigger(self.__player.stats.level)

    def __player_collision(self) -> None:
        took_damage = self.__collision_manager.check_player_enemy(self.__player, self.__enemy_sprites)
        if took_damage and not self.__player.stats.is_alive:
            self.__game_state.set_game_over()

    def __draw_game(self) -> None:
        """Draw everything"""
        self.__display_surface.fill('black')
        
        if self.__in_menu:
            self.__main_menu.draw()
        else:
            self.__all_sprites.draw(self.__player.rect.center)
            self.__ui.draw()
            self.__ui.draw_skill_icon(self.__player.active_skill)
            self.__level_up_notification.draw(self.__display_surface)
            
            if self.__level_up_menu.is_active:
                self.__level_up_menu.draw()
            elif self.__name_input_screen.is_active:
                self.__name_input_screen.draw()
            elif self.__game_state.is_paused:
                self.__pause_menu.draw()
            elif self.__game_state.is_game_over:
                final_stats = {
                    'score': self.__game_state.score,
                    'level': self.__player.stats.level,
                    'kills': self.__player.stats.kills,
                    'time': f"{int(self.__game_state.elapsed_time // 60)}:{int(self.__game_state.elapsed_time % 60):02d}"
                }
                self.__game_over_screen.draw(final_stats)
        
        pygame.display.update()
    
    def run(self) -> None:
        """Main game loop"""
        while self.__game_state.is_running:
            dt = self.__clock.tick(FPS) / 1000
            self.__handle_events()
            self.__update_game(dt)
            self.__draw_game()
        pygame.quit()
