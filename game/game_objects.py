from enum import IntEnum, StrEnum
from random import shuffle, choice
from game.constants import *
from collections import defaultdict
from game.events import *
from itertools import product, combinations
from abc import ABC, abstractmethod


class Color(StrEnum):
    RED = 'r'
    GREEN = 'g'
    PURPLE = 'p'

class Symbol(StrEnum):
    OVAL = 'o'
    DIAMOND = 'd'
    SQUIGGLE = 's'

class Shading(StrEnum):
    FILLED = 'f'
    STRIPED = 's'
    EMPTY = 'e'

class Number(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3

class Card:
    def __init__(self, color, symbol, shading, number):
        self.color = color
        self.symbol = symbol
        self.shading = shading
        self.number = number

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
    
def card_image_source(card):
    return f"images/{card}.png"


def is_feature_valid(value1, value2, value3):
    if value1 == value2 == value3:
        return True
    elif value1 != value2 and value2 != value3 and value1 != value3:
        return True
    else:
        return False

def is_set(card1, card2, card3):
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
def all_cards():
    return [Card(*features) for features in list(product(*FEATURES))]

short_game = True
deck_size = 15
class Deck(ABC):
    def __init__(self):
        self.cards = all_cards()
        if short_game:
            shuffle(self.cards)
            self.cards = self.cards[:deck_size]

    @abstractmethod
    def draw_cards(self, *args):
        pass
    @abstractmethod
    def remaining_cards(self):
        pass
    @abstractmethod
    def initial_draw(self):
        pass

class EndlessDeck(Deck):

    def draw_card(self, used_cards):
        available_cards = [card for card in self.cards if card not in used_cards]
        if len(available_cards) == 0:
            self.cards.extend(all_cards())
            available_cards = [card for card in self.cards if card not in used_cards]
        new_card = choice(available_cards)
        self.cards.remove(new_card)
        return new_card
        
    def draw_cards(self, displayed_cards, num=SET_SIZE):
        used_cards = set(displayed_cards)
        new_cards = []
        for _ in range(num):
            new_card = self.draw_card(used_cards)
            new_cards.append(new_card)
            used_cards.add(new_card)
        return new_cards

    def remaining_cards(self):
        return -1
    
    def initial_draw(self):
        while True:
            initial_cards = set()
            while len(initial_cards) < STANDARD_FIELD_SIZE:
                initial_cards.add(choice(self.cards))
            if contains_set(initial_cards):
                for card in initial_cards:
                    self.cards.remove(card)
                return list(initial_cards)

class StandardDeck(Deck):

    def draw_cards(self, displayed_cards, num=SET_SIZE):
        if len(self.cards) < num:
            return []
        new_cards = self.cards[:num]
        self.cards = self.cards[num:]
        return new_cards
    
    def remaining_cards(self):
        return len(self.cards)
    
    def initial_draw(self):
        while True:
            shuffle(self.cards)
            if contains_set(self.cards[:STANDARD_FIELD_SIZE]):
                return self.draw_cards([], num=STANDARD_FIELD_SIZE)

    
class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.sets = []
        self.missed_sets = 0
        self.missed_empties = 0

    def score(self):
        return len(self.sets) - self.missed_sets - self.missed_empties
    
    def misses(self):
        return self.missed_sets + self.missed_empties

class Rules:
    def __init__(self, punish_missed_sets, punish_missed_empties, enable_hints, endless_mode):
        self.punish_missed_sets = punish_missed_sets
        self.punish_missed_empties = punish_missed_empties
        self.enable_hints = enable_hints
        self.endless_mode = endless_mode

    def default_rules():
        return Rules(True, True, False, False)

    def to_dict(self):
        return {rule: getattr(self, rule.value) for rule in Rule}
        
    @classmethod
    def from_dict(cls, data):
        instance = cls()
        for key, value in data.items():
            setattr(instance, key, value)
        return instance

class MissingEventException(Exception):
    def __init__(self, event_index, current_num_events):
        super().__init__(self, f"Given event index: {event_index}, Number of events: {current_num_events}")

class SetGameState:

    def __init__(self, displayed_cards, remaining_cards, players):
        self.displayed_cards = displayed_cards
        self.remaining_cards = remaining_cards
        self.players = players
        self.num_events = 0
        self.round_called_empty = None
        self.round_missed_sets = defaultdict(list)
        self.game_over = False

    def is_set_showing(self):
        return contains_set(self.displayed_cards)
    
    def replace_card(self, card, replacement_card):
        self.displayed_cards[self.displayed_cards.index(card)] = replacement_card
        
    def process_event(self, event):
        if event.event_num != self.num_events:
            raise MissingEventException(event.event_num, self.num_events)
        if type(event) is ValidSetEvent:
            self.process_valid_set_event(event)
        if type(event) is InvalidSetEvent:
            self.process_invalid_set_event(event)
        if type(event) is ValidCallEmptyEvent:
            self.process_valid_call_empty_event(event)
        if type(event) is InvalidCallEmptyEvent:
            self.process_invalid_call_empty_event(event)
        self.num_events += 1

    def process_valid_set_event(self, event):
        self.players[event.player_id].sets.append(event.cards)
        self.round_called_empty = None
        self.remaining_cards -= len(event.replacement_cards)
        self.remaining_cards -= len(event.drawn_cards)
        for i, card in enumerate(event.cards):
            if len(event.replacement_cards) > 0:
                self.replace_card(card, event.replacement_cards[i])
            else:
                self.displayed_cards.remove(card)
        if len(event.drawn_cards) > 0:
            self.displayed_cards.append(event.drawn_cards)
    
    def process_invalid_set_event(self, event):
        self.players[event.player_id].missed_sets += 1
    
    def process_valid_call_empty_event(self, event):
        self.round_called_empty = None
        self.displayed_cards.append(event.drawn_cards)
    
    def process_invalid_call_empty_event(self, event):
        self.round_called_empty = event.player_id
        self.players[event.player_id].missed_empties += 1

    def replace_card(self, card, replacement_card):
        self.displayed_cards[self.displayed_cards.index(card)] = replacement_card

    def player_score(self, player):
        player_id = player if type(player) is str else player.id
        return self.players[player_id].score()
    
    def get_hint(self, hints):
        if len(hints) + 1 == SET_SIZE:
            return None
        all_possible_sets = [possible_set for possible_set in combinations(self.displayed_cards, SET_SIZE) if hints.issubset(set(possible_set))]
        shuffle(all_possible_sets)
        for possible_set in all_possible_sets:
            if is_set(*list(possible_set)):
                for card in possible_set:
                    if card not in hints:
                        return card
        return None

    
    def print_displayed_cards(self):
        for i in range(0, len(self.displayed_cards), GRID_WIDTH):
            print('  '.join(map(str, self.displayed_cards[i:i+GRID_WIDTH])))