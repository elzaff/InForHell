"""
INVENTORY MANAGER MODULE
Sistem inventory untuk skills dan passives.
"""
from typing import Optional


class Inventory:
    """
    Inventory system untuk Player
    Properties: __owner, __skills: list, __passives: list
    Methods: update(dt), add_upgrade(upgrade), apply_all_passives()
    """
    
    def __init__(self, owner):
        self.__owner = owner
        self.__skills = []
        self.__passives = []
        self.__max_skills = 6
        self.__max_passives = 6
    
    @property
    def skills(self):
        """Get list of skills"""
        return self.__skills.copy()
    
    @property
    def passives(self):
        """Get list of passives"""
        return self.__passives.copy()
    
    def update(self, dt):
        """Update all skills"""
        for skill in self.__skills:
            skill.update(dt)
    
    def add_upgrade(self, upgrade) -> bool:
        """
        Tambah upgrade baru atau level up yang sudah ada
        Returns: True jika berhasil, False jika inventory penuh
        """
        # Import here to avoid circular imports
        from src.combat.mechanics import Skill, PassiveItem
        
        # Check if upgrade already exists
        if isinstance(upgrade, Skill):
            existing_skill = self._find_skill_by_name(upgrade.name)
            if existing_skill:
                # Level up existing skill
                if existing_skill.can_level_up():
                    existing_skill.level_up()
                    return True
                return False
            else:
                # Add new skill
                if len(self.__skills) < self.__max_skills:
                    self.__skills.append(upgrade)
                    return True
                return False
        
        elif isinstance(upgrade, PassiveItem):
            existing_passive = self._find_passive_by_name(upgrade.name)
            if existing_passive:
                # Level up existing passive
                if existing_passive.can_level_up():
                    existing_passive.level_up()
                    self.apply_all_passives()  # Reapply all passives
                    return True
                return False
            else:
                # Add new passive
                if len(self.__passives) < self.__max_passives:
                    self.__passives.append(upgrade)
                    self.apply_all_passives()  # Apply new passive
                    return True
                return False
        
        return False
    
    def _find_skill_by_name(self, name: str) -> Optional[object]:
        """Find skill by name"""
        for skill in self.__skills:
            if skill.name == name:
                return skill
        return None
    
    def _find_passive_by_name(self, name: str) -> Optional[object]:
        """Find passive by name"""
        for passive in self.__passives:
            if passive.name == name:
                return passive
        return None
    
    def apply_all_passives(self):
        """Apply all passive stats to owner"""
        for passive in self.__passives:
            passive.apply_stat(self.__owner)
    
    def get_upgrade_count(self) -> int:
        """Get total number of upgrades"""
        return len(self.__skills) + len(self.__passives)
    
    def is_skill_full(self) -> bool:
        """Check if skill inventory is full"""
        return len(self.__skills) >= self.__max_skills
    
    def is_passive_full(self) -> bool:
        """Check if passive inventory is full"""
        return len(self.__passives) >= self.__max_passives
