from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.lang import Builder
from game.management import *
from widgets.game_stats_display import *
from widgets.grid_display import *


Builder.load_file('set_game.kv')

class SetGame(BoxLayout):
    def __init__(self, manager, game_state, player_id, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.manager=manager
        self.game_state = game_state
        self.player = game_state.players[player_id]

        self.selected_cards = set()
        self.hints = set()
        self.card_grid = self.ids.card_grid
        self.display_cards()

        self.stats_display = self.make_game_stats_display()
        self.add_widget(self.stats_display, index=(self.children.index(self.card_grid)))
        self.update_game_stats()

        self.buttons_layout = self.ids.buttons_layout
        self.buttons_layout.add_widget(Button(text="Shuffle", on_press=self.shuffle_press))
        if self.manager.rules.punish_missed_empties:
            self.buttons_layout.add_widget(Button(text="Add Cards", on_press=self.add_cards_press))
        elif self.manager.rules.enable_hints:
            self.buttons_layout.add_widget(Button(text="Hint", on_press=self.hint_press))


    def display_cards(self):
        self.card_grid.clear_widgets()

        for card in self.game_state.displayed_cards:
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
                Clock.schedule_once(lambda _: self.do_set_action(CallSet(self.player.id, {card for card in self.selected_cards})), 0.2)

    def button_widget_parent(self):
        if self.manager.rules.punish_missed_empties or self.manager.rules.enable_hints:
            button_widget_parent = BoxLayout(orientation='horizontal', height='64dp', size_hint_y=None)
            self.add_widget(button_widget_parent)
        return self

    def do_set_action(self):
        pass

    def shuffle_press(self, _):
        shuffle(self.game_state.displayed_cards)
        self.display_cards()

    def add_cards_press(self, _):
        self.do_add_cards_action(CallEmpty(self.player.id))

    def do_add_cards_action(self):
        pass

    def hint_press(self, _):
        self.do_hint()

    def do_hint(self):
        pass

    def reset_card_opacity(self):
        for child in self.ids.card_grid.children:
            child.opacity = 1

    def make_game_stats_display(self) -> BoxLayout:
        pass

    def game_over(self):
        game_over_label = Label(text=GAME_OVER, color=(1, 1, 1, 1), size_hint=(1, None), height=50)
        popup = Popup(title='Set Game', content=game_over_label, size_hint=(None, None), size=(300, 100))
        popup.open()