from time import time
from game.game_objects import Card
# from typing import list
from host.serialization import GameSerializable
from game.globals import *


class ActionType(EnsurableEnum):
    CALL_EMPTY = "call_empty"
    CALL_SET = "call_set"

class Action(GameSerializable):
    def __init__(self, atype: ActionType, player_id: str,
                 cards: list[Card] = []):
        self.atype: ActionType = ActionType.ensure(atype)
        self.player_id: str = player_id
        self.cards: list[Card] = cards
    
    def __repr__(self) -> str:
        return f"{self.atype} - {self.player_id} - {self.cards}"
    
    def to_json(self) -> dict:
        return {
            'atype': self.atype,
            'player_id': self.player_id,
            'cards': [card.to_json() for card in self.cards],
        }
    
    @classmethod
    def from_json(cls, json_data: dict):
        atype = ActionType(json_data['atype'])
        player_id = json_data['player_id']
        
        cards_data = json_data.get('cards', [])
        cards = [Card.from_json(card) for card in cards_data]
        
        return cls(atype, player_id,
                   cards=cards)

class EventType(EnsurableEnum):
    VALID_SET_EVENT = "valid_set_event"
    INVALID_SET_EVENT = "invalid_set_event"
    VALID_CALL_EMPTY_EVENT = "valid_call_empty_event"
    INVALID_CALL_EMPTY_EVENT = "invalid_call_empty_event"

class Event(GameSerializable):
    def __init__(self, etype: EventType, player_id: str, timestamp: int, event_num: int,
                 selected_cards: list[Card] = [], replacement_cards: list[Card] = [], drawn_cards: list[Card] = [],
                 game_over=False):
        self.etype: EventType = EventType.ensure(etype)
        self.player_id: str = player_id
        self.timestamp: int = timestamp
        self.event_num: int = event_num
        self.selected_cards: list[Card] = selected_cards
        self.replacement_cards: list[Card] = replacement_cards
        self.drawn_cards: list[Card] = drawn_cards
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
