import os
import sys
sys.path.append(os.getcwd())
from game.game_objects import Identity, Rules
from mp.lobby_state import LobbyState
from game.management import LocalGameManager
from typing import Self

class Instance:
    def __init__(self, id: str, host: Identity):
        self.id: str = id
        self.host: Identity = host
    
    def name(self):
        return f"{self.host.name}'s Game"

class LobbyInstance(Instance):
    def __init__(self, id: str, host: Identity, rules: Rules):
        super().__init__(id, host)
        self.lobby_state: LobbyState = LobbyState(host, rules)
        
    def is_full(self) -> bool:
        return self.lobby_state.is_full()

    def add_player(self, player: Identity) -> bool:
        if player not in self.lobby_state.players:
            self.lobby_state.players.append(player)
            return True
        return False

    def remove_player(self, player) -> bool:
        self.lobby_state.players.remove(player)
        return self.lobby_state.host in self.lobby_state.players

    def update_rules(self, new_rules, timestamp):
        if timestamp > self.rules_updated:
            self.rules = new_rules
            self.rules_updated = timestamp
    

class GameInstance(Instance):
    def __init__(self, id: str, host: Identity, rules: Rules, players: list[Identity]):
        super().__init__(id, host)
        self.manager: LocalGameManager = LocalGameManager(rules, players)

    @classmethod
    def from_lobby_instance(cls, lobby_instance: LobbyInstance) -> Self:
        return GameInstance(lobby_instance.id, lobby_instance.host, lobby_instance.lobby_state.rules, lobby_instance.lobby_state.players)
