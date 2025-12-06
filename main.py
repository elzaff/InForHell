"""
MAIN GAME - InForHell
Vampire Survivor-inspired game dengan arsitektur OOP.

Entry point untuk menjalankan game.
"""
from src.core.game import Game


if __name__ == '__main__':
    game = Game()
    game.run()
