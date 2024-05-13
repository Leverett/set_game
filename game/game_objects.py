from game.globals import *
from itertools import product, combinations
from typing import Self
from host.serialization import GameSerializable


class Color(EnsurableEnum):
    RED = 'r'
    GREEN = 'g'
    PURPLE = 'p'

class Symbol(EnsurableEnum):
    OVAL = 'o'
    DIAMOND = 'd'
    SQUIGGLE = 's'

class Shading(EnsurableEnum):
    FILLED = 'f'
    STRIPED = 's'
    EMPTY = 'e'

class Number(EnsurableEnum):
    ONE = '1'
    TWO = '2'
    THREE = '3'

class Card(GameSerializable):
    def __init__(self, color: Color, symbol: Symbol, shading: Shading, number: Number):
        self.color: Color = Color.ensure(color)
        self.symbol: Symbol = Symbol.ensure(symbol)
        self.shading: Shading = Shading.ensure(shading)
        self.number: Number = Number.ensure(number)

    def to_tuple(self):
        return (self.color, self.symbol, self.shading, self.number)

    def __repr__(self):
        return f"{self.color}{self.symbol}{self.shading}{self.number}"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.to_tuple() == other.to_tuple()

    def __hash__(self):
        return hash(self.to_tuple())

    def __contains__(self, item):
        if not isinstance(item, Card):
            return False
        return self == item
    
    def to_json(self) -> dict:
        return {
            'color': self.color,
            'symbol': self.symbol,
            'shading': self.shading,
            'number': self.number
        }

    @classmethod
    def from_json(cls, json_data: dict) -> Self:
        return cls(**json_data)
    
def card_image_source(card):
    return f"images/{card}.png"


def is_feature_valid(value1, value2, value3):
    if value1 == value2 == value3:
        return True
    elif value1 != value2 and value2 != value3 and value1 != value3:
        return True
    else:
        return False

def is_set(card1: Card, card2: Card, card3: Card) -> bool:
    features = ['symbol', 'color', 'number', 'shading']
    for feature in features:
        if not is_feature_valid(getattr(card1, feature), getattr(card2, feature), getattr(card3, feature)):
            return False
    return True

def contains_set(cards):
    for set in combinations(cards, 3):
        if (is_set(*set)):
            return True
    return False

FEATURES = [Color, Symbol, Shading, Number]
def all_cards() -> list[Card]:
    return [Card(*features) for features in list(product(*FEATURES))]

class Identity(GameSerializable):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Identity):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __contains__(self, item):
        if not isinstance(item, Identity):
            return False
        return self == item
    
    def to_dict(self) -> dict:
        return {
            'player_id': self.id,
            'player_name': self.name
        }
    
    def to_json(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
        }
    
    @classmethod
    def from_json(cls, json_data: dict) -> Self:
        id = json_data['id']
        name = json_data['name']
        return cls(id, name)

class Player(Identity):
    def __init__(self, identity: Identity,
                 sets: list[list[Card]] = [], missed_sets: int = 0, missed_empties: int = 0):
        super().__init__(identity.id, identity.name)
        self.sets: list[list[Card]] = sets
        self.missed_sets: int = missed_sets
        self.missed_empties: int = missed_empties

    def score(self) -> int:
        return len(self.sets) - self.missed_sets - self.missed_empties
    
    def misses(self) -> int:
        return self.missed_sets + self.missed_empties
    
    def to_json(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'sets': [[card.to_json() for card in valid_set] for valid_set in self.sets],
            'missed_sets': self.missed_sets,
            'missed_empties': self.missed_empties,
        }
    
    @classmethod
    def from_json(cls, json_data: dict) -> Self:
        id = json_data['id']
        name = json_data['name']
        
        sets_data = json_data.get('sets', [])
        sets = [[Card.from_json(card) for card in valid_set] for valid_set in sets_data]

        missed_sets = json_data.get('missed_sets', 0)
        missed_empties = json_data.get('missed_empties', 0)
        
        return cls(Identity(id, name), sets=sets, missed_sets=missed_sets, missed_empties=missed_empties)

class Rules(GameSerializable):
    def __init__(self, punish_missed_sets: bool, punish_missed_empties: bool, enable_hints: bool, endless_mode: bool):
        self.punish_missed_sets: bool = punish_missed_sets
        self.punish_missed_empties: bool = punish_missed_empties
        self.enable_hints: bool = enable_hints
        self.endless_mode: bool = endless_mode

    def count_misses(self) -> bool:
        return self.punish_missed_sets or self.punish_missed_empties

    def default_rules():
        return Rules(True, True, False, False)

    def to_dict(self):
        return {rule: getattr(self, rule.value) for rule in Rule}
    
    def to_json(self) -> dict:
        return self.to_dict()
        
    @classmethod
    def from_json(cls, json_data: dict):
        return Rules(**json_data)
        # instance = cls(**json_data)
        # for key, value in json_data.items():
        #     setattr(instance, key, value)
        # return instance

class MissingEventException(Exception):
    def __init__(self, event_index: int, current_num_events: int):
        super().__init__(self, f"Given event index: {event_index}, Number of events: {current_num_events}")
