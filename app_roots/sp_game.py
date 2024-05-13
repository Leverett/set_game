from app_roots.game_base import SetGame
from kivy.app import App
from widgets.game_stats_display import GameStatsDisplay
from widgets.grid_display import HighlightedImage
from widgets.sp.game_stats_widgets import SPStatsDisplay
from game.management import GameManager, LocalGameManager
from kivy.uix.popup import Popup
from kivy.lang import Builder
from game.game_objects import Player, Rules, GameMode
from game.globals import *


Builder.load_file('widgets/sp/gameover_popup.kv')

class SPGame(SetGame):
    def __init__(self, rules: Rules):
        player = Player(App.get_running_app().identity)
        manager: GameManager = LocalGameManager(rules, [player])
        game_state, rules = manager.get_current_game()
        super().__init__(manager, game_state, rules, player_id=default_id)

    def refresh(self):
        pass

    def do_hint(self):
        hint = self.game_state.get_hint(self.hints)
        if hint:
            self.hints.add(hint)
            self.display_cards()
        else:
            self.flash_hints()

    def flash_hints(self):
        for image in self.card_grid.children:
            if isinstance(image, HighlightedImage):
                image.flash_hint()

    def make_game_stats_display(self) -> GameStatsDisplay:
        return SPStatsDisplay(self.rules)
    
    def quit(self):
        App.get_running_app().go_home()

    def title(self) -> str:
        return "Solitaire"
    
    def game_over(self):
        GameOverPopup().open()

class GameOverPopup(Popup):

    def new_game(self):
        App.get_running_app().start_game(GameMode.SINGLE_PLAYER)
        self.dismiss()

    def quit(self):
        App.get_running_app().go_home()
        self.dismiss()
