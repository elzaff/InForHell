"""
ENEMIES MODULE
Implementasi class Enemy dan variannya.
Memisahkan logika musuh dari sprites.py untuk modularitas yang lebih baik.
"""
from settings import *
from sprites import CollisionSprite
import pygame
from abc import ABC, abstractmethod
import random
from math import sin

# ==================== BASE ENEMY CLASS ====================

class Enemy(pygame.sprite.Sprite, ABC):
    """
    Abstract Base Class untuk semua musuh (Enemy).
    Mengatur movement, animasi, health, dan collision.
    """
    
    def __init__(self, pos: tuple[int, int], frames: list[pygame.Surface], groups: tuple[pygame.sprite.Group, ...], 
                 player: pygame.sprite.Sprite, collision_sprites: pygame.sprite.Group, 
                 health: int, speed: int, damage: int, exp_value: int):
        super().__init__(groups)
        
        # Referensi ke objek lain
        self._player = player
        self._collision_sprites = collision_sprites
        
        # Grafik dan Animasi
        self._frames = frames
        self._frame_index = 0.0
        self.image = self._frames[int(self._frame_index)]
        self._animation_speed = 6
        
        # Posisi dan Hitbox
        self.rect = self.image.get_frect(center = pos)
        self._hitbox_rect = self.rect.inflate(-20, -40)
        self._direction = pygame.Vector2()
        
        # Statistik (Encapsulated)
        self.__max_health = health
        self.__current_health = health
        self.__speed = speed
        self.__damage = damage
        self.__exp_value = exp_value
        
        # Status
        self.__is_dead = False
        self.__death_time = 0
        self.__death_duration = 400
        self.__exp_given = False  # Flag untuk memastikan EXP hanya diberikan sekali
    
    # Properties (Getters)
    @property
    def damage(self) -> int:
        """Mengembalikan damage musuh"""
        return self.__damage
    
    @property
    def exp_value(self) -> int:
        """Mengembalikan nilai EXP musuh"""
        return self.__exp_value
    
    @property
    def is_dead(self) -> bool:
        """Mengecek apakah musuh sudah mati"""
        return self.__is_dead
    
    @property
    def exp_given(self) -> bool:
        """Mengecek apakah EXP sudah diberikan"""
        return self.__exp_given
    
    @property
    def health_percentage(self) -> float:
        """Mengembalikan persentase HP saat ini"""
        return self.__current_health / self.__max_health if self.__max_health > 0 else 0
    
    def take_damage(self, damage: int) -> bool:
        """
        Musuh menerima damage.
        Returns: True jika musuh BARU SAJA mati akibat damage ini.
        """
        if not self.__is_dead:
            self.__current_health -= damage
            if self.__current_health <= 0:
                self.destroy()
                return True  # Baru mati
        return False  # Sudah mati sebelumnya atau masih hidup
    
    def animate(self, dt: float) -> None:
        """Mengupdate animasi sprite musuh"""
        self._frame_index += self._animation_speed * dt
        self.image = self._frames[int(self._frame_index) % len(self._frames)]
    
    @abstractmethod
    def _calculate_direction(self) -> None:
        """
        Method abstrak untuk menghitung arah pergerakan.
        Harus diimplementasikan oleh subclass.
        """
        pass
    
    def move(self, dt: float) -> None:
        """Menggerakkan musuh berdasarkan arah yang dihitung"""
        self._calculate_direction()
        
        # Update posisi dengan collision detection
        self._hitbox_rect.x += self._direction.x * self.__speed * dt
        self._collision('horizontal')
        self._hitbox_rect.y += self._direction.y * self.__speed * dt
        self._collision('vertical')
        self.rect.center = self._hitbox_rect.center
    
    def _collision(self, direction: str) -> None:
        """Menangani collision dengan obstacle"""
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
    
    def destroy(self) -> None:
        """Menandai musuh sebagai mati dan memulai animasi kematian"""
        self.__is_dead = True
        self.__death_time = pygame.time.get_ticks()
        
        # Ubah gambar menjadi efek kematian (siluet putih/mask)
        surf = pygame.mask.from_surface(self._frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf
    
    def give_exp_reward(self) -> int:
        """
        Memberikan reward EXP.
        Returns: Nilai EXP jika belum diberikan, 0 jika sudah.
        """
        if not self.__exp_given:
            self.__exp_given = True
            return self.__exp_value
        return 0
    
    def _death_timer(self) -> None:
        """Menangani timer animasi kematian sebelum sprite dihapus"""
        if pygame.time.get_ticks() - self.__death_time >= self.__death_duration:
            self.kill()
    
    def update(self, dt: float) -> None:
        """Update logic musuh setiap frame"""
        if not self.__is_dead:
            self.move(dt)
            self.animate(dt)
        else:
            self._death_timer()


# ==================== CONCRETE ENEMY IMPLEMENTATIONS ====================

class BasicEnemy(Enemy):
    """Musuh dasar yang bergerak lurus mengejar player"""
    
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(
            pos, frames, groups, player, collision_sprites,
            health=50,
            speed=150,
            damage=10,
            exp_value=10
        )
    
    def _calculate_direction(self) -> None:
        """Menghitung arah langsung ke player"""
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        if (player_pos - enemy_pos).length() > 0:
            self._direction = (player_pos - enemy_pos).normalize()
        else:
            self._direction = pygame.Vector2()


class FastEnemy(Enemy):
    """Musuh cepat dengan HP rendah"""
    
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(
            pos, frames, groups, player, collision_sprites,
            health=30,
            speed=250,
            damage=15,
            exp_value=15
        )
    
    def _calculate_direction(self) -> None:
        """Menghitung arah langsung ke player dengan cepat"""
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        if (player_pos - enemy_pos).length() > 0:
            self._direction = (player_pos - enemy_pos).normalize()
        else:
            self._direction = pygame.Vector2()


class TankEnemy(Enemy):
    """Musuh lambat dengan HP tinggi"""
    
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(
            pos, frames, groups, player, collision_sprites,
            health=150,
            speed=80,
            damage=25,
            exp_value=25
        )
    
    def _calculate_direction(self) -> None:
        """Menghitung arah langsung ke player"""
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        if (player_pos - enemy_pos).length() > 0:
            self._direction = (player_pos - enemy_pos).normalize()
        else:
            self._direction = pygame.Vector2()


class ZigzagEnemy(Enemy):
    """Musuh yang bergerak dengan pola zigzag"""
    
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(
            pos, frames, groups, player, collision_sprites,
            health=40,
            speed=180,
            damage=12,
            exp_value=20
        )
        self.__zigzag_timer = 0.0
        self.__zigzag_offset = pygame.Vector2()
    
    def _calculate_direction(self) -> None:
        """Menghitung arah zigzag menuju player"""
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        
        # Arah dasar ke player
        if (player_pos - enemy_pos).length() > 0:
            base_direction = (player_pos - enemy_pos).normalize()
        else:
            base_direction = pygame.Vector2()
        
        # Tambahkan gerakan tegak lurus (zigzag)
        self.__zigzag_timer += 0.1
        perpendicular = pygame.Vector2(-base_direction.y, base_direction.x)
        zigzag_amount = 0.5
        self.__zigzag_offset = perpendicular * sin(self.__zigzag_timer) * zigzag_amount
        
        if (base_direction + self.__zigzag_offset).length() > 0:
            self._direction = (base_direction + self.__zigzag_offset).normalize()
        else:
            self._direction = base_direction


class CirclingEnemy(Enemy):
    """Musuh yang bergerak melingkar di sekitar player"""
    
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
    
    def _calculate_direction(self) -> None:
        """Menghitung arah untuk menjaga jarak radius tertentu dari player"""
        player_pos = pygame.Vector2(self._player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        
        # Jarak ke player
        to_player = player_pos - enemy_pos
        distance = to_player.length()
        
        if distance == 0:
            self._direction = pygame.Vector2(1, 0)
            return

        # Jika terlalu dekat atau terlalu jauh, sesuaikan
        if distance < self.__circle_radius - 50:
            # Menjauh
            self._direction = -to_player.normalize()
        elif distance > self.__circle_radius + 50:
            # Mendekat
            self._direction = to_player.normalize()
        else:
            # Melingkar (tegak lurus terhadap arah ke player)
            self.__circle_angle += 2
            perpendicular = pygame.Vector2(-to_player.y, to_player.x).normalize()
            self._direction = perpendicular


# ==================== ENEMY FACTORY ====================

class EnemyFactory:
    """Factory Pattern untuk pembuatan musuh"""
    
    ENEMY_MAPPING = {
        'bat': BasicEnemy,
        'blob': TankEnemy,
        'skeleton': FastEnemy
    }
    
    @staticmethod
    def create_enemy(enemy_type: str, pos: tuple[int, int], frames_dict: dict, 
                     groups: tuple[pygame.sprite.Group, ...], player: pygame.sprite.Sprite, 
                     collision_sprites: pygame.sprite.Group) -> Enemy:
        """Membuat instance musuh berdasarkan tipe"""
        enemy_class = EnemyFactory.ENEMY_MAPPING.get(enemy_type, BasicEnemy)
        
        # Ambil frames yang sesuai dengan tipe musuh
        # Jika tidak ada, pakai yang pertama tersedia
        frames = frames_dict.get(enemy_type)
        if not frames:
            frames = list(frames_dict.values())[0]
            
        return enemy_class(pos, frames, groups, player, collision_sprites)
    
    @staticmethod
    def create_random_enemy(pos: tuple[int, int], frames_dict: dict, groups: tuple[pygame.sprite.Group, ...], 
                            player: pygame.sprite.Sprite, collision_sprites: pygame.sprite.Group) -> Enemy:
        """Membuat musuh dengan tipe acak"""
        enemy_type = random.choice(list(EnemyFactory.ENEMY_MAPPING.keys()))
        return EnemyFactory.create_enemy(enemy_type, pos, frames_dict, groups, player, collision_sprites)
