from app_roots.game_base import SetGame
from kivy.app import App
from widgets.game_stats_display import GameStatsDisplay
from widgets.grid_display import HighlightedImage
from widgets.sp.game_stats_widgets import SPStatsDisplay
from mp.remote_manager import RemoteGameManager
from kivy.uix.popup import Popup
from kivy.lang import Builder
from game.game_objects import Player
from game.globals import *
from game.events import EventType


Builder.load_file('widgets/sp/gameover_popup.kv')

class MPGame(SetGame):
    def __init__(self, player: Player):
        manager = RemoteGameManager(player, "game_id")
        game_state = manager.get_game_state()
        super().__init__(manager, game_state, player_id=default_id)

    def refresh(self):
        pass

    def do_set_action(self, action):
        events = self.manager.handle_action(action)
        self.selected_cards.clear()
        self.reset_card_opacity()
        if len(events) > 0:
            event = events[0]
            self.game_state.process_event(event)
            if event.etype is EventType.VALID_SET_EVENT:
                self.hints.clear()
            self.display_cards()
            self.update_game_stats()
            if event.etype is EventType.VALID_SET_EVENT and event.game_over:
                self.game_over()

    def do_add_cards_action(self, action):
        events = self.manager.handle_action(action)
        self.selected_cards.clear()
        self.reset_card_opacity()
        if len(events) > 0:
            self.game_state.process_event(events[0])
            self.display_cards()
            self.update_game_stats()

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
        return SPStatsDisplay(self.manager.rules)
    
    def quit(self):
        App.get_running_app().go_home()

    def title(self):
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
