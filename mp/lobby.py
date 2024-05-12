from mp.identity import Identity


class Lobby:

    def __init__(self, host, rules, started=False):
        self.host = host
        self.players = [self.host]
        self.rules = rules
        self.started = started

    def lobby_id(self):
        return f"lid_{self.host.player_id}"
    
    def name(self):
        return f"{self.host.name}'s Game"