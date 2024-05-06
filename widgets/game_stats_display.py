from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from game.game_objects import *


def score_text(n):
    return f"Score: {n}"

def sets_found_text(n):
    return f"Sets Found: {n}"

def missed_sets_text(n):
    return f"Missed Sets: {n}"

def missed_empties_text(n):
    return f"Missed Empties: {n}"

def remaining_deals_text(n):
    return f"Remaining Deals: {n // 3}"

class GameStatsDisplay(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_game_stats(self, game_state, player) -> None:
        pass

class SPStatsDisplay(GameStatsDisplay):
    def __init__(self):
        super().__init__(orientation='horizontal', height='64dp', size_hint_y=None)


class SPBasicStatsDisplay(GameStatsDisplay):
    def __init__(self):
        super().__init__()
        self.sets_found_label = Label(text=sets_found_text(0))
        self.add_widget(self.sets_found_label)
        self.remaining_deals_label = Label(text=remaining_deals_text(0))
        self.add_widget(self.remaining_deals_label)

    def update_game_stats(self, game_state, player) -> None:
        self.sets_found_label.text = sets_found_text(len(player.sets))
        self.remaining_deals_label.text = remaining_deals_text(game_state.remaining_cards)

class MissesDisplay(BoxLayout):
    def __init__(self):
        super().__init__()
        self.orientation = 'vertical'

    def update_misses_display(self, player) -> None:
        pass

class MissedSetsDisplay(MissesDisplay):
    def __init__(self, **kwargs):
        MissesDisplay.__init__(self, **kwargs)
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

class SPScoreStatsDisplay(SPStatsDisplay):
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
        self.remaining_deals_label = Label(text=remaining_deals_text(0))
        self.add_widget(self.remaining_deals_label)

    def update_game_stats(self, game_state, player) -> None:
        SPBasicStatsDisplay.update_game_stats(self, game_state, player)
        self.score_label.text = score_text(game_state.player_score(player))
        self.misses_display.update_misses_display(player)
