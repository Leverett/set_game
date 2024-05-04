from copy import deepcopy
from kivy.uix.boxlayout import BoxLayout
from app_roots.game_base import *
from kivy.app import App


Builder.load_file('widgets/sp_gameover_popup.kv')

class SPGame(SetGame):
    def __init__(self, rules):
        manager = LocalGameManager(rules, {default_id: Player(default_id, default_name)})
        super().__init__(manager, deepcopy(manager.game_state), player_id=default_id)

    def refresh(self):
        pass

    def do_set_action(self, action):
        events = self.manager.handle_action(action)
        self.selected_cards.clear()
        self.reset_card_opacity()
        if len(events) > 0:
            event = events[0]
            self.game_state.process_event(event)
            if type(event) is ValidSetEvent:
                self.hints.clear()
            self.display_cards()
            self.update_game_stats()
            if type(event) is ValidSetEvent and event.game_over:
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

    def make_game_stats_display(self) -> BoxLayout:
        rules = self.manager.rules
        return  SPScoreStatsDisplay(self.manager.rules) if rules.punish_missed_sets or rules.punish_missed_empties else SPBasicStatsDisplay()
    
    def game_over(self):
        GameOverPopup().open()

class GameOverPopup(Popup):

    def new_game(self):
        App.get_running_app().start_game(CONFIG_SP_RULES)
        self.dismiss()

    def quit(self):
        App.get_running_app().go_home()
        self.dismiss()

    