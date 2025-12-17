"""
Upgrade Manager Module
Database upgrade, kartu level up, dan GameState.
"""
import pygame
import random


class GameState:
    """Mengelola state game (running, paused, game over)."""
    
    def __init__(self):
        self.__is_running = True
        self.__is_paused = False
        self.__is_game_over = False
        self.__start_time = pygame.time.get_ticks()
        self.__game_over_time = 0
        self.__pause_time = 0
        self.__last_pause_start = 0
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
        """Waktu bermain dalam detik (berhenti saat game over)."""
        if self.__is_game_over and self.__game_over_time > 0:
            return (self.__game_over_time - self.__start_time) / 1000
        else:
            return (pygame.time.get_ticks() - self.__start_time) / 1000
    
    @property
    def score(self) -> int:
        return self.__score
    
    def stop_game(self) -> None:
        """Hentikan game loop."""
        self.__is_running = False
    
    def toggle_pause(self) -> None:
        """Toggle status pause."""
        self.__is_paused = not self.__is_paused
        if self.__is_paused:
            self.__last_pause_start = pygame.time.get_ticks()
        else:
            if self.__last_pause_start > 0:
                self.__pause_time += pygame.time.get_ticks() - self.__last_pause_start
    
    def pause(self) -> None:
        """Set game ke pause."""
        if not self.__is_paused:
            self.toggle_pause()
    
    def resume(self) -> None:
        """Resume game dari pause."""
        if self.__is_paused:
            self.toggle_pause()
    
    def set_game_over(self) -> None:
        """Set status game over."""
        if not self.__is_game_over:
            self.__is_game_over = True
            self.__game_over_time = pygame.time.get_ticks()
    
    def calculate_score(self, player_stats) -> int:
        """Hitung skor: (kills * 100) + (level * 500) + (time * 10)"""
        kills_score = player_stats.kills * 100
        level_score = player_stats.level * 500
        time_score = int(self.elapsed_time * 10)
        self.__score = kills_score + level_score + time_score
        return self.__score


class UpgradeCard:
    """Representasi kartu upgrade untuk level up."""
    
    def __init__(self, upgrade_data: dict):
        self.id = upgrade_data['id']
        self.name = upgrade_data['name']
        self.description = upgrade_data['description']
        self.type = upgrade_data['type']
        self.rarity = upgrade_data.get('rarity', 'common')
        self.current_level = upgrade_data.get('current_level', 0)
        self.max_level = upgrade_data.get('max_level', 5)
        self.icon_color = upgrade_data.get('icon_color', (100, 100, 100))
        self.apply_func = upgrade_data.get('apply_func', None)
        self.is_new = self.current_level == 0
    
    def can_upgrade(self) -> bool:
        """Cek apakah masih bisa di-upgrade."""
        return self.current_level < self.max_level
    
    def get_next_level(self) -> int:
        """Level setelah upgrade."""
        return self.current_level + 1
    
    def get_label(self) -> str:
        """Label kartu (NEW! atau Level Up)."""
        if self.is_new:
            return "NEW!"
        else:
            return f"Lv {self.current_level} -> Lv {self.get_next_level()}"


