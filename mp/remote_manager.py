from game.events import Action, Event
from game.game_state import GameState
from game.management import GameManager
import requests
from game.globals import *
from game.game_objects import Rules
from time import time


class RemoteGameManager(GameManager):
    def __init__(self, player, game_id):
        self.player = player
        self.game_id = game_id
    
    def handle_action(self, action: Action) -> list[Event]:
        response = requests.post(get_url('action'), json=self.make_request_payload(action=action))
        response_data = response.json()
        events_data = response_data['events']
        events = [Event.from_json(event) for event in events_data]
        return events
    
    def get_events(self) -> list[Event]:
        response = requests.get(get_url('events'), json=self.make_request_payload())
        response_data = response.json()
        events_data = response_data['events']
        events = [Event.from_json(event) for event in events_data]
        return events
    
    def get_current_game(self) -> tuple[GameState, Rules]:
        response = requests.get(get_url('current_game'), json=self.make_request_payload())
        response_data = response.json()
        game_state_data = response_data['game_state']
        game_state = GameState.from_json(game_state_data)
        rules_data = response_data['rules']
        rules = Rules.from_json(rules_data)
        return game_state, rules
    
    def make_request_payload(self, **kwargs):
        request_payload = {
            'timestamp': time(),
            'game_id': self.game_id,
        }
        for key, value in kwargs.items():
            request_payload[key] = value.to_json()
        return request_payload

