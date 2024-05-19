from app_roots.game_base import SetGame
from kivy.app import App
from widgets.game_stats_display import GameStatsDisplay
from widgets.card_image import HighlightedImage
from widgets.sp.game_stats_widgets import SPStatsDisplay
from game.management import GameManager, LocalGameManager
from kivy.uix.popup import Popup
from game.game_objects import Rules, GameMode
from game.globals import *


class SPGame(SetGame):
    def __init__(self, rules: Rules):
        manager: GameManager = LocalGameManager(rules, [App.get_running_app().get_identity()])
        game_state, rules = manager.get_current_game()
        super().__init__(manager, game_state, rules)

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
        self.app.go_home()

    def title(self) -> str:
        return "Solitaire"
    
    def game_over(self):
        popup = GameOverPopup()
        popup.open()

class GameOverPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def new_game(self):
        self.app.start_game(GameMode.SINGLE_PLAYER)
        self.dismiss()

    def quit(self):
        self.app.go_home()
        self.dismiss()
