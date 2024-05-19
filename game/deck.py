from random import shuffle, choice
from abc import ABC, abstractmethod
from typing import List, MutableSet
from copy import copy
from game.globals import *
from game.game_objects import Card, all_cards, contains_set


# This could probably be implemented in a way in which draw_cards would do the complete draw
# rather than 3 at a time, and throw an error if it reached a point where the deck ran out
# before a set was displayed
# This could probably be more simply caught by the LocalGameManager and handled appropriately
# instead of having to iterate there while checking for an empty deck. The deck could just
# say when it was game over.
# Or maybe it would cause more methods to be needed to handle initializing, replacement draw, etc
# Or maybe it could just take a parameter to specify the limit of the field size, and the first 3
# cards could just be called the replacements when applicable
# Tentative TODO
class Deck(ABC):
    def __init__(self):
        self.cards: List[Card] = all_cards()

    @abstractmethod
    def draw_cards(self, *args) -> List[Card]:
        pass
    @abstractmethod
    def remaining_cards(self) -> int:
        pass
    @abstractmethod
    def initial_draw(self) -> List[Card]:
        pass

class EndlessDeck(Deck):

    def draw_card(self, used_cards: MutableSet[Card]) -> Card:
        available_cards = [card for card in self.cards if card not in used_cards]
        if len(available_cards) == 0:
            self.cards.extend(all_cards())
            available_cards = [card for card in self.cards if card not in used_cards]
        new_card = choice(available_cards)
        self.cards.remove(new_card)
        return new_card
        
    def draw_cards(self, field: List[Card], num: int = SET_SIZE) -> List[Card]:
        used_cards = set(field)
        new_cards = []
        for _ in range(num):
            new_card = self.draw_card(used_cards)
            new_cards.append(new_card)
            used_cards.add(new_card)
        return new_cards

    def remaining_cards(self) -> int:
        return -1
    
    def initial_draw(self) -> List[Card]:
        while True:
            initial_cards = set()
            while len(initial_cards) < STANDARD_FIELD_SIZE:
                initial_cards.add(choice(self.cards))
            if contains_set(initial_cards):
                for card in initial_cards:
                    self.cards.remove(card)
                return list(initial_cards)

class StandardDeck(Deck):
    def __init__(self):
        super().__init__()
        shuffle(self.cards)
        while not contains_set(self.cards[:STANDARD_FIELD_SIZE]):
            shuffle(self.cards)

    def draw_cards(self, field, num: int = SET_SIZE) -> List[Card]:
        if len(self.cards) < num:
            return []
        new_cards = self.cards[:num]
        self.cards = self.cards[num:]
        return new_cards
    
    def remaining_cards(self) -> int:
        return len(self.cards)
    
    def initial_draw(self) -> List[Card]:
        return self.draw_cards([], num=STANDARD_FIELD_SIZE)
            
class StackedDeck(StandardDeck):
    def __init__(self, deck_size: int = None, expand_field_round: int = None):
        super().__init__()
        self.round = 0
        if deck_size is not None:
            self.cards = self.cards[:deck_size]
        if expand_field_round is not None:
            self.cards = self.stack_cards()
        self.expand_field_round = expand_field_round

    def stack_cards(self) -> List[Card]:
        stacked_cards = []
        for i in range(STANDARD_FIELD_SIZE):
            stacked_cards.append(self.get_set_card(stacked_cards, i == STANDARD_FIELD_SIZE - 1))
        stacked_cards.extend([card for card in self.cards if card not in stacked_cards])
        return stacked_cards

    def draw_cards(self, field: List[Card], num: int = SET_SIZE) -> List[Card]:
        self.round += 1
        if self.round > self.expand_field_round:
            super().draw_cards(field, num=num)
        expand_field = False
        if self.round == self.expand_field_round:
            expand_field = True

        working_field = copy(field)
        drawn_cards = []
        for i in range(num):
            new_card = self.get_set_card(working_field, (expand_field and i == num - 1))
            drawn_cards.append(new_card)
            field.append(new_card)
            self.cards.remove(new_card)
        return drawn_cards

    def get_set_card(self, field: List[Card], makes_set: bool) -> Card:
        if not makes_set and contains_set(field):
            print("Ooooooppps")
            return
        original_field_size = len(field)
        working_field = copy(field)
        
        available_cards = [card for card in self.cards if card not in field]
        new_card = choice(available_cards)
        print(original_field_size)
        print(len(working_field))
        working_field.append(new_card)
        print(len(working_field))
        while (not makes_set and contains_set(working_field)) or (makes_set and not contains_set(working_field)):
            new_card = choice(available_cards)
            working_field[original_field_size] = new_card
        return new_card

    def initial_draw(self) -> List[Card]:
        draw = self.cards[:STANDARD_FIELD_SIZE]
        self.cards = self.cards[STANDARD_FIELD_SIZE:]
        return draw