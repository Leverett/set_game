from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.popup import Popup
from mp.lobby_state import LobbyState
from widgets.game_settings import GameSettings
from game.globals import *
from app_roots.lobbies import get_lobbies

Builder.load_file('app_roots/layouts/home_screen.kv')
Builder.load_file('widgets/game_settings_popup.kv')

class GameSettingsInPopup(GameSettings):
    pass

class GameSettingsPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def on_start_game_press(self):
        self.app.start_sp_game()
        self.dismiss()


class HomeScreen(BoxLayout):
    def __init__(self):
        super().__init__()
        self.app = App.get_running_app()
        
    def start_sp_press(self):
        popup = GameSettingsPopup()
        popup.open()

    def start_mp_press(self):
        lobbies: dict[str, LobbyState] = get_lobbies()
        self.app.open_lobbies(lobbies)

    