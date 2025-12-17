"""
SPAWN MANAGER MODULE
Updated: Added Boss Spawn Logic + Random Spawn Position
"""
import pygame
from random import choice, randint
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
                 pathfinder, map_width: int, map_height: int): 
                 
        self.__spawn_positions = spawn_positions
        self.__enemy_frames = enemy_frames
        self.__pathfinder = pathfinder 
        self.map_width = map_width
        self.map_height = map_height
        
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
        Setiap 30 detik: +20% kesulitan, kurangi interval spawn.
        """
        # 1. Scaling Kesulitan Musuh Biasa
        self.__difficulty_multiplier = 1.0 + (elapsed_time // 30) * 0.2
        
        # Kurangi interval spawn (Makin lama makin cepat spawnnya)
        # Batas minimum 200ms
        reduction = int(elapsed_time * 5)
        self.__spawn_interval = max(200, ENEMY_SPAWN_INTERVAL - reduction)
        
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
        Memunculkan musuh atau Boss dengan random spawn position.
        """
        player_pos = pygame.Vector2(player.rect.center)
        spawn_pos = None
        
        # Coba generate posisi spawn yang valid (maks 10 percobaan)
        for _ in range(10):
            # Generate random position
            x = randint(0, self.map_width)
            y = randint(0, self.map_height)
            pos = pygame.Vector2(x, y)
            
            # Cek jarak dari player
            if (pos - player_pos).length() < ENEMY_SPAWN_DISTANCE:
                continue
                
            # Cek tabrakan dengan collision sprites (tembok, props)
            # Buat dummy rect size kira-kira ukuran musuh (misal 64x64) untuk cek collision
            dummy_rect = pygame.Rect(x - 32, y - 32, 64, 64)
            collision = False
            for sprite in collision_sprites:
                if sprite.rect.colliderect(dummy_rect):
                    collision = True
                    break
            
            if not collision:
                spawn_pos = pos
                break
        
        if spawn_pos and self.__enemy_frames:
            # Pilih tipe musuh
            enemy_types = list(self.__enemy_frames.keys())
            if not enemy_types: 
                return None
            
            chosen_type = choice(enemy_types)
            
            # Cek apakah ini jatahnya Boss?
            is_boss_spawn = False
            if self.__spawn_boss_next:
                is_boss_spawn = True
                self.__spawn_boss_next = False  # Reset flag setelah boss spawn
                print(f"WARNING: BOSS {chosen_type.upper()} APPEARED!")
            
            # Panggil Factory
            enemy = enemy_factory.create_enemy(
                chosen_type,
                spawn_pos, 
                self.__enemy_frames,
                groups,
                player,
                collision_sprites,
                self.__pathfinder,
                is_boss=is_boss_spawn
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