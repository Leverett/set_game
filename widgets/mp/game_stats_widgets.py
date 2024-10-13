from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from game.game_objects import Player, Rules
from game.game_state import GameState
from widgets.game_stats_display import GameStatsDisplay, GameStatsWidget


class MPStatsDisplay(GameStatsDisplay):
    def __init__(self, players: list[Player], rules: Rules):
        super().__init__(orientation='horizontal', height='64dp', size_hint_y=None)
        if rules.count_misses():
            self.add_widget(ScoreDisplay())
        self.add_widget(SetsFoundDisplay())
        if rules.count_misses():
            misses_display = MissesDisplay()
            if rules.punish_missed_sets:
                misses_display.add_widget(MissedSetsDisplay())
            if rules.punish_missed_empties:
                misses_display.add_widget(MissedEmptiesDisplay())
            self.add_widget(misses_display)
        if not rules.endless_mode:
            self.add_widget(RemainingDealsDisplay())

class ScoreDisplay(Label, GameStatsWidget):
    def update_stats(self, game_state: GameState, player: Player):
        self.text = f"Score: {game_state.player_score(player)}"

class SetsFoundDisplay(Label, GameStatsWidget):
    def update_stats(self, game_state: GameState, player: Player):
        self.text = f"Sets Found: {len((player.sets))}"

class RemainingDealsDisplay(Label, GameStatsWidget):
    def update_stats(self, game_state: GameState, player: Player):
        self.text = f"Remaining Deals: {game_state.remaining_cards // 3}"

class MissesDisplay(BoxLayout, GameStatsWidget):
    def __init__(self):
        super().__init__()
        self.orientation = 'vertical'

    def update_stats(self, game_state: GameState, player: Player):
        for child in self.children:
            child.update_stats(game_state, player)

class MissedSetsDisplay(Label, GameStatsWidget):
    def update_stats(self, game_state: GameState, player: Player):
        self.text = f"Missed Sets: {player.missed_sets}"

class MissedEmptiesDisplay(Label, GameStatsWidget):
    def update_stats(self, game_state: GameState, player: Player):
        self.text = f"Missed Empties: {player.missed_empties}"
