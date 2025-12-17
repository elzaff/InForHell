"""
Settings Module
Konfigurasi dan konstanta global untuk game InForHell.
"""

# Pengaturan Layar
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720 
TILE_SIZE = 64
FPS = 60

# Pengaturan Player
PLAYER_SPEED = 300
PLAYER_MAX_HEALTH = 100
PLAYER_BASE_DAMAGE = 10

# Pengaturan Senjata
GUN_COOLDOWN = 200          # Cooldown tembakan dalam ms
BULLET_SPEED = 1200         # Kecepatan peluru
BULLET_LIFETIME = 1000      # Durasi hidup peluru dalam ms

# Pengaturan Enemy
ENEMY_SPAWN_INTERVAL = 2000     # Interval spawn enemy dalam ms
ENEMY_BASE_SPEED = 100          # Kecepatan dasar enemy
ENEMY_SPAWN_DISTANCE = 600      # Jarak spawn dari player

# Pengaturan Level Up
EXP_BASE = 100              # EXP yang dibutuhkan untuk level 1
EXP_MULTIPLIER = 1.5        # Pengali EXP setiap level
HEALTH_PER_LEVEL = 10       # Bonus HP per level
DAMAGE_PER_LEVEL = 2        # Bonus damage per level
SPEED_PER_LEVEL = 5         # Bonus speed per level

# Warna UI
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
