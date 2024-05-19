from kivy.app import App
from kivy.lang import Builder
from game.globals import *
import requests
from host.instance import RejectionReason
from mp.lobby_state import LobbyState
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty
from game.game_objects import Rules, Identity
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.label import Label

Builder.load_file('app_roots/layouts/lobbies.kv')


class Lobbies(FloatLayout):
    def __init__(self, lobbies: dict[str, LobbyState], **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.lobbies: dict[str, LobbyState] = lobbies
        self.lobby_boxes: dict[str, LobbyBox] = {}
        self.lobbies_list: BoxLayout = None

        #Testing only
        if len(self.lobbies) == 0:
            self.lobbies[test_lobby_id] = LobbyState(test_lobby_id, Identity(test_id, test_name), Rules.default_rules())
        
        Clock.schedule_once(self._on_widget_ready)

    def _on_widget_ready(self, dt):
        self.lobbies_list: BoxLayout = self.ids.lobbies_list
        for lobby in self.lobbies.values():
            self.add_lobby(lobby)

    def add_lobby(self, lobby: LobbyState):
        lobby_box = LobbyBox(lobby)
        lobby_box.bind(on_touch_down=self.on_lobby_click)
        self.lobbies_list.add_widget(lobby_box)
        self.lobby_boxes[lobby.id] = lobby_box

    def remove_lobby(self, lobby_id: str):
            self.lobbies_list.remove_widget(self.lobby_boxes[lobby_id])
            del self.lobby_boxes[lobby_id]

    def update_lobbies(self):
        for id, lobby_box in self.lobby_boxes.items():
            if id in self.lobbies:
                lobby_box.num_players = len(self.lobbies[id].players)
            else:
                self.remove_widget(id)
        for id, lobby in self.lobbies:
            if id not in self.lobby_boxes:
                self.add_lobby(lobby)

    def on_lobby_click(self, instance, touch):
        if instance.collide_point(*touch.pos):
            lobby_id: str = instance.lobby_id
            request_payload = make_request_payload(instance=lobby_id)
            response = requests.post(get_url(f"join_lobby/{instance.lobby_id}"), json=request_payload)
            response_payload = response.json()
            if response_payload[SUCCESS_KEY]:
                lobby_state = LobbyState.from_json(response_payload[LOBBY_STATE_KEY])
                self.app.open_lobby(lobby_state)
            else:
                reason = RejectionReason.ensure(response_payload[REASON_KEY])
                self.show_rejection_notification(reason, instance.pos)

    def on_back_pressed(self):
        self.app.go_home()

    def on_new_game_pressed(self):
        request_payload = make_request_payload(rules=Rules.default_rules())
        response = requests.post(get_url('create_lobby'), json=request_payload)
        response_payload = response.json()
        lobby_state = LobbyState.from_json(response_payload[LOBBY_STATE_KEY])
        self.app.open_lobby(lobby_state)

    def show_rejection_notification(self, reason, loc):
        popup_label = Label(text=f"This is a popup! {reason}", size_hint=(None, None), size=(200, 50),
                            pos_hint=loc,
                            opacity=0)
        self.add_widget(popup_label)

        anim = Animation(opacity=1, duration=0.5) + Animation(opacity=0, duration=2)
        anim.bind(on_complete=lambda *args: self.remove_widget(popup_label))
        anim.start(popup_label)

class LobbyBox(BoxLayout):
    lobby_id = StringProperty("")
    name = StringProperty("")
    num_players = NumericProperty(0)
    def __init__(self, lobby: LobbyState, **kwargs):
        super().__init__(**kwargs)
        self.lobby_id = lobby.id
        self.name = lobby.name()
        self.num_players = len(lobby.players)


def make_request_payload(**kwargs):
        request_payload = {key: value if isinstance(value, str) else value.to_json() for key, value in kwargs.items()}
        request_payload[PLAYER_KEY] = App.get_running_app().get_identity().to_json()
        return request_payload

def get_lobbies() -> dict[str, LobbyState]:
    request_payload = make_request_payload()
    response = requests.get(get_url('get_lobbies'), json=request_payload)
    return get_lobbies_from_response(response)
    
def get_lobbies_from_response(response) -> dict[str, LobbyState]:
    response_payload = response.json()
    if not response_payload[SUCCESS_KEY]:
        print(f"Failed to get lobbies. API response: {response_payload}")
        return {}
    else:
        return {lobby['id']: LobbyState.from_json(lobby) for lobby in response.json()[LOBBIES_KEY]}

