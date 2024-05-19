from game.events import Action, Event
from game.game_state import GameState
from game.management import GameManager
import requests
from game.globals import *
from game.game_objects import Rules
from time import time


class RemoteGameManager(GameManager):
    def __init__(self, game_id):
        self.game_id = game_id
    
    def handle_action(self, action: Action) -> list[Event]:
        response = requests.post(get_url(f"action/{self.game_id}"), json=make_request_payload(action=action))
        response_data = response.json()
        events_data = response_data[EVENTS_KEY]
        events = [Event.from_json(event) for event in events_data]
        return events
    
    def get_events(self) -> list[Event]:
        response = requests.get(get_url(f"events/{self.game_id}"))
        response_data = response.json()
        events_data = response_data[EVENTS_KEY]
        events = [Event.from_json(event) for event in events_data]
        return events
    
    def get_current_game(self) -> tuple[GameState, Rules]:
        response = requests.get(get_url(f"current_game/{self.game_id}"))
        response_data = response.json()
        game_state_data = response_data[GAME_STATE_KEY]
        game_state = GameState.from_json(game_state_data)
        rules_data = response_data[RULES_KEY]
        rules = Rules.from_json(rules_data)
        return game_state, rules


def make_request_payload(**kwargs):
        request_payload = {key: value if isinstance(value, str) else value.to_json() for key, value in kwargs.items()}
        request_payload[TIMESTAMP_KEY] = time()
        return request_payload