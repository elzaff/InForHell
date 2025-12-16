"""
PATHFINDING MODULE
Menggunakan algoritma A* (A-Star) untuk mencari jalan yang lebih optimal.
"""
import pygame
import heapq  # Digunakan untuk Priority Queue pada A*
from settings import TILE_SIZE

import pygame
import heapq
from collections import deque
from settings import TILE_SIZE

class Pathfinder:
    def __init__(self, tmx_map):
        self.matrix = self.__create_grid(tmx_map)
        self.width = len(self.matrix[0])
        self.height = len(self.matrix)
        
    def __create_grid(self, tmx_map):
        # ... (Kode grid creation SAMA PERSIS seperti sebelumnya) ...
        width = tmx_map.width
        height = tmx_map.height
        matrix = [[0 for x in range(width)] for y in range(height)]
        target_layers = ['Collisions', 'Objects']
        
        for layer_name in target_layers:
            try:
                layer = tmx_map.get_layer_by_name(layer_name)
                if hasattr(layer, 'tiles'):
                    for x, y, image in layer.tiles():
                        matrix[y][x] = 1
                else:
                    for obj in layer:
                        start_col = int(obj.x // TILE_SIZE)
                        start_row = int(obj.y // TILE_SIZE)
                        cols_span = int(obj.width / TILE_SIZE) + 1
                        rows_span = int(obj.height / TILE_SIZE) + 1
                        for r in range(rows_span):
                            for c in range(cols_span):
                                if 0 <= start_row + r < height and 0 <= start_col + c < width:
                                    matrix[start_row + r][start_col + c] = 1
            except ValueError:
                pass
        return matrix

    # --- ALGORITMA BFS (Untuk Musuh Biasa) ---
    def get_path_bfs(self, start_pos, target_pos):
        start = (int(start_pos[0] // TILE_SIZE), int(start_pos[1] // TILE_SIZE))
        end = (int(target_pos[0] // TILE_SIZE), int(target_pos[1] // TILE_SIZE))
        
        if start == end: return pygame.Vector2()
        
        queue = deque([start])
        came_from = {start: None}
        found = False
        
        while queue:
            current = queue.popleft()
            if current == end:
                found = True
                break
            
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                next_node = (current[0] + dx, current[1] + dy)
                if (0 <= next_node[0] < self.width and 
                    0 <= next_node[1] < self.height and 
                    self.matrix[next_node[1]][next_node[0]] == 0 and 
                    next_node not in came_from):
                    queue.append(next_node)
                    came_from[next_node] = current
        
        if not found: return pygame.Vector2()
        
        # Traceback
        current = end
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
            
        next_step = path[-1]
        pixel_pos = pygame.Vector2(next_step[0]*TILE_SIZE + TILE_SIZE//2, next_step[1]*TILE_SIZE + TILE_SIZE//2)
        return (pixel_pos - pygame.Vector2(start_pos)).normalize()

    # --- ALGORITMA A* (Untuk Boss) ---
    def get_path_astar(self, start_pos, target_pos):
        start = (int(start_pos[0] // TILE_SIZE), int(start_pos[1] // TILE_SIZE))
        end = (int(target_pos[0] // TILE_SIZE), int(target_pos[1] // TILE_SIZE))
        
        if start == end: return pygame.Vector2()

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        found = False

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == end:
                found = True
                break
            
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if (0 <= neighbor[0] < self.width and 
                    0 <= neighbor[1] < self.height and 
                    self.matrix[neighbor[1]][neighbor[0]] == 0):
                    
                    tentative_g = g_score[current] + 1
                    if tentative_g < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f = tentative_g + heuristic(neighbor, end)
                        heapq.heappush(open_set, (f, neighbor))
        
        if not found: return pygame.Vector2()
        
        current = end
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
            
        next_step = path[-1]
        pixel_pos = pygame.Vector2(next_step[0]*TILE_SIZE + TILE_SIZE//2, next_step[1]*TILE_SIZE + TILE_SIZE//2)
        return (pixel_pos - pygame.Vector2(start_pos)).normalize()