"""
Enemies Module
Class Enemy sebagai abstract base class dengan concrete subclass untuk setiap tipe enemy.
Menggunakan Pathfinding untuk mengejar player dan Flocking untuk pergerakan natural.
"""
import pygame
from abc import ABC
import random
from src.core.flocking import FlockingBehavior


class Enemy(pygame.sprite.Sprite, ABC):
    """
    Abstract base class untuk semua enemy.
    Menggunakan Pathfinding untuk chase dan Flocking untuk natural movement.
    """
    
    def __init__(self, pos: tuple[int, int], frames: list[pygame.Surface], groups: tuple[pygame.sprite.Group, ...], 
                 player: pygame.sprite.Sprite, collision_sprites: pygame.sprite.Group, enemy_sprites: pygame.sprite.Group,
                 pathfinder,
                 health: int, speed: int, damage: int, exp_value: int, 
                 is_boss: bool = False, difficulty_multiplier: float = 1.0):
        super().__init__(groups)
        
        self._player = player
        self._collision_sprites = collision_sprites
        self._enemy_sprites = enemy_sprites
        self.pathfinder = pathfinder
        self.is_boss = is_boss
        
        # Grafik dan scaling
        self._frames = frames
        self._frame_index = 0.0
        
        # Boss: 5x ukuran sprite
        if self.is_boss:
            self._frames = [
                pygame.transform.scale(f, (f.get_width() * 5, f.get_height() * 5)) 
                for f in self._frames
            ]
            self._animation_speed = 4
            shrink_x = -50
            shrink_y = -50
        else:
            self._animation_speed = 6
            shrink_x = -20
            shrink_y = -40
            
        self.image = self._frames[int(self._frame_index)]
        
        # Movement dan collision
        self.rect = self.image.get_frect(center=pos)
        self._hitbox_rect = self.rect.inflate(shrink_x, shrink_y)
        self._direction = pygame.Vector2()
        
        # Stats dengan difficulty scaling
        scaled_health = int(health * difficulty_multiplier)
        scaled_damage = int(damage * difficulty_multiplier)
        scaled_exp = int(exp_value * difficulty_multiplier)
        
        if self.is_boss:
            # Boss: 8x HP, 0.4x speed, 3x damage, 15x exp
            self.__max_health = scaled_health * 8
            self.__current_health = scaled_health * 8
            self.__speed = speed * 0.4
            self.__damage = scaled_damage * 3
            self.__exp_value = scaled_exp * 15
        else:
            self.__max_health = scaled_health
            self.__current_health = scaled_health
            self.__speed = speed
            self.__damage = scaled_damage
            self.__exp_value = scaled_exp
        
        self.__is_dead = False
        self.__death_time = 0
        self.__death_duration = 400
        self.__exp_given = False

        # Pathfinding timer
        self.path_timer = 0
        self.path_cooldown = 150 if self.is_boss else random.randint(300, 500)
        
        # Flocking behavior
        self.flocking = FlockingBehavior(
            enemy=self,
            enemy_sprites=enemy_sprites,
            perception_radius=100 if not is_boss else 150,
            separation_weight=1.5,
            alignment_weight=1.0,
            cohesion_weight=0.8
        )
        self.use_flocking = True

    # Properties
    @property
    def damage(self) -> int: 
        return self.__damage
    
    @property
    def exp_value(self) -> int: 
        return self.__exp_value
    
    @property
    def is_dead(self) -> bool: 
        return self.__is_dead
    
    @property
    def exp_given(self) -> bool: 
        return self.__exp_given
    
    @property
    def health_percentage(self) -> float: 
        return self.__current_health / self.__max_health if self.__max_health > 0 else 0
    
    def take_damage(self, damage: int) -> bool:
        """Menerima damage. Return True jika mati."""
        if not self.__is_dead:
            self.__current_health -= damage
            if self.__current_health <= 0:
                self.destroy()
                return True
        return False
    
    def animate(self, dt: float) -> None:
        """Animasi sprite enemy."""
        self._frame_index += self._animation_speed * dt
        self.image = self._frames[int(self._frame_index) % len(self._frames)]
    
    def _calculate_direction(self) -> None:
        """Hitung arah ke player menggunakan pathfinding."""
        current_time = pygame.time.get_ticks()
        start_pos = self.rect.center
        target_pos = self._player.rect.center
        
        # Direct direction sebagai fallback
        diff = pygame.Vector2(target_pos) - pygame.Vector2(start_pos)
        direct_direction = diff.normalize() if diff.length() > 0 else pygame.Vector2()
        
        # Pathfinding setiap cooldown
        if current_time - self.path_timer > self.path_cooldown:
            self.path_timer = current_time
            
            if self.is_boss:
                pathfind_result = self.pathfinder.get_path_astar(start_pos, target_pos)
            else:
                pathfind_result = self.pathfinder.get_path_bfs(start_pos, target_pos)
            
            if pathfind_result.magnitude() > 0:
                self._direction = pathfind_result
            else:
                self._direction = direct_direction
        
        if self._direction.magnitude() == 0:
            self._direction = direct_direction
    
    def _calculate_flocking_force(self) -> pygame.Vector2:
        """Hitung flocking force dari enemy sekitar."""
        if not self.use_flocking:
            return pygame.Vector2()
        return self.flocking.calculate()
    
    def move(self, dt: float) -> None:
        """Movement dengan pathfinding + flocking."""
        self._calculate_direction()
        flocking_force = self._calculate_flocking_force()
        
        # Bobot: 70% pathfinding, 30% flocking (10% untuk boss)
        pathfinding_weight = 0.7
        flocking_weight = 0.3 if not self.is_boss else 0.1
        
        final_direction = (self._direction * pathfinding_weight) + (flocking_force * flocking_weight)
        
        if final_direction.length() > 0:
            final_direction = final_direction.normalize()

        self._hitbox_rect.x += final_direction.x * self.__speed * dt
        self._collision('horizontal')
        self._hitbox_rect.y += final_direction.y * self.__speed * dt
        self._collision('vertical')
        self.rect.center = self._hitbox_rect.center
    
    def _collision(self, direction: str) -> None:
        """Handle collision dengan obstacle."""
        for sprite in self._collision_sprites:
            if sprite.rect.colliderect(self._hitbox_rect):
                if direction == 'horizontal':
                    if self._direction.x > 0: self._hitbox_rect.right = sprite.rect.left
                    if self._direction.x < 0: self._hitbox_rect.left = sprite.rect.right
                else:
                    if self._direction.y < 0: self._hitbox_rect.top = sprite.rect.bottom
                    if self._direction.y > 0: self._hitbox_rect.bottom = sprite.rect.top

    def destroy(self) -> None:
        """Menandai enemy sebagai mati."""
        self.__is_dead = True
        self.__death_time = pygame.time.get_ticks()
        surf = pygame.mask.from_surface(self._frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf
    
    def give_exp_reward(self) -> int:
        """Memberikan exp reward sekali saja."""
        if not self.__exp_given:
            self.__exp_given = True
            return self.__exp_value
        return 0
    
    def _death_timer(self) -> None:
        """Timer untuk death animation."""
        if pygame.time.get_ticks() - self.__death_time >= self.__death_duration:
            self.kill()
    
    def update(self, dt: float) -> None:
        """Update enemy setiap frame."""
        if not self.__is_dead:
            self.move(dt)
            self.animate(dt)
        else:
            self._death_timer()


# Concrete Enemy Classes - Setiap class sesuai dengan nama folder di images/enemies/

class Glitchslime(Enemy):
    """Slime digital yang berglitch, balanced stats."""
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder, 
                 is_boss=False, difficulty_multiplier=1.0):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder,
                         health=50, speed=120, damage=8, exp_value=10, 
                         is_boss=is_boss, difficulty_multiplier=difficulty_multiplier)
        self.__facing_left = False
    
    def animate(self, dt: float) -> None:
        """Flip sprite berdasarkan arah gerak."""
        self._frame_index += self._animation_speed * dt
        current_frame = self._frames[int(self._frame_index) % len(self._frames)]
        
        if self._direction.x < 0 and not self.__facing_left:
            self.__facing_left = True
        elif self._direction.x > 0 and self.__facing_left:
            self.__facing_left = False
        
        if self.__facing_left:
            self.image = pygame.transform.flip(current_frame, True, False)
        else:
            self.image = current_frame


