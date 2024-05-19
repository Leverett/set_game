from enum import StrEnum

MAX_PLAYERS = 12
SET_SIZE = 3
STANDARD_FIELD_SIZE = 12

default_id = "id1"
default_name = "leverett"
local_game_id = "local"

#Testing
test_id = "test_id"
test_name = "Test Host"
test_lobby_id = "test_lobby"

SUCCESS_KEY = 'success'
ACTION_KEY = 'action'
EVENTS_KEY = 'events'
TIMESTAMP_KEY = 'timestamp'
PLAYER_KEY = 'player'
INSTANCE_KEY = 'instance'
RULES_KEY = 'rules'
GAME_STATE_KEY = 'game_state'
LOBBIES_KEY = 'lobbies'
LOBBY_STATE_KEY = 'lobby_state'
REASON_KEY = 'reason'


GRID_WIDTH = 3
HINT_FLASHES = 3
HIGHLIGHT_COLOR = (1, 0, 0, 0.69)
FLASH_COLOR = (1, 0, 0, 1)
FLASH_INTERVAL = 0.12
GAME_OVER = "Game Over"

CONFIG_FILE = "config.ini"


# host_ip = '0.0.0.0'
host_ip = '127.0.0.1'

def get_url(api):
    return f"http://{host_ip}:5000/{api}"


class EnsurableEnum(StrEnum):
    @classmethod
    def ensure(cls, value):
        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"{value} is not a valid {cls.__name__}")

class GameMode(EnsurableEnum):
    SINGLE_PLAYER = "sp"
    MULTI_PLAYER = "mp"

class Rule(EnsurableEnum):
    PUNISH_MISSED_SETS = "punish_missed_sets"
    PUNISH_MISSED_EMPTIES = "punish_missed_empties"
    ENABLE_HINTS = "enable_hints"
    ENDLESS_MODE = "endless_mode"