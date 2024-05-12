from enum import StrEnum

MAX_PLAYERS = 12
SET_SIZE = 3
STANDARD_FIELD_SIZE = 12

default_id = "id1"
default_name = "leverett"

GRID_WIDTH = 3
HINT_FLASHES = 3
HIGHLIGHT_COLOR = (1, 0, 0, 0.69)
FLASH_COLOR = (1, 0, 0, 1)
FLASH_INTERVAL = 0.12
GAME_OVER = "Game Over"

CONFIG_FILE = "config.ini"

class GameMode(StrEnum):
    SINGLE_PLAYER = "sp"
    MULTI_PLAYER = "mp"

class Rule(StrEnum):
    PUNISH_MISSED_SETS = "punish_missed_sets"
    PUNISH_MISSED_EMPTIES = "punish_missed_empties"
    ENABLE_HINTS = "enable_hints"
    ENDLESS_MODE = "endless_mode"

# host_ip = '0.0.0.0'
host_ip = '127.0.0.1'

def get_url(api):
    return f"http://{host_ip}:5000/{api}"