import os
import sys
from time import time
current_dir = os.path.dirname(os.path.abspath(__file__))
game_dir = os.path.join(os.path.dirname(current_dir), 'game')
sys.path.insert(0, game_dir)
from game.game_objects import Player, Rules
from mp.lobby import Lobby
from mp.lobby_events import *
from game.globals import MAX_PLAYERS


class LobbyInstance(Lobby):
    def __init__(self, host, rules):
        super().__init__(host, rules)
        self.rules_updated = time()
        self.players_updated = time()
        self.game_started = False
        
    def is_full(self):
        return len(self.players) >= MAX_PLAYERS

    def add_player(self, player):
        if not self.is_full():
            if player not in self.players:
                self.players.append(player)
                self.players_updated = time()
            return LobbyEvent(self)
        return LobbyRejected(Reason.FULL)

    def remove_player(self, player):
        self.players.remove(player)

    def update_rules(self, new_rules, timestamp):
        if timestamp > self.rules_updated:
            self.rules = new_rules
            self.rules_updated = timestamp
    
    def get_lobby(self):
        lobby_copy = Lobby(self.host, self.rules, started=self.started)
        lobby_copy.players = self.players
        return lobby_copy


