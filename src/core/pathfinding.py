"""
PATHFINDING MODULE
Menggunakan algoritma BFS (Breadth-First Search) untuk mencari jalan.
"""
import pygame
from settings import TILE_SIZE
from collections import deque


class Pathfinder:
    def __init__(self, tmx_map):
        self.matrix = self.__create_grid(tmx_map)
        self.width = len(self.matrix[0])
        self.height = len(self.matrix)
        
    def __create_grid(self, tmx_map):
        """Mengubah TMX Map menjadi Matrix 0 dan 1"""
        width = tmx_map.width
        height = tmx_map.height
        
        # Buat grid kosong (0 = jalan, 1 = tembok)
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
                        # Konversi Pixel -> Grid Index
                        start_col = int(obj.x // TILE_SIZE)
                        start_row = int(obj.y // TILE_SIZE)
                        
                        # Hitung lebar & tinggi objek dalam satuan tile
                        cols_span = int(obj.width / TILE_SIZE) + 1
                        rows_span = int(obj.height / TILE_SIZE) + 1
                        
                        # Loop semua tile yang tertutup kotak objek ini
                        for r in range(rows_span):
                            for c in range(cols_span):
                                target_y = start_row + r
                                target_x = start_col + c
                                
                                # Pastikan tidak keluar batas map
                                if 0 <= target_y < height and 0 <= target_x < width:
                                    matrix[target_y][target_x] = 1
                                    
            except ValueError:
                pass
                
        return matrix

    def get_path(self, start_pos, target_pos):
        """
        Mencari jalan dari Start ke Target.
        Input: Koordinat PIXEL (x, y)
        Output: Vector arah langkah pertama (next step)
        """
        # Konversi Pixel ke Grid Index
        start = (int(start_pos[0] // TILE_SIZE), int(start_pos[1] // TILE_SIZE))
        end = (int(target_pos[0] // TILE_SIZE), int(target_pos[1] // TILE_SIZE))
        
        # Cek batas map
        if not (0 <= start[0] < self.width and 0 <= start[1] < self.height): return pygame.Vector2()
        if not (0 <= end[0] < self.width and 0 <= end[1] < self.height): return pygame.Vector2()
        
        # Jika posisi sama, diam
        if start == end:
            return pygame.Vector2()

        # --- ALGORITMA BFS ---
        queue = deque([start])
        came_from = {start: None}
        
        while queue:
            current = queue.popleft()
            
            if current == end:
                break
            
            # Cek 4 arah (Atas, Bawah, Kiri, Kanan)
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                next_node = (current[0] + dx, current[1] + dy)
                
                # Cek apakah valid (dalam map, bukan tembok, belum dikunjungi)
                if (0 <= next_node[0] < self.width and 
                    0 <= next_node[1] < self.height and 
                    self.matrix[next_node[1]][next_node[0]] == 0 and 
                    next_node not in came_from):
                    
                    queue.append(next_node)
                    came_from[next_node] = current
        
        # --- REKONSTRUKSI JALUR ---
        # Kita tarik mundur dari End ke Start untuk tau langkah pertama
        if end not in came_from:
            return pygame.Vector2() # Tidak ada jalan (tembok tertutup total)
            
        current = end
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
            
        # Path sekarang terbalik (End -> Start), kita cuma butuh langkah terakhir (langkah pertama dari start)
        next_step_grid = path[-1]
        
        # Konversi balik Grid -> Pixel (tengah tile)
        next_step_pixel = pygame.Vector2(
            next_step_grid[0] * TILE_SIZE + TILE_SIZE // 2,
            next_step_grid[1] * TILE_SIZE + TILE_SIZE // 2
        )
        
        # Hitung vector arah
        direction = (next_step_pixel - pygame.Vector2(start_pos)).normalize()
        return direction
