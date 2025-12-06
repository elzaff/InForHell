"""
COLLISION MANAGER MODULE
Mengelola semua deteksi tabrakan.
"""
import pygame
from typing import Optional, List, Dict, Any
import random


class CollisionManager:
    """
    Mengelola semua deteksi tabrakan.
    Methods: check_bullet_enemy(), check_player_enemy(), check_player_item()
    """
    
    def __init__(self, impact_sound: Optional[pygame.mixer.Sound] = None):
        self.__impact_sound = impact_sound
    
    def check_bullet_enemy(self, bullet_sprites: pygame.sprite.Group, enemy_sprites: pygame.sprite.Group, player: Any) -> Dict[str, Any]:
        """
        Cek tabrakan antara peluru dan musuh.
        Returns: dict dengan 'kills', 'exp_gained', 'level_up'
        """
        result = {
            'kills': 0,
            'exp_gained': 0,
            'level_up': False
        }
        
        if bullet_sprites:
            for bullet in bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(
                    bullet, enemy_sprites, False, pygame.sprite.collide_mask
                )
                
                if collision_sprites:
                    if self.__impact_sound:
                        self.__impact_sound.play()
                    
                    for enemy in collision_sprites:
                        # take_damage return True jika enemy baru mati
                        just_died = enemy.take_damage(bullet.damage)
                        
                        # Lifesteal check (Plagiat Tugas)
                        if hasattr(player, 'lifesteal_chance') and player.lifesteal_chance > 0:
                            if random.random() < player.lifesteal_chance:
                                player.heal(1)
                                # Optional: Visual feedback bisa ditambah nanti
                        
                        # Berikan EXP dan kill count hanya jika baru mati
                        if just_died:
                            exp_reward = enemy.give_exp_reward()
                            if exp_reward > 0:
                                leveled_up = player.gain_exp(exp_reward)
                                player.stats.add_kill()
                                
                                result['kills'] += 1
                                result['exp_gained'] += exp_reward
                                if leveled_up:
                                    result['level_up'] = True
                    
                    bullet.kill()
        
        return result
    
    def check_player_enemy(self, player: Any, enemy_sprites: pygame.sprite.Group) -> bool:
        """
        Cek tabrakan antara player dan musuh.
        Returns: True jika player menerima damage.
        """
        if player.stats.is_alive:
            collided_enemies = pygame.sprite.spritecollide(
                player, enemy_sprites, False, pygame.sprite.collide_mask
            )
            
            if collided_enemies:
                # Terima damage dari semua musuh yang bertabrakan
                for enemy in collided_enemies:
                    if not enemy.is_dead:
                        player.take_damage(enemy.damage)
                return True
        return False
    
    def check_player_item(self, player: Any, item_sprites: pygame.sprite.Group) -> List[Any]:
        """
        Cek tabrakan antara player dan item.
        Returns: list item yang diambil.
        """
        picked_items = []
        
        # Cek attraction (tarikan magnet) terlebih dahulu
        player_pos = pygame.Vector2(player.rect.center)
        for item in item_sprites:
            if hasattr(item, 'check_attraction'):
                item.check_attraction(player_pos)
            if hasattr(item, 'move_towards_player'):
                item.move_towards_player(player_pos, 1/60)  # Asumsi 60 FPS
        
        # Cek pickup collision
        collided_items = pygame.sprite.spritecollide(
            player, item_sprites, False, pygame.sprite.collide_mask
        )
        
        if collided_items:
            for item in collided_items:
                if hasattr(item, 'on_pickup'):
                    item.on_pickup(player)
                    picked_items.append(item)
                    item.kill()
        
        return picked_items
