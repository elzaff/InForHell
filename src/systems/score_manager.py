"""
SCORE MANAGER MODULE
Sistem penyimpanan high score dengan JSON.
"""
import json
import os
from typing import List, Dict, Tuple, Optional


class ScoreManager:
    """
    Manager untuk high score dengan JSON file storage.
    Properties: __scores, __file_path
    Methods: load_scores(), save_score(), get_leaderboard(), get_player_rank()
    """
    
    def __init__(self, file_path: str = "data/highscores.json"):
        self.__file_path = file_path
        self.__scores: List[Dict] = []
        self.__max_entries = 100
        self.__last_player_score: Optional[int] = None
        self.__last_player_name: Optional[str] = None
        self.load_scores()
    
    def load_scores(self) -> None:
        """Load scores dari file JSON"""
        try:
            if os.path.exists(self.__file_path):
                with open(self.__file_path, 'r') as f:
                    data = json.load(f)
                    self.__scores = data.get('scores', [])
            else:
                self.__scores = []
        except (json.JSONDecodeError, IOError):
            self.__scores = []
    
    def save_score(self, name: str, score: int) -> int:
        """
        Simpan score baru ke leaderboard.
        Returns: rank pemain (1-indexed)
        """
        # Validasi nama (3 huruf uppercase)
        name = name.upper()[:3].ljust(3, '_')
        
        # Tambah entry baru
        new_entry = {
            'name': name,
            'score': score
        }
        self.__scores.append(new_entry)
        
        # Sort by score descending
        self.__scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit entries
        if len(self.__scores) > self.__max_entries:
            self.__scores = self.__scores[:self.__max_entries]
        
        # Simpan ke file
        self._write_to_file()
        
        # Track last player untuk display
        self.__last_player_score = score
        self.__last_player_name = name
        
        # Return rank
        return self.get_player_rank(score, name)
    
    def _write_to_file(self) -> None:
        """Write scores ke file JSON"""
        try:
            # Buat folder jika belum ada
            os.makedirs(os.path.dirname(self.__file_path), exist_ok=True)
            
            with open(self.__file_path, 'w') as f:
                json.dump({'scores': self.__scores}, f, indent=2)
        except IOError as e:
            print(f"Error saving scores: {e}")
    
    def get_leaderboard(self, top_n: int = 5) -> List[Dict]:
        """
        Get top N entries untuk display.
        Returns: list of {'rank': int, 'name': str, 'score': int}
        """
        result = []
        for i, entry in enumerate(self.__scores[:top_n]):
            result.append({
                'rank': i + 1,
                'name': entry['name'],
                'score': entry['score']
            })
        return result
    
    def get_player_rank(self, score: int, name: str = None) -> int:
        """
        Get rank pemain berdasarkan score.
        Returns: rank (1-indexed), 0 jika tidak ditemukan
        """
        for i, entry in enumerate(self.__scores):
            if entry['score'] == score:
                if name is None or entry['name'] == name:
                    return i + 1
        return 0
    
    def get_last_player_entry(self) -> Optional[Dict]:
        """
        Get entry pemain terakhir yang save score.
        Returns: {'rank': int, 'name': str, 'score': int} atau None
        """
        if self.__last_player_score is not None:
            rank = self.get_player_rank(self.__last_player_score, self.__last_player_name)
            if rank > 0:
                return {
                    'rank': rank,
                    'name': self.__last_player_name,
                    'score': self.__last_player_score
                }
        return None
    
    def clear_last_player(self) -> None:
        """Clear last player tracking (untuk new game)"""
        self.__last_player_score = None
        self.__last_player_name = None
    
    def is_high_score(self, score: int) -> bool:
        """Check jika score masuk leaderboard"""
        if len(self.__scores) < self.__max_entries:
            return True
        return score > self.__scores[-1]['score']
    
    @property
    def total_entries(self) -> int:
        return len(self.__scores)
