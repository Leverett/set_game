from time import time
from enum import Enum
from game.game_objects import Card
from typing import List
from host.serialization import GameSerializable


class ActionType(Enum):
    CALL_EMPTY = "call_empty"
    CALL_SET = "call_set"

class Action(GameSerializable):
    def __init__(self, atype: ActionType, player_id: str,
                 timestamp: int = None, cards: List[Card] = []):
        self.atype: ActionType = atype
        self.player_id: str = player_id
        self.timestamp: int = time() if timestamp is None else timestamp
        self.cards: List[Card] = cards
    
    def __repr__(self) -> str:
        return f"{self.atype} - {self.player_id} - {self.timestamp} - {self.cards}"
    
    def to_json(self) -> dict:
        return {
            'atype': self.atype,
            'player_id': self.player_id,
            'timestamp': self.timestamp,
            'cards': [card.from_json() for card in self.cards],
        }
    
    @classmethod
    def from_json(cls, json_data: dict):
        atype = json_data['atype']
        player_id = json_data['player_id']
        timestamp = json_data['timestamp']
        
        cards_data = json_data.get('cards', [])
        cards = [Card.from_json(card) for card in cards_data]
        
        return cls(atype, player_id, timestamp=timestamp,
                   cards=cards)

class EventType(Enum):
    VALID_SET_EVENT = "valid_set_event"
    INVALID_SET_EVENT = "invalid_set_event"
    VALID_CALL_EMPTY_EVENT = "valid_call_empty_event"
    INVALID_CALL_EMPTY_EVENT = "invalid_call_empty_event"

class Event(GameSerializable):
    def __init__(self, etype: EventType, player_id: str, timestamp: int, event_num: int,
                 selected_cards: List[Card] = [], replacement_cards: List[Card] = [], drawn_cards: List[Card] = [],
                 game_over=False):
        self.etype: EventType = etype
        self.player_id: str = player_id
        self.timestamp: int = timestamp
        self.event_num: int = event_num
        self.selected_cards: List[Card] = selected_cards
        self.replacement_cards: List[Card] = replacement_cards
        self.drawn_cards: List[Card] = drawn_cards
        self.game_over: bool = game_over
    
    def __repr__(self) -> str:
        return f"{self.etype} - {self.player_id} - {self.timestamp} - {self.event_num}"
    
    def to_json(self) -> dict:
        return {
            'etype': self.etype,
            'player_id': self.player_id,
            'timestamp': self.timestamp,
            'event_num': self.event_num,
            'selected_cards': [card.to_json() for card in self.selected_cards],
            'replacement_cards': [card.to_json() for card in self.replacement_cards],
            'drawn_cards': [card.to_json() for card in self.drawn_cards],
            'game_over': self.game_over,
        }
    
    @classmethod
    def from_json(cls, json_data: dict):
        etype = json_data['etype']
        player_id = json_data['player_id']
        timestamp = json_data['timestamp']
        event_num = json_data['event_num']
        
        selected_cards_data = json_data.get('selected_cards', [])
        selected_cards = [Card.from_json(card) for card in selected_cards_data]
        replacement_cards_data = json_data.get('replacement_cards', [])
        replacement_cards = [Card.from_json(card) for card in replacement_cards_data]
        drawn_cards_data = json_data.get('drawn_cards', [])
        drawn_cards = [Card.from_json(card) for card in drawn_cards_data]

        game_over = json_data['game_over']
        
        return cls(etype, player_id, timestamp, event_num,
                   selected_cards=selected_cards, replacement_cards=replacement_cards, drawn_cards=drawn_cards,
                   game_over=game_over)
