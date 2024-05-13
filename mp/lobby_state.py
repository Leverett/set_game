from game.game_objects import Identity, Rules
from host.serialization import GameSerializable
from game.globals import *

class LobbyState(GameSerializable):

    def __init__(self, host: Identity, rules: Rules, players: list[Identity] = None):
        self.host: Identity = host
        self.players: list[Identity] = [self.host] if players is None else players
        self.rules: Rules = rules

    def is_full(self) -> bool:
        return len(self.players) >= MAX_PLAYERS


    def to_json(self) -> dict:
        return {
            'host': self.host.to_json(),
            'rules': self.to_json(),
            'players': [player.to_json() for player in self.players],
        }

    @classmethod
    def from_json(cls, json_data: dict):
        host = Identity.from_json(json_data['host'])
        rules = Rules.from_json(json_data['rules'])
        players = [Identity.from_json(player) for player in json_data['players']]

        return LobbyState(host, rules, players=players)