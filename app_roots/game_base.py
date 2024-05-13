from abc import abstractmethod
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.lang import Builder
from game.management import GameManager
from widgets.game_stats_display import GameStatsDisplay
from widgets.grid_display import HighlightedImage
from game.game_state import GameState
from typing import MutableSet
from random import shuffle
from game.events import Action, ActionType, EventType
from game.game_objects import Card, Player, card_image_source, Rules
from game.globals import *


Builder.load_file('layouts/set_game.kv')

class SetGame(BoxLayout):
    def __init__(self, manager: GameManager, game_state: GameState, rules: Rules, player_id: str, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.manager: GameManager = manager
        self.game_state: GameState = game_state
        self.rules: Rules = rules
        self.player: Player = game_state.find_player(player_id)

        self.selected_cards: MutableSet[Card] = set()
        self.hints: MutableSet[Card] = set()
        self.card_grid = self.ids.card_grid
        self.display_cards()

        self.stats_display: GameStatsDisplay = self.make_game_stats_display()
        self.ids.stats_display.add_widget(self.stats_display)
        self.update_game_stats()

        self.buttons_layout = self.ids.buttons_layout
        self.buttons_layout.add_widget(Button(text="Shuffle", on_press=self.shuffle_press))
        if self.rules.punish_missed_empties:
            self.buttons_layout.add_widget(Button(text="Add Cards", on_press=self.add_cards_press))
        elif self.rules.enable_hints:
            self.buttons_layout.add_widget(Button(text="Hint", on_press=self.hint_press))


    def display_cards(self):
        self.card_grid.clear_widgets()

        for card in self.game_state.field:
            image_source = card_image_source(card)
            image = Image(source=image_source, allow_stretch=True) if card not in self.hints else HighlightedImage(source=image_source, allow_stretch=True)
            image.bind(on_touch_down=self.on_card_click)
            image.card = card
            self.card_grid.add_widget(image)

    def update_game_stats(self):
        self.stats_display.update_game_stats(self.game_state, self.player)

    def on_card_click(self, instance, touch):
        if instance.collide_point(*touch.pos):
            if instance.card in self.selected_cards:
                instance.opacity = 1
                self.selected_cards.remove(instance.card)
            else:
                instance.opacity = 0.5
                self.selected_cards.add(instance.card)

            if len(self.selected_cards) == SET_SIZE:
                Clock.schedule_once(lambda _: self.do_set_action(Action(ActionType.CALL_SET, self.player.id, cards={card for card in self.selected_cards})), 0.2)

    def button_widget_parent(self):
        if self.rules.punish_missed_empties or self.rules.enable_hints:
            button_widget_parent = BoxLayout(orientation='horizontal', height='64dp', size_hint_y=None)
            self.add_widget(button_widget_parent)
        return self

    def do_set_action(self, action: Action):
        events = self.manager.handle_action(action)
        self.selected_cards.clear()
        self.reset_card_opacity()
        if len(events) > 0:
            event = events[0]
            self.game_state.process_event(event)
            if event.etype is EventType.VALID_SET_EVENT:
                self.hints.clear()
            self.display_cards()
            self.update_game_stats()
            if event.etype is EventType.VALID_SET_EVENT and event.game_over:
                self.game_over()

    def do_add_cards_action(self, action: Action):
        events = self.manager.handle_action(action)
        self.selected_cards.clear()
        self.reset_card_opacity()
        if len(events) > 0:
            self.game_state.process_event(events[0])
            self.display_cards()
            self.update_game_stats()

    def shuffle_press(self, _):
        shuffle(self.game_state.field)
        self.display_cards()

    def add_cards_press(self, _):
        self.do_add_cards_action(Action(ActionType.CALL_EMPTY, self.player.id))

    def hint_press(self, _):
        self.do_hint()

    @abstractmethod
    def do_hint(self):
        pass

    def reset_card_opacity(self):
        for child in self.ids.card_grid.children:
            child.opacity = 1

    @abstractmethod
    def make_game_stats_display(self) -> GameStatsDisplay:
        pass

    @abstractmethod
    def game_over(self):
        pass

    @abstractmethod
    def title(self):
        pass

    @abstractmethod
    def quit(self):
        pass
