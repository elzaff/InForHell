"""
FLOCKING BEHAVIOR MODULE (Boids Algorithm)
Implementasi algoritma Boids untuk gerakan horde yang realistic.

Tiga aturan utama:
1. Separation - Hindari tabrakan dengan musuh lain
2. Alignment - Bergerak searah dengan musuh terdekat
3. Cohesion - Tetap berkelompok dengan musuh terdekat
"""
import pygame
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.enemies import Enemy


class FlockingBehavior:
    """
    Implementasi Boids Algorithm untuk flocking behavior.
    
    Usage:
        flocking = FlockingBehavior(enemy_instance, enemy_sprites_group)
        # In move calculation:
        flocking_force = flocking.calculate()
        final_direction = pathfinding_direction + flocking_force
    """
    
    def __init__(self, enemy: 'Enemy', enemy_sprites: pygame.sprite.Group,
                 perception_radius: float = 100,
                 separation_weight: float = 1.5,
                 alignment_weight: float = 1.0,
                 cohesion_weight: float = 0.8):
        """
        Args:
            enemy: Enemy yang memiliki flocking behavior ini
            enemy_sprites: Group berisi semua enemy untuk cek neighbors
            perception_radius: Jarak untuk mendeteksi neighbors
            separation_weight: Bobot untuk separation (hindari tabrakan)
            alignment_weight: Bobot untuk alignment (searah)
            cohesion_weight: Bobot untuk cohesion (berkelompok)
        """
        self.enemy = enemy
        self.enemy_sprites = enemy_sprites
        self.perception_radius = perception_radius
        
        # Weights untuk setiap behavior
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight
        self.cohesion_weight = cohesion_weight
        
        # Boss punya radius lebih besar
        if hasattr(enemy, 'is_boss') and enemy.is_boss:
            self.perception_radius = 200
            self.separation_weight = 0.5  # Boss tidak terlalu menghindar
    
    def _get_neighbors(self) -> List['Enemy']:
        """Dapatkan list neighbor dalam perception radius"""
        neighbors = []
        my_pos = pygame.Vector2(self.enemy.rect.center)
        
        for sprite in self.enemy_sprites:
            if sprite == self.enemy:
                continue
            
            other_pos = pygame.Vector2(sprite.rect.center)
            distance = my_pos.distance_to(other_pos)
            
            if distance < self.perception_radius and distance > 0:
                neighbors.append(sprite)
        
        return neighbors
    
    def _separation(self, neighbors: List['Enemy']) -> pygame.Vector2:
        """
        Rule 1: Separation
        Hindari tabrakan dengan musuh lain.
        Arah = menjauhi rata-rata posisi neighbors yang terlalu dekat.
        """
        if not neighbors:
            return pygame.Vector2()
        
        steering = pygame.Vector2()
        my_pos = pygame.Vector2(self.enemy.rect.center)
        
        for neighbor in neighbors:
            other_pos = pygame.Vector2(neighbor.rect.center)
            diff = my_pos - other_pos
            distance = diff.length()
            
            if distance > 0:
                # Semakin dekat, semakin kuat dorongan menjauh
                # Inverse square falloff
                diff = diff.normalize() / (distance * distance) * 100
                steering += diff
        
        if steering.length() > 0:
            steering = steering.normalize()
        
        return steering
    
    def _alignment(self, neighbors: List['Enemy']) -> pygame.Vector2:
        """
        Rule 2: Alignment
        Bergerak searah dengan rata-rata arah neighbors.
        """
        if not neighbors:
            return pygame.Vector2()
        
        avg_direction = pygame.Vector2()
        
        for neighbor in neighbors:
            if hasattr(neighbor, '_direction'):
                avg_direction += neighbor._direction
        
        if len(neighbors) > 0:
            avg_direction /= len(neighbors)
        
        if avg_direction.length() > 0:
            avg_direction = avg_direction.normalize()
        
        return avg_direction
    
    def _cohesion(self, neighbors: List['Enemy']) -> pygame.Vector2:
        """
        Rule 3: Cohesion
        Bergerak menuju rata-rata posisi neighbors (tetap berkelompok).
        """
        if not neighbors:
            return pygame.Vector2()
        
        center_of_mass = pygame.Vector2()
        
        for neighbor in neighbors:
            center_of_mass += pygame.Vector2(neighbor.rect.center)
        
        center_of_mass /= len(neighbors)
        
        # Arah menuju center of mass
        my_pos = pygame.Vector2(self.enemy.rect.center)
        direction = center_of_mass - my_pos
        
        if direction.length() > 0:
            direction = direction.normalize()
        
        return direction
    
    def calculate(self) -> pygame.Vector2:
        """
        Hitung total flocking force.
        
        Returns:
            pygame.Vector2: Combined flocking force vector (normalized)
        """
        neighbors = self._get_neighbors()
        
        if not neighbors:
            return pygame.Vector2()
        
        # Hitung setiap komponen
        separation = self._separation(neighbors) * self.separation_weight
        alignment = self._alignment(neighbors) * self.alignment_weight
        cohesion = self._cohesion(neighbors) * self.cohesion_weight
        
        # Gabungkan semua forces
        total_force = separation + alignment + cohesion
        
        if total_force.length() > 0:
            total_force = total_force.normalize()
        
        return total_force
