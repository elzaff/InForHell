"""
SPRITES MODULE
Implementasi sprites untuk game objects: Sprite, CollisionSprite, Gun, Bullet, Enemies
Menggunakan inheritance dan abstraction sesuai OOP principles
"""
from settings import * 
from math import atan2, degrees, sin, cos
from abc import ABC, abstractmethod
import random


# ==================== BASIC SPRITES ====================

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        # player connection 
        self.player = player 
        self.distance = 140
        self.player_direction = pygame.Vector2(0,1)

        # sprite setup 
        super().__init__(groups)
        self.gun_surf = pygame.image.load(join('images', 'gun', 'gun.png')).convert_alpha()
        self.image = self.gun_surf
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)
    
    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()

    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups, damage=10):
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_frect(center = pos)
        
        # Private attributes
        self.__spawn_time = pygame.time.get_ticks()
        self.__lifetime = BULLET_LIFETIME
        self.__direction = direction 
        self.__speed = BULLET_SPEED
        self.__damage = damage
    
    @property
    def damage(self):
        return self.__damage
    
    def update(self, dt):
        self.rect.center += self.__direction * self.__speed * dt

        if pygame.time.get_ticks() - self.__spawn_time >= self.__lifetime:
            self.kill()

# ==================== BASE ENEMY CLASS ====================

