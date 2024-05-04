from game.constants import MAX_PLAYERS
from game.game_objects import Player, DEFAULT_RULES
from game.management import SetGameState


class SetLobby:
    def __init__(self, player_id, player_name):
        self.players = []
        self.add_player(player_id, player_name)
        self.rules = DEFAULT_RULES
        self.started = False

    def add_player(self, player_id, player_name):
        if len(self.players) < MAX_PLAYERS:
            self.players.append(Player(player_id, player_name))

    def remove_player(self, player_id):
        if self.is_host(player_id):
            return False
        self.players = [player for player in self.players if player.id != player_id]
        return True

    def is_host(self, player_id):
        return player_id == self.players[0]
    
    def get_host(self):
        return self.players[0]

    def make_game(self):
        self.started = True
        return SetGameState(self.players, self.punish_missed_sets, self.punish_missed_empties)