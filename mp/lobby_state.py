from game.game_objects import Identity, Rules
from host.serialization import GameSerializable
from game.globals import *

class LobbyState(GameSerializable):

    def __init__(self, id: str, host: Identity, rules: Rules, players: list[Identity] = None, is_started: bool = False):
        self.id:str = id
        self.host: Identity = host
        self.players: list[Identity] = [self.host] if players is None else players
        self.rules: Rules = rules
        self.is_started: bool = is_started

    def is_full(self) -> bool:
        return len(self.players) >= MAX_PLAYERS
    
    def name(self):
        return f"{self.host.name}'s Game"
    
    def is_host(self, player: Identity):
        return self.host == player

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'host': self.host.to_json(),
            'rules': self.rules.to_json(),
            'players': [player.to_json() for player in self.players],
            'is_started': self.is_started,
        }

    @classmethod
    def from_json(cls, json_data: dict):
        id = json_data['id']
        host = Identity.from_json(json_data['host'])
        rules = Rules.from_json(json_data['rules'])
        players = [Identity.from_json(player) for player in json_data['players']]
        is_started = json_data['is_started']

        return LobbyState(id, host, rules, players=players, is_started=is_started)