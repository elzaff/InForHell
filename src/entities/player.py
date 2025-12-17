"""
Player Module
Implementasi Player dengan PlayerStats untuk encapsulation.
"""
import pygame
from os.path import join
from os import walk
from settings import (
    PLAYER_MAX_HEALTH, PLAYER_BASE_DAMAGE, PLAYER_SPEED,
    EXP_BASE, EXP_MULTIPLIER, HEALTH_PER_LEVEL, DAMAGE_PER_LEVEL, SPEED_PER_LEVEL
)


class PlayerStats:
    """Mengelola statistik player."""
    
    def __init__(self):
        self.__max_health = PLAYER_MAX_HEALTH
        self.__current_health = self.__max_health
        self.__base_damage = PLAYER_BASE_DAMAGE
        self.__base_speed = PLAYER_SPEED
        
        # Level dan EXP
        self.__level = 1
        self.__current_exp = 0
        self.__exp_to_next_level = EXP_BASE
        
        # Tracking
        self.__kills = 0
        self.__damage_taken = 0
        self.__is_alive = True
    
    # Properties
    @property
    def max_health(self):
        return self.__max_health
    
    @property
    def current_health(self):
        return self.__current_health
    
    @property
    def base_damage(self):
        return self.__base_damage
    
    @property
    def base_speed(self):
        return self.__base_speed
    
    @property
    def level(self):
        return self.__level
    
    @property
    def current_exp(self):
        return self.__current_exp
    
    @property
    def exp_to_next_level(self):
        return self.__exp_to_next_level
    
    @property
    def kills(self):
        return self.__kills
    
    @property
    def is_alive(self):
        return self.__is_alive
    
    @property
    def health_percentage(self):
        return self.__current_health / self.__max_health
    
    @property
    def exp_percentage(self):
        return self.__current_exp / self.__exp_to_next_level
    
    def take_damage(self, damage: int):
        """Kurangi HP player."""
        self.__current_health = max(0, self.__current_health - damage)
        self.__damage_taken += damage
        if self.__current_health <= 0:
            self.__is_alive = False
    
    def heal(self, amount: int):
        """Heal HP player."""
        self.__current_health = min(self.__max_health, self.__current_health + amount)
    
    def add_exp(self, amount: int) -> bool:
        """Tambah EXP, return True jika level up."""
        self.__current_exp += amount
        if self.__current_exp >= self.__exp_to_next_level:
            self.__level_up()
            return True
        return False
    
    def add_kill(self):
        """Tambah kill count."""
        self.__kills += 1
    
    def increase_max_health(self, amount: int):
        """Tingkatkan max HP dan heal sebesar kenaikan."""
        self.__max_health += amount
        self.__current_health += amount
    
    def decrease_max_health(self, amount: int):
        """Kurangi max HP (untuk upgrade risk/reward)."""
        self.__max_health = max(10, self.__max_health - amount)
        if self.__current_health > self.__max_health:
            self.__current_health = self.__max_health
    
    def increase_damage(self, amount: int):
        """Tingkatkan base damage."""
        self.__base_damage += amount
    
    def increase_speed(self, amount: int):
        """Tingkatkan base speed."""
        self.__base_speed += amount
    
    def __level_up(self):
        """Level up dengan bonus stats."""
        self.__level += 1
        self.__current_exp -= self.__exp_to_next_level
        self.__exp_to_next_level = int(self.__exp_to_next_level * EXP_MULTIPLIER)
        
        # Bonus stats per level
        self.increase_max_health(HEALTH_PER_LEVEL)
        self.increase_damage(DAMAGE_PER_LEVEL)
        self.increase_speed(SPEED_PER_LEVEL)
        
        print(f"Level Up! Lv{self.__level} | +{HEALTH_PER_LEVEL} HP, +{DAMAGE_PER_LEVEL} DMG, +{SPEED_PER_LEVEL} SPD")


