"""
SPAWN MANAGER MODULE
Updated: Added Boss Spawn Logic
"""
import pygame
from random import choice
from typing import List, Tuple, Dict, Any
from settings import ENEMY_SPAWN_INTERVAL, ENEMY_SPAWN_DISTANCE

# Konstanta internal (Bisa dipindah ke settings.py jika mau)
BOSS_SPAWN_INTERVAL = 60  # Detik (Setiap 1 menit ada boss)

class SpawnManager:
    """
    Mengelola kemunculan musuh dan Boss.
    """
    
    def __init__(self, spawn_positions: List[Tuple[int, int]], 
                 enemy_frames: Dict[str, List[pygame.Surface]], 
                 pathfinder): 
                 
        self.__spawn_positions = spawn_positions
        self.__enemy_frames = enemy_frames
        self.__pathfinder = pathfinder 
        
        # Timer & Difficulty
        self.__spawn_interval = ENEMY_SPAWN_INTERVAL
        self.__last_spawn_time = pygame.time.get_ticks()
        self.__difficulty_multiplier = 1.0
        self.__enemies_spawned = 0
        
        # Logic Boss
        self.__boss_wave_counter = 1      # Menghitung ini boss gelombang keberapa
        self.__spawn_boss_next = False    # Flag antrian boss
    
    @property
    def difficulty_multiplier(self) -> float:
        return self.__difficulty_multiplier
    
    @property
    def enemies_spawned(self) -> int:
        return self.__enemies_spawned
    
    def update_difficulty(self, elapsed_time: float) -> None:
        """
        Meningkatkan kesulitan seiring waktu (elapsed_time dalam DETIK).
        """
        # 1. Scaling Kesulitan Musuh Biasa
        # Setiap 30 detik: +20% kesulitan (Stat musuh nanti bisa dikali ini jika mau)
        self.__difficulty_multiplier = 1.0 + (elapsed_time // 30) * 0.2
        
        # Kurangi interval spawn (Makin lama makin cepat spawnnya)
        # Batas minimum 500ms
        self.__spawn_interval = max(500, ENEMY_SPAWN_INTERVAL - int(elapsed_time * 10))
        
        # 2. Cek Waktunya BOSS
        # Jika waktu sekarang melebihi (Counter * 60 detik), waktunya Boss muncul!
        if elapsed_time > self.__boss_wave_counter * BOSS_SPAWN_INTERVAL:
            self.__spawn_boss_next = True   # Tandai spawn berikutnya harus Boss
            self.__boss_wave_counter += 1   # Siapkan target waktu untuk boss berikutnya
    
    def should_spawn(self) -> bool:
        """Cek apakah waktunya memunculkan musuh"""
        current_time = pygame.time.get_ticks()
        
        # Jika ada antrian Boss, segera spawn tanpa menunggu interval biasa!
        if self.__spawn_boss_next:
            return True
            
        if current_time - self.__last_spawn_time >= self.__spawn_interval:
            self.__last_spawn_time = current_time
            return True
        return False
    
    def spawn_enemy(self, groups, player, collision_sprites, enemy_factory):
        """
        Memunculkan musuh atau Boss.
        """
        # 1. Pilih posisi spawn yang valid (jauh dari player)
        player_pos = pygame.Vector2(player.rect.center)
        valid_positions = []
        
        for pos in self.__spawn_positions:
            spawn_pos = pygame.Vector2(pos)
            distance = (spawn_pos - player_pos).length()
            if distance > ENEMY_SPAWN_DISTANCE:
                valid_positions.append(pos)
        
        if valid_positions and self.__enemy_frames:
            spawn_pos = choice(valid_positions)
            
            # 2. Tentukan Jenis Musuh
            enemy_types = list(self.__enemy_frames.keys()) # ['books', 'slime', dll]
            if not enemy_types: return None
            
            chosen_type = choice(enemy_types)
            
            # 3. Cek apakah ini jatahnya Boss?
            is_boss_spawn = False
            if self.__spawn_boss_next:
                is_boss_spawn = True
                self.__spawn_boss_next = False # Reset flag setelah boss spawn
                print(f"WARNING: BOSS {chosen_type.upper()} APPEARED!") # Debug info
            
            # 4. Panggil Factory
            # Note: Pastikan EnemyFactory di enemies.py sudah support parameter is_boss
            enemy = enemy_factory.create_enemy(
                chosen_type,
                spawn_pos, 
                self.__enemy_frames,
                groups,
                player,
                collision_sprites,
                self.__pathfinder,
                is_boss=is_boss_spawn # <--- Flag Penting
            )
            
            self.__enemies_spawned += 1
            return enemy
            
        return None
    
    def reset(self) -> None:
        """Reset spawn manager"""
        self.__last_spawn_time = pygame.time.get_ticks()
        self.__difficulty_multiplier = 1.0
        self.__enemies_spawned = 0
        self.__boss_wave_counter = 1
        self.__spawn_boss_next = False