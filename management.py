from copy import copy
from random import shuffle
from itertools import combinations
from collections import defaultdict
import bisect
from events import *
from game_objects import *

is_debug = False

def is_feature_valid(value1, value2, value3):
    if value1 == value2 == value3:
        return True  # All values are equal
    elif value1 != value2 and value2 != value3 and value1 != value3:
        return True  # All values are different
    else:
        return False  # Neither all equal nor all different

def is_set(card1, card2, card3):
    if is_debug:
        return True
    features = ['symbol', 'color', 'number', 'shading']
    for feature in features:
        if not is_feature_valid(getattr(card1, feature), getattr(card2, feature), getattr(card3, feature)):
            return False
    return True

def is_set_showing(displayed_cards):
    for set in combinations(displayed_cards, 3):
        if (is_set(*set)):
            return True
    return False

def init_deck():
    deck = copy(ALL_CARDS)
    while True:
        shuffle(deck)
        if is_set_showing(deck[:STANDARD_FIELD_SIZE]):
            return deck


class SetLobby:
    def __init__(self, player_id, player_name):
        self.players = []
        self.add_player(player_id, player_name)
        self.rules = Rules(True, True)
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
        # SetGameState.__init__(self, deck=init_deck(), players={player.id: player for player in lobby.players}, events=[])
        self.game_state = SetGameState(deck=init_deck(), players=players)
        if not rules:
            self.rules = Rules(True, True)
        else:
            self.rules = rules
        self.events = []
    
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
    
        
    def handle_call_set(self, set_action):
        cards = set_action.cards
        
        if is_set(*list(cards)):
            self.game_state.round_missed_sets = defaultdict(set)
            num_draws = 0
            try:
                num_draws = self.get_num_draws(cards)
            except GameOverException:
                num_draws = -1
            return ValidSetEvent(set_action, len(self.events), cards, num_draws, game_over=(num_draws >= 0))

        player_id = set_action.player_id
        if self.rules.punish_missed_sets:
            if cards not in self.game_state.round_missed_sets[player_id]:
                self.game_state.round_missed_sets[player_id].append(cards)
                return InvalidSetEvent(set_action, len(self.events), cards)
        return None
    
    def get_num_draws(self, cards):
        # Handle if game_over if no more cards to draw
        if not self.game_state.can_draw():
            remaining_display = [card for card in self.game_state.displayed_cards if card not in cards]
            if not is_set_showing(remaining_display):
                raise GameOverException
            return 0
        
        new_display = copy(self.game_state.displayed_cards)
        for n, card in enumerate(cards):
            new_display[self.game_state.displayed_cards.index(card)] = self.game_state.get_future_card(n)
        draw_num = 0
        while not is_set_showing(new_display):
            try:
                for _ in range(SET_SIZE):
                    new_display.append(self.game_state.get_future_card(SET_SIZE + draw_num))
                draw_num += 1
            except OutOfCardsException:
                raise GameOverException
        return draw_num
    
    def handle_call_empty(self, action):
        if not self.rules.punish_missed_empties or self.game_state.round_called_empty:
            return None
        if is_set_showing(self.game_state.displayed_cards):
            self.game_state.round_called_empty = action.player_id
            return InvalidCallEmptyEvent(action, len(self.events))
        self.game_state.round_called_empty = False
        self.game_state.round_missed_sets = defaultdict(set)
        return ValidCallEmptyEvent(action, len(self.events))
    
    def later_events(self, player_action):
        index = bisect.bisect_left(self.events, player_action, key=lambda event: event.time)
        return self.events[index:]
    




    