class Player(pygame.sprite.Sprite):
    """Class Player dengan movement dan combat."""
    
    def __init__(self, pos, groups, collision_sprites, map_width, map_height):
        super().__init__(groups)
        
        # Batas map
        self.map_width = map_width
        self.map_height = map_height

        # Stats
        self.__stats = PlayerStats()
        self.weapon = None
        self.active_skill = None
        self.collision_sprites = collision_sprites
        
        # Stat modifiers dari upgrade
        self.stat_modifiers = {
            'speed': 1.0,
            'damage': 1.0,
            'cooldown': 1.0,
            'max_health': 1.0
        }
        
        # Multi-shot
        self.multi_shot_count = 1
        
        # Grafik
        self.load_images()
        self.state, self.frame_index = 'down', 0
        self.image = pygame.image.load(join('images', 'player', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-60, -90)
        
        # Movement
        self.direction = pygame.Vector2()
        
        # Timer invulnerability
        self.__is_invulnerable = False
        self.__invulnerable_time = 0
        self.__invulnerable_duration = 500
        
        # Timer dash
        self.__is_dashing = False
        self.__dash_time = 0
        self.__dash_duration = 200
        self.__dash_speed = 0
        
        # Lifesteal dari upgrade
        self.lifesteal_chance = 0.0

    @property
    def stats(self):
        return self.__stats

    @property
    def current_speed(self):
        """Speed dengan modifier."""
        return self.__stats.base_speed * self.stat_modifiers['speed']
    
    @property
    def current_damage(self):
        """Damage dengan modifier."""
        return self.__stats.base_damage * self.stat_modifiers['damage']
    
    def load_images(self):
        """Load sprite animasi."""
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}

        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def input(self):
        """Handle input keyboard."""
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
        
        # Skill input
        if keys[pygame.K_SPACE] or keys[pygame.K_q]:
            if self.active_skill:
                self.active_skill.activate()

    def take_damage(self, damage: int):
        """Player menerima damage dengan invulnerability."""
        if not self.__is_invulnerable:
            self.__stats.take_damage(damage)
            self.__is_invulnerable = True
            self.__invulnerable_time = pygame.time.get_ticks()
    
    def heal(self, amount: int):
        """Heal player."""
        self.__stats.heal(amount)
    
    def gain_exp(self, amount: int):
        """Dapat EXP dan return True jika level up."""
        return self.__stats.add_exp(amount)
    
    def apply_dash(self, speed: int, duration: int):
        """Aktivasi dash."""
        self.__is_dashing = True
        self.__dash_speed = speed
        self.__dash_time = pygame.time.get_ticks()
        self.__dash_duration = duration
    
    def move(self, dt):
        """Movement dengan collision detection."""
        speed = self.__dash_speed if self.__is_dashing else self.current_speed
        
        self.hitbox_rect.x += self.direction.x * speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * speed * dt
        self.collision('vertical')
        
        # Clamp ke batas map
        if self.hitbox_rect.left < 0:
            self.hitbox_rect.left = 0
        if self.hitbox_rect.right > self.map_width:
            self.hitbox_rect.right = self.map_width
        if self.hitbox_rect.top < 0:
            self.hitbox_rect.top = 0
        if self.hitbox_rect.bottom > self.map_height:
            self.hitbox_rect.bottom = self.map_height

        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        """Handle collision dengan obstacle."""
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top

    def animate(self, dt):
        """Animasi sprite berdasarkan arah gerak."""
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        self.frame_index = self.frame_index + 5 * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
        
        # Flash effect saat invulnerable
        if self.__is_invulnerable:
            alpha = 128 if (pygame.time.get_ticks() // 100) % 2 == 0 else 255
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
    
    def update_timers(self):
        """Update timer dash dan invulnerability."""
        current_time = pygame.time.get_ticks()
        
        if self.__is_dashing:
            if current_time - self.__dash_time >= self.__dash_duration:
                self.__is_dashing = False
        
        if self.__is_invulnerable:
            if current_time - self.__invulnerable_time >= self.__invulnerable_duration:
                self.__is_invulnerable = False

    def update(self, dt):
        """Update player setiap frame."""
        if self.__stats.is_alive:
            self.input()
            self.move(dt)
            self.animate(dt)
            self.update_timers()
