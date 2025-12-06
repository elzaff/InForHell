"""
SETTINGS MODULE
Konstanta dan konfigurasi global untuk game
"""
import pygame 
from os.path import join 
from os import walk


# ==================== WINDOW SETTINGS ====================
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720 
TILE_SIZE = 64


# ==================== GAME SETTINGS ====================
FPS = 60


# ==================== PLAYER SETTINGS ====================
PLAYER_SPEED = 300
PLAYER_MAX_HEALTH = 100
PLAYER_BASE_DAMAGE = 10


# ==================== WEAPON SETTINGS ====================
GUN_COOLDOWN = 200
BULLET_SPEED = 1200
BULLET_LIFETIME = 1000


# ==================== ENEMY SETTINGS ====================
ENEMY_SPAWN_INTERVAL = 2000  # milliseconds
ENEMY_BASE_SPEED = 100
ENEMY_SPAWN_DISTANCE = 600


# ==================== PROGRESSION SETTINGS ====================
EXP_BASE = 100
EXP_MULTIPLIER = 1.5
HEALTH_PER_LEVEL = 20


# ==================== UI COLORS ====================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
