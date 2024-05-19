from collections import defaultdict
from itertools import combinations
from game.game_objects import Identity, MissingEventException, Player, Card, is_set, contains_set
from game.events import Event, EventType
from random import shuffle
from game.globals import *
from host.serialization import GameSerializable


class GameState(GameSerializable):

    def __init__(self, field: list[Card], remaining_cards: int, players: list[Player],
                 num_events: int = 0, round_called_empty: str = None, round_missed_sets: defaultdict[str,list[set[Card]]] = defaultdict(list), game_over: bool = False):
        self.field: list[Card] = field
        self.remaining_cards: int = remaining_cards
        self.players: list[Player] = players
        self.num_events: int = num_events
        self.round_called_empty: str = round_called_empty
        self.round_missed_sets: defaultdict[str,list[set[Card]]] = round_missed_sets
        self.game_over: bool = game_over

    def is_set_showing(self):
        return contains_set(self.field)
    
    def replace_card(self, card: Card, replacement_card: Card):
        self.field[self.field.index(card)] = replacement_card
        
    def process_event(self, event):
        if event.event_num != self.num_events:
            raise MissingEventException(event.event_num, self.num_events)
        if event.etype is EventType.VALID_SET_EVENT:
            self.process_valid_set_event(event)
        if event.etype is EventType.INVALID_SET_EVENT:
            self.process_invalid_set_event(event)
        if event.etype is EventType.VALID_CALL_EMPTY_EVENT:
            self.process_valid_call_empty_event(event)
        if event.etype is EventType.INVALID_CALL_EMPTY_EVENT:
            self.process_invalid_call_empty_event(event)
        if self.game_over:
            return
        self.num_events += 1

    def process_valid_set_event(self, event: Event):
        self.find_player(event.player_id).sets.append(event.selected_cards)
        self.round_called_empty = None
        self.remaining_cards -= len(event.replacement_cards)
        self.remaining_cards -= len(event.drawn_cards)
        for i, card in enumerate(event.selected_cards):
            if len(event.replacement_cards) > 0:
                self.replace_card(card, event.replacement_cards[i])
            else:
                self.field.remove(card)
        if len(event.drawn_cards) > 0:
            self.field.extend(event.drawn_cards)
    
    def process_invalid_set_event(self, event: Event):
        self.find_player(event.player_id).missed_sets += 1
    
    def process_valid_call_empty_event(self, event: Event):
        self.round_called_empty = None
        self.field.extend(event.drawn_cards)
    
    def process_invalid_call_empty_event(self, event: Event):
        self.round_called_empty = event.player_id
        self.find_player(event.player_id).missed_empties += 1

    def replace_card(self, card: Card, replacement_card: Card):
        self.field[self.field.index(card)] = replacement_card

    def player_score(self, player: Player) -> int:
        return self.find_player(player.id).score()
    
    def get_hint(self, hints: set[Card]) -> Card:
        if len(hints) + 1 == SET_SIZE:
            return None
        all_possible_sets = [possible_set for possible_set in combinations(self.field, SET_SIZE) if hints.issubset(set(possible_set))]
        shuffle(all_possible_sets)
        for possible_set in all_possible_sets:
            if is_set(*list(possible_set)):
                for card in possible_set:
                    if card not in hints:
                        return card
        return None
    
    def find_player(self, identity) -> Player: #TODO make everything work from Identity/Player
        for player in self.players:
            if (isinstance(identity, Identity) and identity == player) or (identity == player.id):
                return player
        # return next((player for player in self.players if player.id == player_id), None)

    def print_displayed_cards(self):
        for i in range(0, len(self.field), GRID_WIDTH):
            print('  '.join(map(str, self.field[i:i+GRID_WIDTH])))

    def to_json(self) -> dict:
        return {
            'field': [card.to_json() for card in self.field],
            'remaining_cards': self.remaining_cards,
            'players': [player.to_json() for player in self.players],
            'num_events': self.num_events,
            'round_called_empty': self.round_called_empty,
            'round_missed_sets': {player_id: [{card.to_json() for card in missed_set} for missed_set in missed_sets] for player_id, missed_sets in self.round_missed_sets.items()},
            'game_over': self.game_over
        }

    @classmethod
    def from_json(cls, json_data: dict):
        field = [Card.from_json(card) for card in json_data['field']]
        remaining_cards = json_data.get('remaining_cards', 0)
        players = [Player.from_json(player) for player in json_data['players']]

        num_events = json_data.get('num_events', 0)
        round_called_empty = json_data.get('round_called_empty', None)
        round_missed_sets_data = json_data.get('round_missed_sets', {})
        round_missed_sets = {player_id: [{Card.from_json(card) for card in missed_set} for missed_set in missed_sets] for player_id, missed_sets in round_missed_sets_data.items()}
        game_over = json_data.get('game_over', False)
        return GameState(field, remaining_cards, players,
                         num_events=num_events, round_called_empty=round_called_empty, round_missed_sets=round_missed_sets,
                         game_over=game_over)
