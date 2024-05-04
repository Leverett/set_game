from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from app_roots.sp_game import SPGame
from app_roots.game_base import *
from kivy.lang import Builder
from widgets.game_settings import GameSettings
from game.constants import *

Builder.load_file('layouts/home_screen.kv')
Builder.load_file('widgets/game_settings_popup.kv')

class GameSettingsPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def get_rule(self, rule):
        return self.app.config[CONFIG_SP_RULES][rule].lower() in ['true', 'yes', '1']
    
    def make_rules(self):
        return Rules(self.get_rule(PUNISH_MISSED_SETS), self.get_rule(PUNISH_MISSED_EMPTIES), self.get_rule(ENABLE_HINTS), self.get_rule(ENDLESS_MODE))

    def start_game(self):
        rules = Rules(self.get_rule(PUNISH_MISSED_SETS), self.get_rule(PUNISH_MISSED_EMPTIES), self.get_rule(ENABLE_HINTS), self.get_rule(ENDLESS_MODE))
        print(f"Rules: {rules}")
        self.app.switch_root(SPGame(rules))
        self.dismiss()


class HomeScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def start_sp_press(self):
        popup = GameSettingsPopup()
        popup.open()

    