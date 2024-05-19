from tkinter import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.label import Label
from app_roots.lobbies import get_lobbies_from_response, make_request_payload
from game.game_objects import Identity, Rules
from game.game_state import GameState
from mp.lobby_state import LobbyState
from widgets.game_settings import GameSettings
from game.globals import *
from kivy.clock import Clock
import requests

Builder.load_file('app_roots/layouts/lobby.kv')


class Lobby(BoxLayout):
    def __init__(self, lobby_state: LobbyState, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.lobby_state: LobbyState = lobby_state
        self.is_host = self.lobby_state.host == self.app.get_identity()
        Clock.schedule_once(self._on_widget_ready)

    def _on_widget_ready(self, dt):
        self.ids.title_label.text = self.lobby_name()
        self.game_settings: GameSettings = self.ids.game_settings
        self.players_list: BoxLayout = self.ids.players_list
        host_label = self.make_player_label(self.host())
        self.players_list.add_widget(host_label, index=1)
        if not self.is_host:
            self_label = self.make_player_label(self.app.get_identity())
            self.players_list.add_widget(self_label, index=1)
            self.remove_widget(self.ids.start_button)
        self.other_player_labels = {}
        self.update_lobby()


    def update_lobby(self):
        self.update_rules()
        self.update_players()

    def update_rules(self):
        self.game_settings.update_opts()

    def update_players(self):
        other_players = self.other_players()
        for player in other_players:
            if player not in self.other_player_labels:
                self.add_player(player)
        for id, label in self.other_player_labels.items():
            if id not in other_players:
                self.players_list.remove_widget(label)
                del self.other_player_labels[id]
    
    def add_player(self, player: Identity):
        if player not in self.other_player_labels:
            player_label = self.make_player_label(player)
            self.other_player_labels[player] = player_label
            self.players_list.add_widget(player_label, index=1)

    def other_players(self) -> list[Identity]:
        return [player for player in self.lobby_state.players if (player != self.host() and player != self.app.get_identity())]
    
    def make_player_label(self, player: Identity) -> Label:
        return PlayerLabel(player,
                           is_host=(player == self.host()),
                           is_self=(player == self.app.get_identity()),
                           size_hint_y=None,
                           height='40dp')
    
    def on_exit_pressed(self):
        request_payload = make_request_payload()
        response = requests.post(get_url(f"leave_lobby/{self.lobby_state.id}"), json=request_payload)
        lobbies: dict[str, LobbyState] = get_lobbies_from_response(response)
        self.app.open_lobbies(lobbies)

    def on_start_press(self):
        response = requests.post(get_url(f"start_game/{self.lobby_state.id}"))
        response_data = response.json()
        game_state_data = response_data[GAME_STATE_KEY]
        game_state = GameState.from_json(game_state_data)
        rules_data = response_data[RULES_KEY]
        rules = Rules.from_json(rules_data)
        self.app.start_mp_game(self.lobby_state.id, game_state, rules)

    def host(self) -> Identity:
        return self.lobby_state.host
    
    def lobby_name(self):
        return self.host().name
    
class GameSettingsInLobby(GameSettings):
    pass

class PlayerLabel(Label):
    def __init__(self, player: Identity, is_host=False, is_self=False,  **kwargs):
        super().__init__(**kwargs)
        self.player: Identity = player
        self.text = f"{player.name} (host)" if is_host else player.name
        self.size_hint_x = 0.5
        if is_self:
            self.color = [0, 1, 0, 1]
    



