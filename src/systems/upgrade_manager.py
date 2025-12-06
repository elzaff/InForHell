"""
UPGRADE MANAGER MODULE
Database upgrade, kartu level up, dan GameState.
"""
import pygame
from typing import List, Dict, Any, Optional
import random


# ==================== GAME STATE ====================

class GameState:
    """
    Mengelola state game dengan encapsulation.
    Properties: __is_running, __is_paused, __is_game_over, __score, __start_time
    Methods: calculate_score(player_stats), toggle_pause()
    """
    
    def __init__(self):
        self.__is_running = True
        self.__is_paused = False
        self.__is_game_over = False
        self.__start_time = pygame.time.get_ticks()
        self.__game_over_time = 0  # Waktu saat game over
        self.__pause_time = 0  # Total waktu yang di-pause
        self.__last_pause_start = 0  # Waktu mulai pause terakhir
        self.__score = 0
    
    @property
    def is_running(self) -> bool:
        return self.__is_running
    
    @property
    def is_paused(self) -> bool:
        return self.__is_paused
    
    @property
    def is_game_over(self) -> bool:
        return self.__is_game_over
    
    @property
    def elapsed_time(self) -> float:
        """Mengembalikan waktu berlalu dalam detik - berhenti saat game over"""
        if self.__is_game_over and self.__game_over_time > 0:
            # Return waktu saat game over (frozen)
            return (self.__game_over_time - self.__start_time) / 1000
        else:
            # Return waktu saat ini (masih bermain)
            return (pygame.time.get_ticks() - self.__start_time) / 1000
    
    @property
    def score(self) -> int:
        return self.__score
    
    def stop_game(self) -> None:
        """Menghentikan game loop"""
        self.__is_running = False
    
    def toggle_pause(self) -> None:
        """Mengubah status pause dan track waktu pause"""
        self.__is_paused = not self.__is_paused
        if self.__is_paused:
            # Mulai pause - catat waktu
            self.__last_pause_start = pygame.time.get_ticks()
        else:
            # Resume - tambahkan durasi pause ke total
            if self.__last_pause_start > 0:
                self.__pause_time += pygame.time.get_ticks() - self.__last_pause_start
    
    def pause(self) -> None:
        """Set game ke state paused"""
        if not self.__is_paused:
            self.toggle_pause()
    
    def resume(self) -> None:
        """Resume game dari pause"""
        if self.__is_paused:
            self.toggle_pause()
    
    def set_game_over(self) -> None:
        """Set status game over dan bekukan waktu"""
        if not self.__is_game_over:
            self.__is_game_over = True
            self.__game_over_time = pygame.time.get_ticks()  # Simpan waktu saat game over
    
    def calculate_score(self, player_stats: Any) -> int:
        """
        Menghitung skor berdasarkan kills, level, dan waktu.
        Rumus: (kills * 100) + (level * 500) + (time * 10)
        """
        kills_score = player_stats.kills * 100
        level_score = player_stats.level * 500
        time_score = int(self.elapsed_time * 10)
        self.__score = kills_score + level_score + time_score
        return self.__score


# ==================== UPGRADE CARD ====================

class UpgradeCard:
    """
    Representasi kartu upgrade individual
    """
    def __init__(self, upgrade_data: Dict[str, Any]):
        self.id = upgrade_data['id']
        self.name = upgrade_data['name']
        self.description = upgrade_data['description']
        self.type = upgrade_data['type']  # 'stat', 'weapon', 'passive'
        self.rarity = upgrade_data.get('rarity', 'common')  # common, rare, epic
        self.current_level = upgrade_data.get('current_level', 0)
        self.max_level = upgrade_data.get('max_level', 5)
        self.icon_color = upgrade_data.get('icon_color', (100, 100, 100))
        self.apply_func = upgrade_data.get('apply_func', None)
        
        # Untuk tracking apakah ini upgrade baru atau level up
        self.is_new = self.current_level == 0
    
    def can_upgrade(self) -> bool:
        """Check apakah masih bisa di-upgrade"""
        return self.current_level < self.max_level
    
    def get_next_level(self) -> int:
        """Get level setelah upgrade"""
        return self.current_level + 1
    
    def get_label(self) -> str:
        """Get label untuk kartu (NEW! atau Level Up!)"""
        if self.is_new:
            return "NEW!"
        else:
            return f"Lv {self.current_level} -> Lv {self.get_next_level()}"


# ==================== UPGRADE DATABASE ====================