class Dinointernet(Enemy):
    """Dinosaurus dari era internet mati, sedikit lebih kuat."""
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder, 
                 is_boss=False, difficulty_multiplier=1.0):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder,
                         health=60, speed=130, damage=10, exp_value=12, 
                         is_boss=is_boss, difficulty_multiplier=difficulty_multiplier)
        self.__facing_left = False
    
    def animate(self, dt: float) -> None:
        """Flip sprite berdasarkan arah gerak."""
        self._frame_index += self._animation_speed * dt
        current_frame = self._frames[int(self._frame_index) % len(self._frames)]
        
        if self._direction.x < 0 and not self.__facing_left:
            self.__facing_left = True
        elif self._direction.x > 0 and self.__facing_left:
            self.__facing_left = False
        
        if self.__facing_left:
            self.image = pygame.transform.flip(current_frame, True, False)
        else:
            self.image = current_frame


class Burnout(Enemy):
    """Mahasiswa yang kelelahan, cepat tapi lemah."""
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder, 
                 is_boss=False, difficulty_multiplier=1.0):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder,
                         health=35, speed=200, damage=12, exp_value=15, 
                         is_boss=is_boss, difficulty_multiplier=difficulty_multiplier)
        self.__facing_right = False
    
    def animate(self, dt: float) -> None:
        """Flip sprite berdasarkan arah gerak (flip ke kanan)."""
        self._frame_index += self._animation_speed * dt
        current_frame = self._frames[int(self._frame_index) % len(self._frames)]
        
        if self._direction.x > 0 and not self.__facing_right:
            self.__facing_right = True
        elif self._direction.x < 0 and self.__facing_right:
            self.__facing_right = False
        
        if self.__facing_right:
            self.image = pygame.transform.flip(current_frame, True, False)
        else:
            self.image = current_frame


