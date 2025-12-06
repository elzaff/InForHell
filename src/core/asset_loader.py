"""
ASSET LOADER MODULE
Manager khusus untuk load gambar dan suara game.
"""
import pygame
from os.path import join
from os import walk


class AssetLoader:
    """
    Centralized asset loading manager.
    Handles loading of images, sounds, and animations.
    """
    
    def __init__(self):
        self.__images = {}
        self.__sounds = {}
        self.__animations = {}
    
    @property
    def images(self):
        return self.__images
    
    @property
    def sounds(self):
        return self.__sounds
    
    @property
    def animations(self):
        return self.__animations
    
    def load_image(self, key: str, path: str, convert_alpha: bool = True) -> pygame.Surface:
        """Load a single image and cache it."""
        try:
            if convert_alpha:
                surf = pygame.image.load(path).convert_alpha()
            else:
                surf = pygame.image.load(path).convert()
            self.__images[key] = surf
            return surf
        except Exception as e:
            print(f"Failed to load image {path}: {e}")
            return None
    
    def load_animation_folder(self, key: str, folder_path: str) -> list:
        """Load all images from a folder as animation frames."""
        frames = []
        try:
            for _, __, file_names in walk(folder_path):
                png_files = [f for f in file_names if f.endswith('.png')]
                try:
                    png_files.sort(key=lambda name: int(name.split('.')[0]))
                except ValueError:
                    png_files.sort()
                
                for file_name in png_files:
                    full_path = join(folder_path, file_name)
                    try:
                        surf = pygame.image.load(full_path).convert_alpha()
                        frames.append(surf)
                    except:
                        pass
            
            if frames:
                self.__animations[key] = frames
            return frames
        except Exception as e:
            print(f"Failed to load animation from {folder_path}: {e}")
            return []
    
    def load_enemy_frames(self, enemies_path: str) -> dict:
        """Load all enemy animation frames."""
        enemy_frames = {}
        
        if not list(walk(enemies_path)):
            return enemy_frames
        
        folders = list(walk(enemies_path))[0][1]
        
        for folder in folders:
            folder_path = join(enemies_path, folder)
            frames = self.load_animation_folder(f"enemy_{folder}", folder_path)
            if frames:
                enemy_frames[folder] = frames
        
        return enemy_frames
    
    def load_player_frames(self, player_path: str) -> dict:
        """Load all player animation frames."""
        player_frames = {'left': [], 'right': [], 'up': [], 'down': []}
        
        for state in player_frames.keys():
            state_path = join(player_path, state)
            frames = self.load_animation_folder(f"player_{state}", state_path)
            if frames:
                player_frames[state] = frames
        
        return player_frames
    
    def load_sound(self, key: str, path: str, volume: float = 1.0) -> pygame.mixer.Sound:
        """Load a sound file and cache it."""
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            self.__sounds[key] = sound
            return sound
        except Exception as e:
            print(f"Failed to load sound {path}: {e}")
            return None
    
    def get_image(self, key: str) -> pygame.Surface:
        """Get a cached image by key."""
        return self.__images.get(key)
    
    def get_sound(self, key: str) -> pygame.mixer.Sound:
        """Get a cached sound by key."""
        return self.__sounds.get(key)
    
    def get_animation(self, key: str) -> list:
        """Get cached animation frames by key."""
        return self.__animations.get(key, [])
