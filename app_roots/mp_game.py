from app_roots.game_base import SetGame
from kivy.app import App
from game.game_state import GameState
from widgets.game_stats_display import GameStatsDisplay
from widgets.card_image import HighlightedImage
from widgets.sp.game_stats_widgets import SPStatsDisplay
from mp.remote_manager import RemoteGameManager
from kivy.uix.popup import Popup
from kivy.lang import Builder
from game.game_objects import GameMode, Rules
from game.globals import *


Builder.load_file('widgets/sp/gameover_popup.kv')

class MPGame(SetGame):
    def __init__(self, game_id: str, game_state: GameState, rules: Rules):
        manager = RemoteGameManager(game_id)
        super().__init__(manager, game_state, rules)

    def refresh(self):
        pass

    def make_game_stats_display(self) -> GameStatsDisplay:
        return SPStatsDisplay(self.rules)
    
    def quit(self):
        self.app.go_home()

    def title(self):
        return "Solitaire"
    
    def game_over(self):
        GameOverPopup().open()

    # Only for testing
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

class GameOverPopup(Popup):

    def new_game(self):
        App.get_running_app().start_game(GameMode.SINGLE_PLAYER)
        self.dismiss()

    def quit(self):
        App.get_running_app().go_home()
        self.dismiss()
