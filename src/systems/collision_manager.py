"""
Collision Manager Module
Mengelola semua deteksi collision.
"""
import pygame
import random


class CollisionManager:
    """Mengelola collision antara bullet, enemy, dan player."""
    
    def __init__(self, impact_sound=None):
        self.__impact_sound = impact_sound
    
    def check_bullet_enemy(self, bullet_sprites, enemy_sprites, player) -> dict:
        """
        Cek collision antara bullet dan enemy.
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
                        just_died = enemy.take_damage(bullet.damage)
                        
                        # Lifesteal (Plagiat Tugas)
                        if hasattr(player, 'lifesteal_chance') and player.lifesteal_chance > 0:
                            if random.random() < player.lifesteal_chance:
                                player.heal(1)
                        
                        # EXP dan kill count
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
    
    def check_player_enemy(self, player, enemy_sprites) -> bool:
        """
        Cek collision antara player dan enemy.
        Returns: True jika player kena damage.
        """
        if player.stats.is_alive:
            collided_enemies = pygame.sprite.spritecollide(
                player, enemy_sprites, False, pygame.sprite.collide_mask
            )
            
            if collided_enemies:
                for enemy in collided_enemies:
                    if not enemy.is_dead:
                        player.take_damage(enemy.damage)
                return True
        return False
    
    def check_player_item(self, player, item_sprites) -> list:
        """
        Cek collision antara player dan item.
        Returns: list item yang diambil.
        """
        picked_items = []
        
        player_pos = pygame.Vector2(player.rect.center)
        for item in item_sprites:
            if hasattr(item, 'check_attraction'):
                item.check_attraction(player_pos)
            if hasattr(item, 'move_towards_player'):
                item.move_towards_player(player_pos, 1/60)
        
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
