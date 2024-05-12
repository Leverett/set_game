from game.events import Action, Event
from typing import List
from game.game_state import GameState
from game.management import GameManager
import requests
from game.globals import *
from host.serialization import serialize_to_json, deserialize_from_json
from game.game_objects import Rules




class RemoteGameManager(GameManager):
    def __init__(self, player, game_id):
        self.player = player
        self.game_id = game_id
        self.rules = Rules.default_rules()
    
    def handle_action(self, action: Action) -> List[Event]:
        action_payload = serialize_to_json(action)
        events_payload = requests.post(get_url('action'), json=action_payload)
        events = [Event(**event) for event in events_payload]
        return events
    
    def get_events(self, timestamp: int) -> List[Event]:
        request_payload = {'timestamp': timestamp}
        events_payload = requests.get(get_url('events'), json=request_payload)
        events = [Event(**event) for event in events_payload]
        return events
    
    def get_game_state(self) -> GameState:
        response = requests.get(get_url('game_state'))
        game_state_payload = response.json()
        game_state = GameState.from_json(game_state_payload)
        return game_state
