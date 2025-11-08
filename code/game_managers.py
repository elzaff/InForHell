"""
LAYER 5: Management Systems - GameState, SpawnManager, CollisionManager
Implementasi sesuai class diagram
"""
from settings import *
import pygame
from random import choice


# ==================== GAME STATE ====================

class GameState:
    """
    Manage game state dengan encapsulation
    Properties: __is_running, __is_paused, __is_game_over, __score, __start_time
    Methods: calculate_score(player_stats), toggle_pause()
    """
    
    def __init__(self):
        self.__is_running = True
        self.__is_paused = False
        self.__is_game_over = False
        self.__start_time = pygame.time.get_ticks()
        self.__game_over_time = 0  # Waktu saat game over
        self.__score = 0
    
    @property
    def is_running(self):
        return self.__is_running
    
    @property
    def is_paused(self):
        return self.__is_paused
    
    @property
    def is_game_over(self):
        return self.__is_game_over
    
    @property
    def elapsed_time(self):
        """Get elapsed time in seconds - frozen saat game over"""
        if self.__is_game_over and self.__game_over_time > 0:
            # Return waktu saat game over (frozen)
            return (self.__game_over_time - self.__start_time) / 1000
        else:
            # Return waktu current (masih bermain)
            return (pygame.time.get_ticks() - self.__start_time) / 1000
    
    @property
    def score(self):
        return self.__score
    
    def stop_game(self):
        """Stop game loop"""
        self.__is_running = False
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.__is_paused = not self.__is_paused
    
    def set_game_over(self):
        """Set game over state dan freeze waktu"""
        if not self.__is_game_over:
            self.__is_game_over = True
            self.__game_over_time = pygame.time.get_ticks()  # Simpan waktu saat game over
    
    def calculate_score(self, player_stats):
        """
        Calculate score based on kills, level, and time
        Formula: (kills * 100) + (level * 500) + (time * 10)
        """
        kills_score = player_stats.kills * 100
        level_score = player_stats.level * 500
        time_score = int(self.elapsed_time * 10)
        self.__score = kills_score + level_score + time_score
        return self.__score


# ==================== SPAWN MANAGER ====================

class SpawnManager:
    """
    Manage enemy spawning dengan difficulty scaling
    Properties: __spawn_positions, __difficulty
    Methods: spawn_enemy(), update_difficulty(time), should_spawn()
    """
    
    def __init__(self, spawn_positions, enemy_frames):
        self.__spawn_positions = spawn_positions
        self.__enemy_frames = enemy_frames
        self.__spawn_interval = ENEMY_SPAWN_INTERVAL
        self.__last_spawn_time = pygame.time.get_ticks()
        self.__difficulty_multiplier = 1.0
        self.__enemies_spawned = 0
    
    @property
    def difficulty_multiplier(self):
        return self.__difficulty_multiplier
    
    @property
    def enemies_spawned(self):
        return self.__enemies_spawned
    
    def update_difficulty(self, elapsed_time: float):
        """
        Increase difficulty over time
        Every 30 seconds: +20% difficulty, reduce spawn interval
        """
        # Increase difficulty multiplier
        self.__difficulty_multiplier = 1.0 + (elapsed_time // 30) * 0.2
        
        # Reduce spawn interval (faster spawning)
        self.__spawn_interval = max(500, ENEMY_SPAWN_INTERVAL - int(elapsed_time * 10))
    
    def should_spawn(self) -> bool:
        """Check if it's time to spawn enemy"""
        current_time = pygame.time.get_ticks()
        if current_time - self.__last_spawn_time >= self.__spawn_interval:
            self.__last_spawn_time = current_time
            return True
        return False
    
    def spawn_enemy(self, groups, player, collision_sprites, enemy_factory):
        """
        Spawn random enemy at random position far from player
        Returns: spawned enemy or None
        """
        # Choose spawn position far from player
        player_pos = pygame.Vector2(player.rect.center)
        valid_positions = []
        
        for pos in self.__spawn_positions:
            spawn_pos = pygame.Vector2(pos)
            distance = (spawn_pos - player_pos).length()
            if distance > ENEMY_SPAWN_DISTANCE:
                valid_positions.append(pos)
        
        if valid_positions:
            spawn_pos = choice(valid_positions)
            enemy = enemy_factory.create_random_enemy(
                spawn_pos, 
                self.__enemy_frames,
                groups,
                player,
                collision_sprites
            )
            self.__enemies_spawned += 1
            return enemy
        return None
    
    def reset(self):
        """Reset spawn manager"""
        self.__last_spawn_time = pygame.time.get_ticks()
        self.__difficulty_multiplier = 1.0
        self.__enemies_spawned = 0


# ==================== COLLISION MANAGER ====================

class CollisionManager:
    """
    Manage all collision detection
    Methods: check_bullet_enemy(), check_player_enemy(), check_player_item()
    """
    
    def __init__(self, impact_sound=None):
        self.__impact_sound = impact_sound
    
    def check_bullet_enemy(self, bullet_sprites, enemy_sprites, player) -> dict:
        """
        Check collision between bullets and enemies
        Returns: dict with 'kills', 'exp_gained', 'level_up'
        """
        result = {
            'kills': 0,
            'exp_gained': 0,
            'level_up': False
        }
        
        if bullet_sprites:
            for bullet in bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(
                    bullet, enemy_sprites, False, pygame.sprite.collide_mask
                )
                
                if collision_sprites:
                    if self.__impact_sound:
                        self.__impact_sound.play()
                    
                    for enemy in collision_sprites:
                        # take_damage return True jika enemy baru mati
                        just_died = enemy.take_damage(bullet.damage)
                        
                        # Give EXP and kill count hanya jika baru mati
                        if just_died:
                            exp_reward = enemy.give_exp_reward()
                            if exp_reward > 0:
                                leveled_up = player.gain_exp(exp_reward)
                                player.stats.add_kill()
                                
                                result['kills'] += 1
                                result['exp_gained'] += exp_reward
                                if leveled_up:
                                    result['level_up'] = True
                    
                    bullet.kill()
        
        return result
    
    def check_player_enemy(self, player, enemy_sprites) -> bool:
        """
        Check collision between player and enemies
        Returns: True if player took damage
        """
        if player.stats.is_alive:
            collided_enemies = pygame.sprite.spritecollide(
                player, enemy_sprites, False, pygame.sprite.collide_mask
            )
            
            if collided_enemies:
                # Take damage from all colliding enemies
                for enemy in collided_enemies:
                    if not enemy.is_dead:
                        player.take_damage(enemy.damage)
                return True
        return False
    
    def check_player_item(self, player, item_sprites) -> list:
        """
        Check collision between player and items
        Returns: list of picked items
        """
        picked_items = []
        
        # Check attraction first
        player_pos = pygame.Vector2(player.rect.center)
        for item in item_sprites:
            if hasattr(item, 'check_attraction'):
                item.check_attraction(player_pos)
            if hasattr(item, 'move_towards_player'):
                item.move_towards_player(player_pos, 1/60)  # Assume 60 FPS
        
        # Check pickup collision
        collided_items = pygame.sprite.spritecollide(
            player, item_sprites, False, pygame.sprite.collide_mask
        )
        
        if collided_items:
            for item in collided_items:
                if hasattr(item, 'on_pickup'):
                    item.on_pickup(player)
                    picked_items.append(item)
                    item.kill()
        
        return picked_items