class UpgradeDatabase:
    """
    Database untuk semua upgrade yang tersedia
    """
    def __init__(self):
        self.upgrades: Dict[str, Dict[str, Any]] = {}
        self.player_upgrades: Dict[str, int] = {}  # Track level setiap upgrade
        self._init_default_upgrades()
    
    def register_upgrade(self, upgrade_data: Dict[str, Any]):
        """Register upgrade baru ke database"""
        upgrade_id = upgrade_data['id']
        self.upgrades[upgrade_id] = upgrade_data
        if upgrade_id not in self.player_upgrades:
            self.player_upgrades[upgrade_id] = 0
    
    def get_upgrade(self, upgrade_id: str) -> Optional[Dict[str, Any]]:
        """Get upgrade data by ID"""
        if upgrade_id in self.upgrades:
            data = self.upgrades[upgrade_id].copy()
            data['current_level'] = self.player_upgrades.get(upgrade_id, 0)
            return data
        return None
    
    def get_available_upgrades(self, count: int = 3) -> List[UpgradeCard]:
        """
        Get random available upgrades untuk level up selection
        Prioritas: campur skill baru dan upgrade skill lama
        """
        available = []
        
        # Filter upgrades yang masih bisa di-level up
        for upgrade_id, upgrade_data in self.upgrades.items():
            current_level = self.player_upgrades.get(upgrade_id, 0)
            max_level = upgrade_data.get('max_level', 5)
            
            if current_level < max_level:
                data = upgrade_data.copy()
                data['current_level'] = current_level
                available.append(data)
        
        # Jika available kurang dari count, return semua yang ada
        if len(available) <= count:
            return [UpgradeCard(data) for data in available]
        
        # Pisahkan new dan existing upgrades
        new_upgrades = [u for u in available if self.player_upgrades.get(u['id'], 0) == 0]
        existing_upgrades = [u for u in available if self.player_upgrades.get(u['id'], 0) > 0]
        
        # Strategy: 60% chance untuk new, 40% untuk existing
        selected = []
        for _ in range(count):
            if len(new_upgrades) > 0 and len(existing_upgrades) > 0:
                if random.random() < 0.6:
                    selected.append(new_upgrades.pop(random.randint(0, len(new_upgrades) - 1)))
                else:
                    selected.append(existing_upgrades.pop(random.randint(0, len(existing_upgrades) - 1)))
            elif len(new_upgrades) > 0:
                selected.append(new_upgrades.pop(random.randint(0, len(new_upgrades) - 1)))
            elif len(existing_upgrades) > 0:
                selected.append(existing_upgrades.pop(random.randint(0, len(existing_upgrades) - 1)))
        
        return [UpgradeCard(data) for data in selected]
    
    def apply_upgrade(self, upgrade_id: str, player: Any):
        """Apply upgrade ke player dan increment level"""
        if upgrade_id in self.upgrades:
            # Increment level
            self.player_upgrades[upgrade_id] = self.player_upgrades.get(upgrade_id, 0) + 1
            
            # Apply effect via callback function
            upgrade_data = self.upgrades[upgrade_id]
            if 'apply_func' in upgrade_data and upgrade_data['apply_func']:
                upgrade_data['apply_func'](player, self.player_upgrades[upgrade_id])
            
            return True
        return False
    
    def _init_default_upgrades(self):
        """Initialize passive items dan upgrades"""
        
        # ========================================================================
        # PASSIVE ITEMS - "Neraka Informatika" Theme
        # ========================================================================
        
        # 1. Bocoran Soal Kating - EXP Boost
        self.register_upgrade({
            'id': 'bocoran_soal',
            'name': 'Bocoran Soal Kating',
            'description': 'Pengetahuan instan dari kakak tingkat. +25% EXP Gain per level.',
            'type': 'passive',
            'rarity': 'rare',
            'max_level': 5,
            'icon_color': (255, 220, 100),  # Kuning kertas
            'apply_func': self._apply_bocoran_soal
        })
        
        # 2. SKS (Sistem Kebut Semalam) - Risk vs Reward
        self.register_upgrade({
            'id': 'sks',
            'name': 'SKS (Sistem Kebut Semalam)',
            'description': 'Mode nekat! +15% Damage tapi -10 Max HP per level. Tidur untuk orang lemah!',
            'type': 'passive',
            'rarity': 'epic',
            'max_level': 5,
            'icon_color': (255, 50, 50),  # Merah bahaya
            'apply_func': self._apply_sks
        })
        
        # 3. Broadcasting Protocol - Multi-Shot
        self.register_upgrade({
            'id': 'broadcasting_protocol',
            'name': 'Broadcasting Protocol',
            'description': 'Tembakan menyebar seperti shotgun! +1 peluru per level.',
            'type': 'passive',
            'rarity': 'legendary',
            'max_level': 5,
            'icon_color': (100, 255, 150),  # Hijau signal
            'apply_func': self._apply_broadcasting_protocol
        })
        
        # 4. Kopi Sachet - Movement Speed Boost
        self.register_upgrade({
            'id': 'kopi_sachet',
            'name': 'Kopi Sachet',
            'description': 'Kafein membuat kamu bergerak lebih cepat! +15% Movement Speed per level.',
            'type': 'passive',
            'rarity': 'common',
            'max_level': 5,
            'icon_color': (139, 69, 19),  # Cokelat kopi
            'apply_func': self._apply_kopi_sachet
        })
        
        # 5. Plagiat Tugas - Lifesteal
        self.register_upgrade({
            'id': 'plagiat_tugas',
            'name': 'Plagiat Tugas',
            'description': 'Ambil punya teman, akui punya sendiri. 5-15% kemungkinan heal 1 HP per serangan.',
            'type': 'passive',
            'rarity': 'epic',
            'max_level': 3,
            'icon_color': (138, 43, 226),  # Ungu (Vampire purple)
            'apply_func': self._apply_plagiat_tugas
        })
        
        # 6. GPTHelper - Skill Cooldown Reduction
        self.register_upgrade({
            'id': 'gpthelper',
            'name': 'GPTHelper',
            'description': 'AI yang bikin skill lebih cepat! -10% Skill Cooldown per level.',
            'type': 'passive',
            'rarity': 'epic',
            'max_level': 5,
            'icon_color': (0, 255, 255),  # Cyan AI
            'apply_func': self._apply_gpthelper
        })
        
        # ========================================================================
        # BASIC STAT UPGRADES
        # ========================================================================
        
        self.register_upgrade({
            'id': 'health_boost',
            'name': 'Vitality Boost',
            'description': 'Meningkatkan darah maksimal. +20 Max Health.',
            'type': 'stat',
            'rarity': 'common',
            'max_level': 5,
            'icon_color': (255, 100, 100),
            'apply_func': lambda player, level: player.stats.increase_max_health(20)
        })
    
    # ========================================================================
    # UPGRADE APPLY FUNCTIONS
    # ========================================================================
    
    @staticmethod
    def _apply_bocoran_soal(player, level):
        """Meningkatkan EXP Gain"""
        exp_boost = 1.25 * level
        if not hasattr(player.stats, 'exp_multiplier'):
            player.stats.exp_multiplier = 1.0
        player.stats.exp_multiplier += 0.25 * level
        print(f"[Bocoran Soal] EXP Gain: +{int(exp_boost * 100)}%")

    @staticmethod
    def _apply_sks(player, level):
        """Risk vs Reward: +Damage tapi -Max HP"""
        damage_boost = int(player.stats.base_damage * 0.15 * level)
        player.stats.increase_damage(damage_boost)
        hp_penalty = 10 * level
        player.stats.decrease_max_health(hp_penalty)
        print(f"[SKS] Damage +{damage_boost}, Max HP -{hp_penalty}")

    @staticmethod
    def _apply_broadcasting_protocol(player, level):
        """Multi-shot: Menambah jumlah peluru per tembakan"""
        if not hasattr(player, 'multi_shot_count'):
            player.multi_shot_count = 1
        player.multi_shot_count = 1 + level
        print(f"[Broadcasting Protocol] Bullets per shot: {player.multi_shot_count}")

    @staticmethod
    def _apply_kopi_sachet(player, level):
        """Kopi Sachet: Movement Speed Boost"""
        speed_boost = 0.15 * level
        player.stat_modifiers['speed'] = 1.0 + speed_boost
        print(f"[Kopi Sachet] Movement Speed +{int(speed_boost * 100)}%!")

    @staticmethod
    def _apply_plagiat_tugas(player, level):
        """Plagiat Tugas: Lifesteal"""
        lifesteal = 0.05 * level
        player.lifesteal_chance = min(lifesteal, 0.15)
        print(f"[Plagiat Tugas] Lifesteal {int(player.lifesteal_chance * 100)}% chance!")

    @staticmethod
    def _apply_gpthelper(player, level):
        """GPTHelper: Skill Cooldown Reduction"""
        cooldown_reduction = 0.10 * level
        player.stat_modifiers['cooldown'] = 1.0 - cooldown_reduction
        print(f"[GPTHelper] Skill Cooldown -{int(cooldown_reduction * 100)}%!")