class UpgradeDatabase:
    """Database semua upgrade yang tersedia."""
    
    def __init__(self):
        self.upgrades = {}
        self.player_upgrades = {}
        self._init_default_upgrades()
    
    def register_upgrade(self, upgrade_data: dict):
        """Daftarkan upgrade baru."""
        upgrade_id = upgrade_data['id']
        self.upgrades[upgrade_id] = upgrade_data
        if upgrade_id not in self.player_upgrades:
            self.player_upgrades[upgrade_id] = 0
    
    def get_upgrade(self, upgrade_id: str):
        """Ambil data upgrade berdasarkan ID."""
        if upgrade_id in self.upgrades:
            data = self.upgrades[upgrade_id].copy()
            data['current_level'] = self.player_upgrades.get(upgrade_id, 0)
            return data
        return None
    
    def get_available_upgrades(self, count: int = 3):
        """Ambil random upgrade untuk pilihan level up."""
        available = []
        
        for upgrade_id, upgrade_data in self.upgrades.items():
            current_level = self.player_upgrades.get(upgrade_id, 0)
            max_level = upgrade_data.get('max_level', 5)
            
            if current_level < max_level:
                data = upgrade_data.copy()
                data['current_level'] = current_level
                available.append(data)
        
        if len(available) <= count:
            return [UpgradeCard(data) for data in available]
        
        # 60% chance untuk upgrade baru
        new_upgrades = [u for u in available if self.player_upgrades.get(u['id'], 0) == 0]
        existing_upgrades = [u for u in available if self.player_upgrades.get(u['id'], 0) > 0]
        
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
    
    def apply_upgrade(self, upgrade_id: str, player):
        """Apply upgrade ke player."""
        if upgrade_id in self.upgrades:
            self.player_upgrades[upgrade_id] = self.player_upgrades.get(upgrade_id, 0) + 1
            
            upgrade_data = self.upgrades[upgrade_id]
            if 'apply_func' in upgrade_data and upgrade_data['apply_func']:
                upgrade_data['apply_func'](player, self.player_upgrades[upgrade_id])
            
            return True
        return False
    
    def _init_default_upgrades(self):
        """Inisialisasi upgrade default."""
        
        # 1. Bocoran Soal - EXP Boost
        self.register_upgrade({
            'id': 'bocoran_soal',
            'name': 'Bocoran Soal',
            'description': 'Ujian lancar kalo ada bocoran soal. +25% EXP Gain per level.',
            'type': 'passive',
            'rarity': 'rare',
            'max_level': 5,
            'icon_color': (255, 220, 100),
            'apply_func': self._apply_bocoran_soal
        })
        
        # 2. SKS - Risk vs Reward
        self.register_upgrade({
            'id': 'sks',
            'name': 'SKS (Sistem Kebut Semalam)',
            'description': 'Cocok banget untuk deadliner. +15% Damage tapi -10 Max HP per level.',
            'type': 'passive',
            'rarity': 'epic',
            'max_level': 5,
            'icon_color': (255, 50, 50),
            'apply_func': self._apply_sks
        })
        
        # 3. Keyboard Smash - Multi-Shot
        self.register_upgrade({
            'id': 'keyboard_smash',
            'name': 'Keyboard Smash',
            'description': 'Memukul keyboard bukan solusi memecahkan error loh! +1 peluru per level.',
            'type': 'passive',
            'rarity': 'legendary',
            'max_level': 5,
            'icon_color': (100, 255, 150),
            'apply_func': self._apply_keyboard_smash
        })
        
        # 4. Kopi Sachet - Speed Boost
        self.register_upgrade({
            'id': 'kopi_sachet',
            'name': 'Kopi Sachet',
            'description': 'Kafein membuat kamu bergerak lebih cepat! +15% Movement Speed per level.',
            'type': 'passive',
            'rarity': 'common',
            'max_level': 5,
            'icon_color': (139, 69, 19),
            'apply_func': self._apply_kopi_sachet
        })
        
        # 5. Plagiat Tugas - Lifesteal
        self.register_upgrade({
            'id': 'plagiat_tugas',
            'name': 'Plagiat Tugas',
            'description': 'Nyolong tugas teman bukan hal baik ya! 5-15% kemungkinan heal 1 HP per serangan.',
            'type': 'passive',
            'rarity': 'epic',
            'max_level': 3,
            'icon_color': (138, 43, 226),
            'apply_func': self._apply_plagiat_tugas
        })
        
        # 6. GPT Helper - Cooldown Reduction
        self.register_upgrade({
            'id': 'gpthelper',
            'name': 'GPT Helper',
            'description': 'AI ngebantu kehidupan sehari-hari! -10% Skill Cooldown per level.',
            'type': 'passive',
            'rarity': 'epic',
            'max_level': 5,
            'icon_color': (0, 255, 255),
            'apply_func': self._apply_gpthelper
        })
        
        # 7. Kantin TC - Health Boost
        self.register_upgrade({
            'id': 'health_boost',
            'name': 'Kantin TC',
            'description': 'Makanan kantin TC enak semua! +20 Max Health.',
            'type': 'stat',
            'rarity': 'common',
            'max_level': 5,
            'icon_color': (255, 100, 100),
            'apply_func': lambda player, level: player.stats.increase_max_health(20)
        })
    
    # Fungsi apply upgrade
    
    @staticmethod
    def _apply_bocoran_soal(player, level):
        """EXP Gain boost."""
        if not hasattr(player.stats, 'exp_multiplier'):
            player.stats.exp_multiplier = 1.0
        player.stats.exp_multiplier += 0.25 * level

    @staticmethod
    def _apply_sks(player, level):
        """Damage boost dengan HP penalty."""
        damage_boost = int(player.stats.base_damage * 0.15 * level)
        player.stats.increase_damage(damage_boost)
        hp_penalty = 10 * level
        player.stats.decrease_max_health(hp_penalty)

    @staticmethod
    def _apply_keyboard_smash(player, level):
        """Multi-shot upgrade."""
        if not hasattr(player, 'multi_shot_count'):
            player.multi_shot_count = 1
        player.multi_shot_count = 1 + level

    @staticmethod
    def _apply_kopi_sachet(player, level):
        """Speed boost."""
        speed_boost = 0.15 * level
        player.stat_modifiers['speed'] = 1.0 + speed_boost

    @staticmethod
    def _apply_plagiat_tugas(player, level):
        """Lifesteal upgrade."""
        lifesteal = 0.05 * level
        player.lifesteal_chance = min(lifesteal, 0.15)

    @staticmethod
    def _apply_gpthelper(player, level):
        """Cooldown reduction."""
        cooldown_reduction = 0.10 * level
        player.stat_modifiers['cooldown'] = 1.0 - cooldown_reduction
