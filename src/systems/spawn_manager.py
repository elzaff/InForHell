"""
SPAWN MANAGER MODULE
Mengelola kemunculan musuh dengan skala kesulitan.
"""
import pygame
from random import choice
from typing import List, Tuple, Dict, Any
from settings import ENEMY_SPAWN_INTERVAL, ENEMY_SPAWN_DISTANCE


class SpawnManager:
    """
    Mengelola kemunculan musuh dengan skala kesulitan.
    Properties: __spawn_positions, __difficulty
    Methods: spawn_enemy(), update_difficulty(time), should_spawn()
    """
    
    def __init__(self, spawn_positions: List[Tuple[int, int]], 
                 enemy_frames: Dict[str, List[pygame.Surface]], 
                 pathfinder): 
                 
        self.__spawn_positions = spawn_positions
        self.__enemy_frames = enemy_frames
        self.__pathfinder = pathfinder 
        self.__spawn_interval = ENEMY_SPAWN_INTERVAL
        self.__last_spawn_time = pygame.time.get_ticks()
        self.__difficulty_multiplier = 1.0
        self.__enemies_spawned = 0
    
    @property
    def difficulty_multiplier(self) -> float:
        return self.__difficulty_multiplier
    
    @property
    def enemies_spawned(self) -> int:
        return self.__enemies_spawned
    
    def update_difficulty(self, elapsed_time: float) -> None:
        """
        Meningkatkan kesulitan seiring waktu.
        Setiap 30 detik: +20% kesulitan, kurangi interval spawn.
        """
        # Tingkatkan multiplier kesulitan
        self.__difficulty_multiplier = 1.0 + (elapsed_time // 30) * 0.2
        
        # Kurangi interval spawn (spawn lebih cepat)
        self.__spawn_interval = max(500, ENEMY_SPAWN_INTERVAL - int(elapsed_time * 10))
    
    def should_spawn(self) -> bool:
        """Cek apakah waktunya memunculkan musuh"""
        current_time = pygame.time.get_ticks()
        if current_time - self.__last_spawn_time >= self.__spawn_interval:
            self.__last_spawn_time = current_time
            return True
        return False
    
    def spawn_enemy(self, groups, player, collision_sprites, enemy_factory):
        """
        Memunculkan musuh acak di posisi acak yang jauh dari player.
        Returns: musuh yang dimunculkan atau None.
        """
        # Pilih posisi spawn yang jauh dari player
        player_pos = pygame.Vector2(player.rect.center)
        valid_positions = []
        
        for pos in self.__spawn_positions:
            spawn_pos = pygame.Vector2(pos)
            distance = (spawn_pos - player_pos).length()
            if distance > ENEMY_SPAWN_DISTANCE:
                valid_positions.append(pos)
        
        if valid_positions and self.__enemy_frames:
            spawn_pos = choice(valid_positions)
            enemy_type = choice(['books', 'paper', 'redblob','slime','toast'])
            enemy = enemy_factory.create_enemy(
                enemy_type,
                spawn_pos, 
                self.__enemy_frames,
                groups,
                player,
                collision_sprites,
                self.__pathfinder)
            self.__enemies_spawned += 1
            return enemy
        return None
    
    def reset(self) -> None:
        """Reset spawn manager"""
        self.__last_spawn_time = pygame.time.get_ticks()
        self.__difficulty_multiplier = 1.0
        self.__enemies_spawned = 0
