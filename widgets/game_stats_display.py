from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from game.game_objects import Player
from game.game_state import GameState
from abc import abstractmethod
from kivy.uix.widget import Widget


class GameStatsDisplay(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_game_stats(self, game_state: GameState, player: Player):
        for child in self.children:
            child.update_stats(game_state, player)

class GameStatsWidget(Widget):

    @abstractmethod
    def update_stats(self, game_state: GameState, player: Player):
        pass