"""
Spawn Manager Module
Mengelola spawn enemy dan boss.
"""
import pygame
from random import choice, randint
from settings import ENEMY_SPAWN_INTERVAL, ENEMY_SPAWN_DISTANCE

# Konstanta spawn
BOSS_SPAWN_INTERVAL = 180  # Spawn boss setiap 180 detik (3 menit)
BOSS_SEQUENCE = ['glitchslime', 'dinointernet', 'burnout', 'evilpaper', 'procrastinatemonster']


class SpawnManager:
    """Mengelola spawn enemy dan boss dengan difficulty scaling."""
    
    def __init__(self, spawn_positions, enemy_frames, pathfinder, map_width: int, map_height: int): 
        self.__spawn_positions = spawn_positions
        self.__enemy_frames = enemy_frames
        self.__pathfinder = pathfinder 
        self.map_width = map_width
        self.map_height = map_height
        
        # Timer dan difficulty
        self.__spawn_interval = ENEMY_SPAWN_INTERVAL
        self.__last_spawn_time = pygame.time.get_ticks()
        self.__difficulty_multiplier = 1.0
        self.__enemies_spawned = 0
        
        # Logic boss
        self.__boss_wave_counter = 1
        self.__spawn_boss_next = False
    
    @property
    def difficulty_multiplier(self) -> float:
        return self.__difficulty_multiplier
    
    @property
    def enemies_spawned(self) -> int:
        return self.__enemies_spawned
    
    def update_difficulty(self, elapsed_time: float) -> None:
        """
        Update difficulty berdasarkan waktu (dalam detik).
        Setiap 30 detik: +20% kesulitan, kurangi interval spawn.
        """
        # Scaling kesulitan
        self.__difficulty_multiplier = 1.0 + (elapsed_time // 30) * 0.2
        
        # Kurangi interval spawn (minimum 200ms)
        reduction = int(elapsed_time * 5)
        self.__spawn_interval = max(200, ENEMY_SPAWN_INTERVAL - reduction)
        
        # Cek spawn boss
        if elapsed_time > self.__boss_wave_counter * BOSS_SPAWN_INTERVAL:
            self.__spawn_boss_next = True
            self.__boss_wave_counter += 1
    
    def should_spawn(self) -> bool:
        """Cek apakah waktunya spawn enemy."""
        current_time = pygame.time.get_ticks()
        
        # Boss langsung spawn tanpa menunggu interval
        if self.__spawn_boss_next:
            return True
            
        if current_time - self.__last_spawn_time >= self.__spawn_interval:
            self.__last_spawn_time = current_time
            return True
        return False
    
    def spawn_enemy(self, groups, player, collision_sprites, enemy_factory):
        """Spawn enemy atau boss di posisi random yang valid."""
        player_pos = pygame.Vector2(player.rect.center)
        spawn_pos = None
        
        is_boss_spawn = self.__spawn_boss_next
        
        # Boss: padding lebih besar dari edge
        edge_padding = 100 if is_boss_spawn else 50
        check_size = 192 if is_boss_spawn else 64
        half_size = check_size // 2
        max_attempts = 15 if is_boss_spawn else 10
        
        # Cari posisi spawn yang valid
        for _ in range(max_attempts):
            x = randint(edge_padding, self.map_width - edge_padding)
            y = randint(edge_padding, self.map_height - edge_padding)
            pos = pygame.Vector2(x, y)
            
            # Cek jarak dari player
            min_distance = ENEMY_SPAWN_DISTANCE * 1.5 if is_boss_spawn else ENEMY_SPAWN_DISTANCE
            if (pos - player_pos).length() < min_distance:
                continue
                
            # Cek collision
            dummy_rect = pygame.Rect(x - half_size, y - half_size, check_size, check_size)
            collision = False
            for sprite in collision_sprites:
                if sprite.rect.colliderect(dummy_rect):
                    collision = True
                    break
            
            if not collision:
                spawn_pos = pos
                break
        
        if spawn_pos and self.__enemy_frames:
            enemy_types = list(self.__enemy_frames.keys())
            if not enemy_types: 
                return None
            
            # Tentukan tipe enemy
            is_boss_spawn = False
            if self.__spawn_boss_next:
                is_boss_spawn = True
                self.__spawn_boss_next = False
                
                # Boss spawn berurutan
                boss_index = (self.__boss_wave_counter - 2) % len(BOSS_SEQUENCE)
                chosen_type = BOSS_SEQUENCE[boss_index]
                print(f"BOSS WAVE {self.__boss_wave_counter - 1}: {chosen_type.upper()} muncul!")
            else:
                chosen_type = choice(enemy_types)
            
            # Buat enemy dengan factory
            enemy = enemy_factory.create_enemy(
                chosen_type,
                spawn_pos, 
                self.__enemy_frames,
                groups,
                player,
                collision_sprites,
                self.__pathfinder,
                is_boss=is_boss_spawn,
                difficulty_multiplier=self.__difficulty_multiplier
            )
            
            self.__enemies_spawned += 1
            return enemy
            
        return None
    
    def reset(self) -> None:
        """Reset spawn manager ke kondisi awal."""
        self.__last_spawn_time = pygame.time.get_ticks()
        self.__difficulty_multiplier = 1.0
        self.__enemies_spawned = 0
        self.__boss_wave_counter = 1
        self.__spawn_boss_next = False