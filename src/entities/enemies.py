"""
ENEMIES MODULE
Updated: Boss Scaling increased to 10x (GIANT)!
"""
import pygame
from abc import ABC, abstractmethod
import random
from math import sin

# ==================== BASE ENEMY CLASS ====================

class Enemy(pygame.sprite.Sprite, ABC):
    
    def __init__(self, pos: tuple[int, int], frames: list[pygame.Surface], groups: tuple[pygame.sprite.Group, ...], 
                 player: pygame.sprite.Sprite, collision_sprites: pygame.sprite.Group, enemy_sprites: pygame.sprite.Group,
                 pathfinder,
                 health: int, speed: int, damage: int, exp_value: int, is_boss: bool = False):
        super().__init__(groups)
        
        self._player = player
        self._collision_sprites = collision_sprites
        self._enemy_sprites = enemy_sprites
        self.pathfinder = pathfinder
        self.is_boss = is_boss
        
        # Grafik & Scaling
        self._frames = frames
        self._frame_index = 0.0
        
        # --- BOSS SCALING LOGIC (10x VERSION) ---
        if self.is_boss:
            self._frames = [
                pygame.transform.scale(f, (f.get_width() * 10, f.get_height() * 10)) 
                for f in self._frames
            ]
            self._animation_speed = 4 
            
            shrink_x = -100 
            shrink_y = -100
        else:
            self._animation_speed = 6
            shrink_x = -20
            shrink_y = -40
            
        self.image = self._frames[int(self._frame_index)]
        
        # Movement
        self.rect = self.image.get_frect(center = pos)
        self._hitbox_rect = self.rect.inflate(shrink_x, shrink_y)
        
        self._direction = pygame.Vector2()
        
        # --- STATS LOGIC ---
        if self.is_boss:
            self.__max_health = 800     
            self.__current_health = 800
            self.__speed = speed * 0.7
            self.__damage = 25           
            self.__exp_value = exp_value * 20 # Exp banjir
        else:
            self.__max_health = health
            self.__current_health = health
            self.__speed = speed
            self.__damage = damage
            self.__exp_value = exp_value
        
        self.__is_dead = False
        self.__death_time = 0
        self.__death_duration = 400
        self.__exp_given = False

        # Pathfinding timer
        self.path_timer = 0
        self.path_cooldown = 100 if self.is_boss else random.randint(300, 500) 

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
    
    def _get_separation_vector(self) -> pygame.Vector2:
        separation = pygame.Vector2()
        radius = 150 if self.is_boss else 50
        neighbors = [sprite for sprite in self._enemy_sprites if sprite != self and 
                    (pygame.Vector2(sprite.rect.center) - pygame.Vector2(self.rect.center)).length() < radius]
        if neighbors:
            for neighbor in neighbors:
                diff = pygame.Vector2(self.rect.center) - pygame.Vector2(neighbor.rect.center)
                if diff.length() > 0:
                    diff = diff.normalize()
                separation += diff
            separation /= len(neighbors)
        return separation.normalize() if separation.length() > 0 else pygame.Vector2()

    def _calculate_direction(self) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.path_timer > self.path_cooldown:
            self.path_timer = current_time
            start_pos = self.rect.center
            target_pos = self._player.rect.center
            
            if self.is_boss:
                self._direction = self.pathfinder.get_path_astar(start_pos, target_pos)
            else:
                self._direction = self.pathfinder.get_path_bfs(start_pos, target_pos)
                
            if self._direction.magnitude() == 0 and (pygame.Vector2(target_pos) - pygame.Vector2(start_pos)).length() > 0:
                self._direction = (pygame.Vector2(target_pos) - pygame.Vector2(start_pos)).normalize()
    
    def move(self, dt: float) -> None:
        self._calculate_direction()
        separation_force = self._get_separation_vector()
        sep_weight = 0.2 if self.is_boss else 0.5
        final_direction = self._direction + (separation_force * sep_weight) 
        if final_direction.length() > 0:
            final_direction = final_direction.normalize()

        self._hitbox_rect.x += final_direction.x * self.__speed * dt
        self._collision('horizontal')
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


# ==================== ENEMY TYPES ====================

class BasicEnemy(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder, is_boss=False):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder,
                         health=50, speed=150, damage=10, exp_value=10, is_boss=is_boss)

class FastEnemy(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder, is_boss=False):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder,
                         health=30, speed=250, damage=15, exp_value=15, is_boss=is_boss)

class TankEnemy(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder, is_boss=False):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder,
                         health=150, speed=80, damage=25, exp_value=25, is_boss=is_boss)

class ZigzagEnemy(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder, is_boss=False):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder,
                         health=40, speed=180, damage=12, exp_value=20, is_boss=is_boss)
        self.__zigzag_timer = 0.0
    
    def _calculate_direction(self) -> None:
        if self.is_boss:
            super()._calculate_direction()
            return
        super()._calculate_direction()
        self.__zigzag_timer += 0.1
        if self._direction.length() > 0:
            perp = pygame.Vector2(-self._direction.y, self._direction.x)
            offset = perp * sin(self.__zigzag_timer) * 0.5
            self._direction = (self._direction + offset).normalize()


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
                 collision_sprites: pygame.sprite.Group, pathfinder, is_boss: bool = False) -> Enemy:
        enemy_class = EnemyFactory.ENEMY_MAPPING.get(enemy_type, BasicEnemy)
        frames = frames_dict.get(enemy_type)
        if not frames: frames = list(frames_dict.values())[0] if frames_dict else []
        enemy_sprites_group = groups[1]
        return enemy_class(pos, frames, groups, player, collision_sprites, enemy_sprites_group, pathfinder, is_boss)