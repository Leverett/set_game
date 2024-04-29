from copy import copy, deepcopy
from random import shuffle
from collections import defaultdict
import bisect
from game.events import *
from game.game_objects import *

def init_deck():
    deck = copy(ALL_CARDS)
    while True:
        shuffle(deck)
        if contains_set(deck[:STANDARD_FIELD_SIZE]):
            return deck[:15]


class SetLobby:
    def __init__(self, player_id, player_name):
        self.players = []
        self.add_player(player_id, player_name)
        self.rules = Rules(True, True, False)
        self.started = False

    def add_player(self, player_id, player_name):
        if len(self.players) < MAX_PLAYERS:
            self.players.append(Player(player_id, player_name))

    def remove_player(self, player_id):
        if self.is_host(player_id):
            return False
        self.players = [player for player in self.players if player.id != player_id]
        return True

    def is_host(self, player_id):
        return player_id == self.players[0]
    
    def get_host(self):
        return self.players[0]

    def make_game(self):
        self.started = True
        return SetGameState(self.players, self.punish_missed_sets, self.punish_missed_empties)


class SetGameManager:
    def handle_action(self, action):
        pass

class LocalGameManager(SetGameManager):
    def __init__(self, rules, players):
        SetGameManager.__init__(self)
        self.deck = init_deck()
        self.deck_index = STANDARD_FIELD_SIZE
        self.game_state = SetGameState(self.deck[:self.deck_index], self.remaining_cards(), players)
        if not rules:
            self.rules = Rules(True, False, True)
        else:
            self.rules = rules
        self.events = []
        self.round_missed_sets = defaultdict(list)
    
    def handle_action(self, action):
        if not self.events or self.events[-1].time < action.time:
            events = []
            if type(action) is CallEmpty:
                event = self.handle_call_empty(action)
                if event:
                    events.append(event)
            if type(action) is CallSet:
                event = self.handle_call_set(action)
                if event:
                    events.append(event)
            if len(events) > 0:
                event = events[0]
                self.events.append(event)
                self.game_state.process_event(event)
            return events
        return self.later_events(action)
    
    def handle_call_set(self, action):
        cards = action.cards
        
        if is_set(*list(cards)):
            working_game_state = deepcopy(self.game_state)
            replacement_cards = self.draw_cards()
            if len(replacement_cards) == 0:
                for card in cards:
                    working_game_state.displayed_cards.remove(card)
                if not working_game_state.is_set_showing():
                    return self.game_over_event(action)
                else:
                    return self.valid_set_event(action, [], [])
            for i, card in enumerate(cards):
                working_game_state.replace_card(card, replacement_cards[i])
            drawn_cards = []
            while not working_game_state.is_set_showing():
                new_cards = self.draw_cards()
                if len(new_cards) == 0:
                    return self.game_over_event(action)
                working_game_state.displayed_cards.append(new_cards)
                drawn_cards.append(new_cards)

            return self.valid_set_event(action, replacement_cards, drawn_cards)

        player_id = action.player_id
        if self.rules.punish_missed_sets:
            if cards not in self.round_missed_sets[player_id]:
                self.round_missed_sets[player_id].append(cards)
                return self.invalid_set_event(action)
        return None
    
    def handle_call_empty(self, action):
        if self.game_state.round_called_empty:
            return None
        if self.game_state.is_set_showing():
            return self.invalid_call_empty_event(action)
        working_game_state = copy(self.game_state)
        drawn_cards = []
        while not working_game_state.is_set_showing():
            new_cards = self.draw_cards()
            working_game_state.displayed_cards.append(new_cards)
            drawn_cards.append(new_cards)
        self.round_missed_sets = defaultdict(set)
        return self.valid_call_empty_event(action, drawn_cards)
    
    def later_events(self, player_action):
        index = bisect.bisect_left(self.events, player_action, key=lambda event: event.time)
        return self.events[index:]

    def remaining_cards(self):
        return len(self.deck) - self.deck_index
    
    def get_next_card(self):
        if self.remaining_cards() == 0:
            return None
        next_card = self.deck[self.deck_index]
        self.deck_index += 1
        return next_card
    
    def draw_cards(self):
        return [card for _ in range(SET_SIZE) if (card := self.get_next_card()) is not None]
    
    def valid_set_event(self, action, replacement_cards, drawn_cards):
        return ValidSetEvent(action, len(self.events), replacement_cards, drawn_cards)
    
    def game_over_event(self, action):
        return ValidSetEvent(action, len(self.events), [], [], game_over=True)
    
    def invalid_set_event(self, action):
        return InvalidSetEvent(action, len(self.events))
    
    def valid_call_empty_event(self, action, drawn_cards):
        return ValidCallEmptyEvent(action, len(self.events), drawn_cards)
    
    def invalid_call_empty_event(self, action):
        return InvalidCallEmptyEvent(action, len(self.events))
