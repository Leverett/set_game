from time import time


class Action:
    def __init__(self, player_id):
        self.player_id = player_id
        self.time = time()

class CallEmpty(Action):
    def __init__(self, player_id):
        super().__init__(player_id)

class CallSet(Action):
    def __init__(self, player_id, cards):
        super().__init__(player_id)
        self.cards = cards

class Event:
    def __init__(self, action, event_num):
        self.player_id = action.player_id
        self.time = action.time
        self.event_num = event_num

class ValidSetEvent(Event):
    def __init__(self, action, event_num, cards, num_draws, game_over=False):
        super().__init__(action, event_num)
        self.cards = cards
        self.num_draws = num_draws
        self.game_over = game_over

class InvalidSetEvent(Event):
    def __init__(self, action, event_num, cards):
        super().__init__(action, event_num)
        self.cards = cards

class ValidCallEmptyEvent(Event):
    def __init__(self, action, event_num, num_draws):
        super().__init__(action, event_num)
        self.num_draws = num_draws

class InvalidCallEmptyEvent(Event):
    def __init__(self, action, event_num):
        super().__init__(action, event_num)