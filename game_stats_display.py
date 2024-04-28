from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from game_objects import *


def score_text(n):
    return f"Score: {n}"

def sets_found_text(n):
    return f"Sets Found: {n}"

def missed_sets_text(n):
    return f"Missed Sets: {n}"

def missed_empties_text(n):
    return f"Missed Empties: {n}"

def remaining_cards_text(n):
    return f"Remaining Cards: {n}"

class GameStatsDisplay(BoxLayout):
    def __init__(self):
        super().__init__()
        self.height = '64dp'
        self.size_hint_y = None
        self.orientation = 'horizontal'

    def update_game_stats(self, game_state, player) -> None:
        pass


class SPBasicStatsDisplay(GameStatsDisplay):
    def __init__(self):
        super().__init__()
        self.sets_found_label = Label(text=sets_found_text(0))
        self.add_widget(self.sets_found_label)
        self.remaining_cards_label = Label(text=remaining_cards_text(len(ALL_CARDS)))
        self.add_widget(self.remaining_cards_label)

    def update_game_stats(self, game_state, player) -> None:
        self.sets_found_label.text = sets_found_text(len(player.sets))
        self.remaining_cards_label.text = remaining_cards_text(game_state.remaining_cards())

class MissesDisplay(BoxLayout):
    def __init__(self):
        super().__init__()
        self.orientation = 'vertical'

    def update_misses_display(self, player) -> None:
        pass

class MissedSetsDisplay(MissesDisplay):
    def __init__(self):
        MissesDisplay.__init__(self)
        self.missed_sets_label = Label(text=missed_sets_text(0))
        self.add_widget(self.missed_sets_label)
    
    def update_misses_display(self, player) -> None:
        self.missed_sets_label.text = missed_sets_text(player.missed_sets)

class MissedEmptiesDisplay(MissesDisplay):
    def __init__(self):
        MissesDisplay.__init__(self)
        self.missed_empties_label = Label(text=missed_empties_text(0))
        self.add_widget(self.missed_empties_label)
    
    def update_misses_display(self, player) -> None:
        self.missed_empties_label.text = missed_empties_text(player.missed_empties)

class AllMissesDisplay(MissedSetsDisplay, MissedEmptiesDisplay):
    def __init__(self):
        MissedSetsDisplay.__init__(self)
        MissedEmptiesDisplay.__init__(self)
        
    def update_misses_display(self, player) -> None:
        MissedSetsDisplay.update_misses_display(self, player)
        MissedEmptiesDisplay.update_misses_display(self, player)

class SPScoreStatsDisplay(GameStatsDisplay):
    def __init__(self, rules):
        super().__init__()
        self.score_label = Label(text=score_text(0))
        self.add_widget(self.score_label)
        self.sets_found_label = Label(text=sets_found_text(0))
        self.add_widget(self.sets_found_label)
        if rules.punish_missed_sets:
            if rules.punish_missed_empties:
                self.misses_display = AllMissesDisplay()
            else:
                self.misses_display = MissedSetsDisplay()
        else:
            self.misses_display = MissedEmptiesDisplay()
        self.add_widget(self.misses_display)
        self.remaining_cards_label = Label(text=remaining_cards_text(len(ALL_CARDS)))
        self.add_widget(self.remaining_cards_label)

    def update_game_stats(self, game_state, player) -> None:
        SPBasicStatsDisplay.update_game_stats(self, game_state, player)
        self.score_label.text = score_text(game_state.player_score(player))
        self.misses_display.update_misses_display(player)
