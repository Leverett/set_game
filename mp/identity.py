


class Identity:
    def __init__(self, player_id, player_name):
        self.player_id = player_id
        self.player_name = player_name

    def __repr__(self):
        return self.player_name

    def __eq__(self, other):
        if not isinstance(other, Identity):
            return False
        return self.player_id == other.player_id

    def __hash__(self):
        return hash(self.player_id)

    def __contains__(self, item):
        if not isinstance(item, Identity):
            return False
        return self == item