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

    def start_game(self):
        self.app.start_game(GameMode.SINGLE_PLAYER)
        self.dismiss()


class HomeScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def start_sp_press(self):
        popup = GameSettingsPopup()
        popup.open()

    