class Enemy(pygame.sprite.Sprite, ABC):
    """Abstract base class untuk semua enemy"""
    
    def __init__(self, pos, frames, groups, player, collision_sprites, 
                 health, speed, damage, exp_value):
        super().__init__(groups)
        
        # References
        self._player = player
        self._collision_sprites = collision_sprites
        
        # Graphics
        self._frames = frames
        self._frame_index = 0 
        self.image = self._frames[self._frame_index]
        self._animation_speed = 6
        
        # Position
        self.rect = self.image.get_frect(center = pos)
        self._hitbox_rect = self.rect.inflate(-20, -40)
        self._direction = pygame.Vector2()
        
        # Private stats
        self.__max_health = health
        self.__current_health = health
        self.__speed = speed
        self.__damage = damage
        self.__exp_value = exp_value
        
        # State
        self.__is_dead = False
        self.__death_time = 0
        self.__death_duration = 400
        self.__exp_given = False  # Flag untuk memastikan EXP hanya diberikan sekali
    
    # Getters
    @property
    def damage(self):
        return self.__damage
    
    @property
    def exp_value(self):
        return self.__exp_value
    
    @property
    def is_dead(self):
        return self.__is_dead
    
    @property
    def exp_given(self):
        return self.__exp_given
    
    @property
    def health_percentage(self):
        return self.__current_health / self.__max_health
    
    def take_damage(self, damage: int) -> bool:
        """Enemy menerima damage, return True jika baru mati"""
        if not self.__is_dead:
            self.__current_health -= damage
            if self.__current_health <= 0:
                self.destroy()
                return True  # Baru mati
        return False  # Sudah mati sebelumnya atau masih hidup
    
    def animate(self, dt):
        """Animate enemy sprite"""
        self._frame_index += self._animation_speed * dt
        self.image = self._frames[int(self._frame_index) % len(self._frames)]
    
    @abstractmethod
    def _calculate_direction(self):
        """Abstract method untuk menghitung arah movement"""
        pass
    
    def move(self, dt):
        """Move enemy berdasarkan direction"""
        self._calculate_direction()
        
        # Update position with collision
        self._hitbox_rect.x += self._direction.x * self.__speed * dt
        self._collision('horizontal')
        self._hitbox_rect.y += self._direction.y * self.__speed * dt
        self._collision('vertical')
        self.rect.center = self._hitbox_rect.center
    
    def _collision(self, direction):
        """Handle collision dengan obstacle"""
        for sprite in self._collision_sprites:
            if sprite.rect.colliderect(self._hitbox_rect):
                if direction == 'horizontal':
                    if self._direction.x > 0: 
                        self._hitbox_rect.right = sprite.rect.left
                    if self._direction.x < 0: 
                        self._hitbox_rect.left = sprite.rect.right
                else:
                    if self._direction.y < 0: 
                        self._hitbox_rect.top = sprite.rect.bottom
                    if self._direction.y > 0: 
                        self._hitbox_rect.bottom = sprite.rect.top
    
    def destroy(self):
        """Mark enemy as dead"""
        self.__is_dead = True
        self.__death_time = pygame.time.get_ticks()
        
        # Change image to death effect
        surf = pygame.mask.from_surface(self._frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf
    
    def give_exp_reward(self):
        """Mark bahwa EXP sudah diberikan dan return exp value"""
        if not self.__exp_given:
            self.__exp_given = True
            return self.__exp_value
        return 0
    
    def _death_timer(self):
        """Handle death animation timer"""
        if pygame.time.get_ticks() - self.__death_time >= self.__death_duration:
            self.kill()
    
    def update(self, dt):
        if not self.__is_dead:
            self.move(dt)
            self.animate(dt)
        else:
            self._death_timer()


# ==================== CONCRETE ENEMY IMPLEMENTATIONS ====================

class BasicEnemy(Enemy):
    """Enemy dasar yang langsung mengejar player"""
    
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(
            pos, frames, groups, player, collision_sprites,
            health=50,
            speed=150,
            damage=10,
            exp_value=10
        )
    
    def _calculate_direction(self):
        """Langsung mengejar player"""
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self._direction = (player_pos - enemy_pos).normalize()


class FastEnemy(Enemy):
    """Enemy cepat dengan HP rendah"""
    
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(
            pos, frames, groups, player, collision_sprites,
            health=30,
            speed=250,
            damage=15,
            exp_value=15
        )
    
    def _calculate_direction(self):
        """Cepat mengejar player"""
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self._direction = (player_pos - enemy_pos).normalize()


class TankEnemy(Enemy):
    """Enemy lambat dengan HP tinggi"""
    
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(
            pos, frames, groups, player, collision_sprites,
            health=150,
            speed=80,
            damage=25,
            exp_value=25
        )
    
    def _calculate_direction(self):
        """Lambat tapi tanky"""
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self._direction = (player_pos - enemy_pos).normalize()


class ZigzagEnemy(Enemy):
    """Enemy yang bergerak zigzag"""
    
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(
            pos, frames, groups, player, collision_sprites,
            health=40,
            speed=180,
            damage=12,
            exp_value=20
        )
        self.__zigzag_timer = 0
        self.__zigzag_offset = pygame.Vector2()
    
    def _calculate_direction(self):
        """Gerak zigzag menuju player"""
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        
        # Base direction ke player
        base_direction = (player_pos - enemy_pos).normalize()
        
        # Add zigzag perpendicular movement
        self.__zigzag_timer += 0.1
        perpendicular = pygame.Vector2(-base_direction.y, base_direction.x)
        zigzag_amount = 0.5
        self.__zigzag_offset = perpendicular * sin(self.__zigzag_timer) * zigzag_amount
        
        self._direction = (base_direction + self.__zigzag_offset).normalize()


class CirclingEnemy(Enemy):
    """Enemy yang bergerak melingkar di sekitar player"""
    
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(
            pos, frames, groups, player, collision_sprites,
            health=60,
            speed=200,
            damage=18,
            exp_value=30
        )
        self.__circle_angle = random.uniform(0, 360)
        self.__circle_radius = 200
    
    def _calculate_direction(self):
        """Bergerak melingkar di radius tertentu dari player"""
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        
        # Get distance to player
        to_player = player_pos - enemy_pos
        distance = to_player.length()
        
        # If too close or too far, move towards optimal radius
        if distance < self.__circle_radius - 50:
            # Move away
            self._direction = -to_player.normalize()
        elif distance > self.__circle_radius + 50:
            # Move closer
            self._direction = to_player.normalize()
        else:
            # Circle around
            self.__circle_angle += 2
            perpendicular = pygame.Vector2(-to_player.y, to_player.x).normalize()
            self._direction = perpendicular


# ==================== ENEMY FACTORY ====================

class EnemyFactory:
    """Factory pattern untuk spawn enemy"""
    
    ENEMY_TYPES = {
        'basic': BasicEnemy,
        'fast': FastEnemy,
        'tank': TankEnemy,
        'zigzag': ZigzagEnemy,
        'circling': CirclingEnemy
    }
    
    @staticmethod
    def create_enemy(enemy_type: str, pos, frames, groups, player, collision_sprites):
        """Create enemy berdasarkan type"""
        enemy_class = EnemyFactory.ENEMY_TYPES.get(enemy_type, BasicEnemy)
        return enemy_class(pos, frames, groups, player, collision_sprites)
    
    @staticmethod
    def create_random_enemy(pos, frames_dict, groups, player, collision_sprites):
        """Create random enemy type"""
        enemy_type = random.choice(list(EnemyFactory.ENEMY_TYPES.keys()))
        frames = frames_dict[random.choice(list(frames_dict.keys()))]
        return EnemyFactory.create_enemy(enemy_type, pos, frames, groups, player, collision_sprites)