class Evilpaper(Enemy):
    """Kertas tugas yang menyerang balik, ringan dan cepat."""
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder, 
                 is_boss=False, difficulty_multiplier=1.0):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder,
                         health=40, speed=160, damage=10, exp_value=14, 
                         is_boss=is_boss, difficulty_multiplier=difficulty_multiplier)
        self.__facing_left = False
    
    def animate(self, dt: float) -> None:
        """Flip sprite berdasarkan arah gerak."""
        self._frame_index += self._animation_speed * dt
        current_frame = self._frames[int(self._frame_index) % len(self._frames)]
        
        if self._direction.x < 0 and not self.__facing_left:
            self.__facing_left = True
        elif self._direction.x > 0 and self.__facing_left:
            self.__facing_left = False
        
        if self.__facing_left:
            self.image = pygame.transform.flip(current_frame, True, False)
        else:
            self.image = current_frame


class Procrastinatemonster(Enemy):
    """Monster prokrastinasi, tank lambat tapi kuat."""
    def __init__(self, pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder, 
                 is_boss=False, difficulty_multiplier=1.0):
        super().__init__(pos, frames, groups, player, collision_sprites, enemy_sprites, pathfinder,
                         health=120, speed=100, damage=20, exp_value=25, 
                         is_boss=is_boss, difficulty_multiplier=difficulty_multiplier)
        self.use_flocking = False  # Tank bergerak sendiri
        self.__facing_left = False
    
    def animate(self, dt: float) -> None:
        """Flip sprite berdasarkan arah gerak."""
        self._frame_index += self._animation_speed * dt
        current_frame = self._frames[int(self._frame_index) % len(self._frames)]
        
        if self._direction.x < 0 and not self.__facing_left:
            self.__facing_left = True
        elif self._direction.x > 0 and self.__facing_left:
            self.__facing_left = False
        
        if self.__facing_left:
            self.image = pygame.transform.flip(current_frame, True, False)
        else:
            self.image = current_frame


class EnemyFactory:
    """Factory pattern untuk membuat enemy berdasarkan tipe."""
    
    ENEMY_MAPPING = {
        'glitchslime': Glitchslime,
        'dinointernet': Dinointernet,
        'burnout': Burnout,
        'evilpaper': Evilpaper,
        'procrastinatemonster': Procrastinatemonster,
    }
    
    @staticmethod
    def create_enemy(enemy_type: str, pos: tuple[int, int], frames_dict: dict, 
                     groups: tuple[pygame.sprite.Group, ...], player: pygame.sprite.Sprite, 
                     collision_sprites: pygame.sprite.Group, pathfinder, 
                     is_boss: bool = False, difficulty_multiplier: float = 1.0) -> Enemy:
        """
        Membuat instance enemy sesuai tipe menggunakan polymorphism.
        Return abstract Enemy, actual object adalah concrete subclass.
        """
        enemy_class = EnemyFactory.ENEMY_MAPPING.get(enemy_type, Glitchslime)
        frames = frames_dict.get(enemy_type)
        if not frames:
            frames = list(frames_dict.values())[0] if frames_dict else []
        enemy_sprites_group = groups[1]
        return enemy_class(pos, frames, groups, player, collision_sprites, enemy_sprites_group, 
                          pathfinder, is_boss, difficulty_multiplier)
