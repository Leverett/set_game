import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
game_dir = os.path.join(os.path.dirname(current_dir), 'game')
sys.path.insert(0, game_dir)


class GameInstance:
    def __init__(self, lobby):
        self.play