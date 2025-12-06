"""
ENEMIES MODULE
Updated: Added Separation Logic (Swarm AI)
"""
import pygame
from abc import ABC, abstractmethod
import random
from math import sin


# ==================== BASE ENEMY CLASS ====================

class Enemy(pygame.sprite.Sprite, ABC):
    
    # UPDATE: Tambah parameter 'enemy_sprites'
    def __init__(self, pos: tuple[int, int], frames: list[pygame.Surface], groups: tuple[pygame.sprite.Group, ...], 
                 player: pygame.sprite.Sprite, collision_sprites: pygame.sprite.Group, enemy_sprites: pygame.sprite.Group,
                 health: int, speed: int, damage: int, exp_value: int):
        super().__init__(groups)
        
        self._player = player
        self._collision_sprites = collision_sprites
        self._enemy_sprites = enemy_sprites  # Simpan referensi ke grup musuh
        
        # Grafik
        self._frames = frames
        self._frame_index = 0.0
        self.image = self._frames[int(self._frame_index)]
        self._animation_speed = 6
        
        # Movement
        self.rect = self.image.get_frect(center = pos)
        self._hitbox_rect = self.rect.inflate(-20, -40)
        self._direction = pygame.Vector2()
        
        # Stats
        self.__max_health = health
        self.__current_health = health
        self.__speed = speed
        self.__damage = damage
        self.__exp_value = exp_value
        
        self.__is_dead = False
        self.__death_time = 0
        self.__death_duration = 400
        self.__exp_given = False

    @property
    def damage(self) -> int: return self.__damage
    @property
    def exp_value(self) -> int: return self.__exp_value
    @property
    def is_dead(self) -> bool: return self.__is_dead
    @property
    def exp_given(self) -> bool: return self.__exp_given
    @property
    def health_percentage(self) -> float: return self.__current_health / self.__max_health if self.__max_health > 0 else 0
    
    def take_damage(self, damage: int) -> bool:
        if not self.__is_dead:
            self.__current_health -= damage
            if self.__current_health <= 0:
                self.destroy()
                return True
        return False
    
    def animate(self, dt: float) -> None:
        self._frame_index += self._animation_speed * dt
        self.image = self._frames[int(self._frame_index) % len(self._frames)]
    
    # SEPARATION (Biar gak numpuk & stuck) 
    def _get_separation_vector(self) -> pygame.Vector2:
        separation = pygame.Vector2()
        # Cari musuh lain di sekitar (radius 50 pixel)
        # Note: Ini agak berat kalau musuh 500+, tapi untuk <100 masih aman
        neighbors = [sprite for sprite in self._enemy_sprites if sprite != self and 
                    (pygame.Vector2(sprite.rect.center) - pygame.Vector2(self.rect.center)).length() < 50]
        
        if neighbors:
            for neighbor in neighbors:
                diff = pygame.Vector2(self.rect.center) - pygame.Vector2(neighbor.rect.center)
                if diff.length() > 0:
                    diff = diff.normalize()
                separation += diff
            
            separation /= len(neighbors)
        
        return separation.normalize() if separation.length() > 0 else pygame.Vector2()

    @abstractmethod
    def _calculate_direction(self) -> None:
        pass
    
    def move(self, dt: float) -> None:
        self._calculate_direction()
        separation_force = self._get_separation_vector()
        
        # Rumus: 80% Kejar Player, 20% Hindari Teman
        # Ini bikin efek "cair", jadi kalau stuck, dia didorong temannya ke samping
        final_direction = self._direction + (separation_force * 0.5) 
        
        if final_direction.length() > 0:
            final_direction = final_direction.normalize()

        # Update posisi X
        self._hitbox_rect.x += final_direction.x * self.__speed * dt
        self._collision('horizontal')
        # Update posisi Y
        self._hitbox_rect.y += final_direction.y * self.__speed * dt
        self._collision('vertical')
        
        self.rect.center = self._hitbox_rect.center
    
    def _collision(self, direction: str) -> None:
        for sprite in self._collision_sprites:
            if sprite.rect.colliderect(self._hitbox_rect):
                if direction == 'horizontal':
                    if self._direction.x > 0: self._hitbox_rect.right = sprite.rect.left
                    if self._direction.x < 0: self._hitbox_rect.left = sprite.rect.right
                else:
                    if self._direction.y < 0: self._hitbox_rect.top = sprite.rect.bottom
                    if self._direction.y > 0: self._hitbox_rect.bottom = sprite.rect.top

    def destroy(self) -> None:
        self.__is_dead = True
        self.__death_time = pygame.time.get_ticks()
        surf = pygame.mask.from_surface(self._frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf
    
    def give_exp_reward(self) -> int:
        if not self.__exp_given:
            self.__exp_given = True
            return self.__exp_value
        return 0
    
    def _death_timer(self) -> None:
        if pygame.time.get_ticks() - self.__death_time >= self.__death_duration:
            self.kill()
    
    def update(self, dt: float) -> None:
        if not self.__is_dead:
            self.move(dt)
            self.animate(dt)
        else:
            self._death_timer()


class BasicEnemy(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites, 
                         health=50, speed=150, damage=10, exp_value=10)
    
    def _calculate_direction(self) -> None:
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        if (player_pos - enemy_pos).length() > 0:
            self._direction = (player_pos - enemy_pos).normalize()
        else:
            self._direction = pygame.Vector2()


class FastEnemy(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites,
                         health=30, speed=250, damage=15, exp_value=15)
    
    def _calculate_direction(self) -> None:
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        if (player_pos - enemy_pos).length() > 0:
            self._direction = (player_pos - enemy_pos).normalize()
        else:
            self._direction = pygame.Vector2()


class TankEnemy(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites,
                         health=150, speed=80, damage=25, exp_value=25)
    
    def _calculate_direction(self) -> None:
        current_time = pygame.time.get_ticks()
        if not hasattr(self, 'last_calc_time'):
            self.last_calc_time = 0
            self.cached_direction = pygame.Vector2()
        if current_time - self.last_calc_time > 500:
            if hasattr(self, 'pathfinder'):
                # Tanya jalan ke Pathfinder
                self.cached_direction = self.pathfinder.get_path(self.rect.center, self._player.rect.center)
            else:
                # Fallback kalau pathfinder error
                player_pos = pygame.Vector2(self._player.rect.center)
                enemy_pos = pygame.Vector2(self.rect.center)
                if (player_pos - enemy_pos).length() > 0:
                    self.cached_direction = (player_pos - enemy_pos).normalize()
            
            self.last_calc_time = current_time
        
        self._direction = self.cached_direction


class ZigzagEnemy(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites,
                         health=40, speed=180, damage=12, exp_value=20)
        self.__zigzag_timer = 0.0
        self.__zigzag_offset = pygame.Vector2()
    
    def _calculate_direction(self) -> None:
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        if (player_pos - enemy_pos).length() > 0:
            base = (player_pos - enemy_pos).normalize()
        else:
            base = pygame.Vector2()
            
        self.__zigzag_timer += 0.1
        perp = pygame.Vector2(-base.y, base.x)
        self.__zigzag_offset = perp * sin(self.__zigzag_timer) * 0.5
        
        if (base + self.__zigzag_offset).length() > 0:
            self._direction = (base + self.__zigzag_offset).normalize()
        else:
            self._direction = base


class CirclingEnemy(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites,
                         health=60, speed=200, damage=18, exp_value=30)
        self.__circle_angle = random.uniform(0, 360)
        self.__circle_radius = 200
        
    def _calculate_direction(self) -> None:
        pass 


# ==================== FACTORY ====================

class EnemyFactory:
    ENEMY_MAPPING = {
        'slime': BasicEnemy, 'redblob': BasicEnemy, 'ghost': BasicEnemy,
        'toast': TankEnemy, 'paper': TankEnemy,
        'books': FastEnemy, 'spider': ZigzagEnemy
    }
    
    @staticmethod
    def create_enemy(enemy_type: str, pos: tuple[int, int], frames_dict: dict, 
                 groups: tuple[pygame.sprite.Group, ...], player: pygame.sprite.Sprite, 
                 collision_sprites: pygame.sprite.Group, pathfinder) -> Enemy:
        
        enemy_class = EnemyFactory.ENEMY_MAPPING.get(enemy_type, BasicEnemy)
        frames = frames_dict.get(enemy_type)
        if not frames:
             frames = list(frames_dict.values())[0] if frames_dict else []
    
        enemy_sprites_group = groups[1]
        enemy = enemy_class(pos, frames, groups, player, collision_sprites, enemy_sprites_group)
        enemy.pathfinder = pathfinder
        
        return enemy_class(pos, frames, groups, player, collision_sprites, enemy_sprites_group)

    # create_random_enemy tidak perlu diubah isinya karena dia memanggil create_enemy di atas
    @staticmethod
    def create_random_enemy(pos: tuple[int, int], frames_dict: dict, groups: tuple[pygame.sprite.Group, ...], 
                            player: pygame.sprite.Sprite, collision_sprites: pygame.sprite.Group) -> Enemy:
        available_types = list(frames_dict.keys())
        if available_types:
            enemy_type = random.choice(available_types)
            return EnemyFactory.create_enemy(enemy_type, pos, frames_dict, groups, player, collision_sprites)
        return None
