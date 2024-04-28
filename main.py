from copy import deepcopy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.lang import Builder
from management import *
from game_stats_display import *

Builder.load_file('set_game.kv')


class SetGame(BoxLayout):
    def __init__(self, manager, game_state, player_id, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.manager=manager
        self.game_state = game_state
        self.player = game_state.players[player_id]

        self.stats_display = self.make_game_stats_display()
        self.add_widget(self.stats_display)

        self.display_cards()
        self.update_game_stats()

        if self.manager.rules.punish_missed_empties:
            add_cards_button = Button(text="Add Cards", size_hint_y=None, height=64, on_press=self.add_cards_press)
            self.add_widget(add_cards_button)

        self.selected_cards = set()

    def display_cards(self):
        card_grid = self.ids.card_grid
        card_grid.clear_widgets()

        for card in self.game_state.displayed_cards:
            image_source = f"images/{card}.png"
            image = Image(source=image_source, allow_stretch=True)
            image.bind(on_touch_down=self.on_card_click)
            image.card = card
            card_grid.add_widget(image)

    def update_game_stats(self):
        self.stats_display.update_game_stats(self.game_state, self.player)

    def on_card_click(self, instance, touch):
        if instance.collide_point(*touch.pos):
            if instance in self.selected_cards:
                instance.opacity = 1
                self.selected_cards.remove(instance)
            else:
                instance.opacity = 0.5
                self.selected_cards.add(instance)

            if len(self.selected_cards) == SET_SIZE:
                Clock.schedule_once(lambda _: self.do_set_action(CallSet(self.player.id, {card.card for card in self.selected_cards})), 0.2)

    def do_set_action(self):
        pass

    def add_cards_press(self, _):
        self.do_add_cards_action(CallEmpty(self.player.id))

    def do_add_cards_action(self):
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


class SPGame(SetGame):
    def __init__(self):
        manager = LocalGameManager(None, {default_id: Player(default_id, default_name)})
        super().__init__(manager, deepcopy(manager.game_state), player_id=default_id)

    def do_set_action(self, action):
        events = self.manager.handle_action(action)
        self.selected_cards.clear()
        self.reset_card_opacity()
        if len(events) > 0:
            event = events[0]
            self.game_state.process_event(event)
            self.display_cards()
            self.update_game_stats()
            if type(event) is ValidSetEvent and event.game_over:
                self.game_over()

    def do_add_cards_action(self, action):
        events = self.manager.handle_action(action)
        self.selected_cards.clear()
        self.reset_card_opacity()
        if len(events) > 0:
            self.game_state.process_event(events[0])
            self.display_cards()
            self.update_game_stats()

    def make_game_stats_display(self) -> BoxLayout:
        rules = self.manager.rules
        if rules.punish_missed_sets or rules.punish_missed_empties:
            return SPScoreStatsDisplay(rules)
        return SPBasicStatsDisplay()


class SetApp(App):
    def build(self):
        return SPGame()

if __name__ == '__main__':
    SetApp().run()
