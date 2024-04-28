from enum import IntEnum, StrEnum
from constants import *
from collections import defaultdict
from events import *
from itertools import product


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

FEATURES = [Color, Symbol, Shading, Number]
ALL_CARDS = [Card(*features) for features in list(product(*FEATURES))]
    
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
    def __init__(self, punish_missed_sets, punish_missed_empties):
        self.punish_missed_sets = punish_missed_sets
        self.punish_missed_empties = punish_missed_empties

class OutOfCardsException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class GameOverException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MissingEventException(Exception):
    def __init__(self, event_index, current_num_events):
        super().__init__(self, f"Given event index: {event_index}, Number of events: {current_num_events}")

class SetGameState:

    def __init__(self, deck, players):
        self.deck = deck
        self.displayed_cards = self.deck[:STANDARD_FIELD_SIZE]
        self.deck_index = STANDARD_FIELD_SIZE
        self.players = players
        self.num_events = 0
        self.round_called_empty = False
        self.round_missed_sets = defaultdict(list)
        self.game_over = False

    def get_future_card(self, draw_num):
        card_in_deck_index = self.deck_index + draw_num
        if card_in_deck_index > len(self.deck):
            raise OutOfCardsException
        return self.deck[self.deck_index + draw_num]

    def remaining_cards(self):
        return len(self.deck) - self.deck_index
    
    def can_draw(self):
        return self.remaining_cards() > 0
    
    def get_next_card(self):
        next_card = self.deck[self.deck_index]
        self.deck_index += 1
        return next_card
    
    def replace_card(self, card_index):
        self.displayed_cards[card_index] = self.get_next_card()
        
    def process_event(self, event):
        if event.event_num != self.num_events:
            raise MissingEventException(event.event_num, self.num_events)
        if event.game_over:
            self.run_game_over()
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
        cards = event.cards
        self.players[event.player_id].sets.append(event.cards)
        for card in cards:
            self.replace_card(card)
        self.do_draws(event.num_draws)
    
    def process_invalid_set_event(self, event):
        self.players[event.player_id].missed_sets += 1
    
    def process_valid_call_empty_event(self, event):
        self.do_draws(event.num_draws)
    
    def process_invalid_call_empty_event(self, event):
        self.players[event.player_id].missed_empties += 1

    def do_draws(self, num_draws):
        for _ in range(num_draws):
            self.do_draw()

    def do_draw(self):
        for _ in range(SET_SIZE):
            self.displayed_cards.append(self.get_next_card())

    def replace_card(self, card):
        if self.deck:
            next_card = self.get_next_card()
            self.displayed_cards = [next_card if c == card else c for c in self.displayed_cards]
            return True
        else:
            return False
        
    def run_game_over(self):
        pass

    def player_score(self, player):
        player_id = player if type(player) is str else player.id
        return self.players[player_id].score()
    
    def print_displayed_cards(self):
        for i in range(0, len(self.displayed_cards), 3):
            print('  '.join(map(str, self.displayed_cards[i:i+3])))