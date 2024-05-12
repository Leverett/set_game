
from game.management import GameState


class Lobby:
    def __init__(self, host, rules):
        self.host = host
        self.players = [self.host]
        self.rules = rules
        self.started = False

    def is_host(self, player_id):
        return player_id == self.players[0]
    
    def get_host(self):
        return self.players[0]

    def make_game(self):
        self.started = True
        return GameState(self.players, self.punish_missed_sets, self.punish_missed_empties)
    
    def name(self):
        return f"{self.host.name}'s Game"