from enum import StrEnum
from time import time


class Reason(StrEnum):
    FULL = "full"
    ERROR = "error"
    KICKED = "kicked"
    CLOSED = "closed"

class LobbyEvent:
    def __init__(self, lobby):
        self.lobby = lobby

class JoinLobbyEvent(LobbyEvent):
    def __init__(self, lobby):
        super()._init__(lobby)
    
class Lobbies:
    def __init__(self, lobbies, games):
        self.lobbies = lobbies
        self.games = games
    
class LobbyRejected(Lobbies):
    def __init__(self, lobbies, games, reason):
        super()._init__(lobbies, games)
        self.reason = reason

# class LobbyStarted(Lobbies):
#     def _init__(self, lobbies, games, reason):
#         super()._init__(lobbies, games)

# class LobbyClosed(Lobbies):
#     def _init__(self, lobbies, games, reason):
#         super()._init__(lobbies, games)
#         self.reason = Reason.CLOSED
    
class GameStarting:
    def __init__(self, game_state):
        self.time = time()
        self.game_state = game_state


class RulesEvent:
    pass

class RulesUpdatedEvent(RulesEvent):
    def __init__(self):
        super().__init__()