from collections import defaultdict
import bisect
from game.events import Action, ActionType, Event, EventType
from game.game_objects import Rules, Player, Card, is_set
from game.game_state import GameState
from abc import ABC, abstractmethod
from game.deck import Deck, EndlessDeck, StandardDeck
from game.globals import *
from typing import List, Dict, DefaultDict, MutableSet


class GameManager(ABC):
    @abstractmethod
    def handle_action(self, action: Action) -> List[Event]:
        pass

    @abstractmethod
    def get_events(self, timestamp: int) -> List[Event]:
        pass

    @abstractmethod
    def get_game_state(self) -> GameState:
        pass

class LocalGameManager(GameManager):
    def __init__(self, rules: Rules, players: Dict[str,List[Player]]):
        self.deck: Deck = EndlessDeck() if rules.endless_mode else StandardDeck() #TODO make a builder that accepts a Rules object
        # self.deck: Deck = StackedDeck(expand_field_round=3)
        self.game_state: GameState = GameState(self.deck.initial_draw(), self.deck.remaining_cards(), players.values())
        if not rules:
            self.rules: Rules = Rules(True, False, True)
        else:
            self.rules: Rules = rules
        self.events: List[Event] = []
        self.round_missed_sets: DefaultDict[str,List[MutableSet]] = defaultdict(list)
    
    def handle_action(self, action: Action) -> List[Event]:
        if not self.events or self.events[-1].timestamp < action.timestamp:
            events = []
            if action.atype is ActionType.CALL_EMPTY:
                event = self.handle_call_empty(action)
                if event:
                    events.append(event)
            if action.atype is ActionType.CALL_SET:
                event = self.handle_call_set(action)
                if event:
                    events.append(event)
            if len(events) > 0:
                event = events[0]
                self.events.append(event)
                self.game_state.process_event(event)
            return events
        return self.get_events(action)
    
    def handle_call_set(self, action: Action) -> Event:
        cards = action.cards
        
        if is_set(*list(cards)):
            working_game_state = self.get_game_state()
            for card in cards:
                working_game_state.field.remove(card)
            full_field = len(working_game_state.field) >= STANDARD_FIELD_SIZE
            if full_field and working_game_state.is_set_showing():
                return self.valid_set_event(action, [], []) #TODO make sure to handle events without replacement cards
            
            
            replacement_cards = self.deck.draw_cards(working_game_state.field)
            working_game_state.field.extend(replacement_cards)
            drawn_cards = []
            while not working_game_state.is_set_showing():
                new_cards = self.deck.draw_cards(working_game_state.field)
                if len(new_cards) == 0:
                    return self.game_over_event(action)
                working_game_state.field.extend(new_cards)
                drawn_cards.extend(new_cards)
            return self.valid_set_event(action, replacement_cards, drawn_cards)
        
        player_id = action.player_id
        if self.rules.punish_missed_sets:
            if cards not in self.round_missed_sets[player_id]:
                self.round_missed_sets[player_id].append(cards)
                return self.invalid_set_event(action)
        return None
    
    def handle_call_empty(self, action: Action) -> Event:
        if self.game_state.round_called_empty:
            return None
        if self.game_state.is_set_showing():
            return self.invalid_call_empty_event(action)
        working_game_state = self.get_game_state()
        drawn_cards = []
        while not working_game_state.is_set_showing():
            new_cards = self.draw_cards()
            working_game_state.field.extend(new_cards)
            drawn_cards.extend(new_cards)
        self.round_missed_sets = defaultdict(list)
        return self.valid_call_empty_event(action, drawn_cards)
    
    def get_events(self, timestamp: int) -> List[Event]:
        index = bisect.bisect_left(self.events, timestamp, key=lambda event: event.timestamp)
        return self.events[index:]
    
    def event_args(self, etype: EventType, action: Action):
        return (etype, action.player_id, action.timestamp, len(self.events))
    
    def valid_set_event(self, action: Action, replacement_cards: List[Card], drawn_cards: List[Card]) -> Event:
        return Event(*self.event_args(EventType.VALID_SET_EVENT, action), selected_cards=action.cards, replacement_cards=replacement_cards, drawn_cards=drawn_cards)
    
    def game_over_event(self, action: Action) -> Event:
        return Event(*self.event_args(EventType.VALID_SET_EVENT, action), selected_cards=action.cards, game_over=True)
    
    def invalid_set_event(self, action: Action) -> Event:
        return Event(*self.event_args(EventType.INVALID_SET_EVENT, action))
    
    def valid_call_empty_event(self, action: Action, drawn_cards: List[Card]) -> Event:
        return Event(*self.event_args(EventType.VALID_CALL_EMPTY_EVENT, action), drawn_cards=drawn_cards)
    
    def invalid_call_empty_event(self, action: Action) -> Event:
        return Event(*self.event_args(EventType.INVALID_CALL_EMPTY_EVENT, action))
    
    def get_game_state(self) -> GameState:
        return GameState.from_json(self.game_state.to_json())
