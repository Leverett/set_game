import os
import sys
sys.path.append(os.getcwd())
from game.game_objects import Identity, Rules
from mp.lobby_state import LobbyState
from game.management import LocalGameManager
from game.globals import *

class Instance:
    def __init__(self, lobby_state: LobbyState, manager: LocalGameManager = None):
        self.id: str = lobby_state.id
        self.lobby_state: LobbyState = lobby_state
        self.manager: LocalGameManager = manager
    
    def is_started(self):
        return self.manager is not None
    
    def is_done(self):
        if self.is_started():
            return self.manager.game_state.game_over
        return False
        
    def is_full(self) -> bool:
        return self.lobby_state.is_full()
    
    def has_player(self, player: Identity):
        return player in self.lobby_state.players
    
    def is_host(self, player):
        return self.lobby_state.is_host(player)

    def add_player(self, player: Identity):
        if player not in self.lobby_state.players:
            self.lobby_state.players.append(player)

    def remove_player(self, player) -> bool:
        self.lobby_state.players.remove(player)

    def start_game(self):
        self.manager = LocalGameManager(self.lobby_state.rules, self.lobby_state.players)

class RejectionReason(EnsurableEnum):
    FULL = "full"
    STARTED = "started"
    CLOSED = "closed"
