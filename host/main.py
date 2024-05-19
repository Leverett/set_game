from flask import Flask, request, jsonify
import os
import sys

sys.path.append(os.getcwd())
from game.management import LocalGameManager
from game.game_objects import Identity, Rules
from game.globals import *
from host.instance import Instance, RejectionReason
from game.events import Action, Event
from mp.lobby_state import LobbyState


app = Flask(__name__)
instances: dict[str, Instance] = {}
instances[test_lobby_id] = Instance(LobbyState(test_lobby_id, Identity(test_id, test_name), Rules.default_rules()))

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify(success=True)


# Lobby Handlers

@app.route('/get_lobbies', methods=['GET'])
def get_lobbies():
    request_payload = request.get_json()
    open_lobbies = [instance.lobby_state for instance in instances.values() if not instance.is_started()]
    open_lobbies_payload = [lobby.to_json() for lobby in open_lobbies]

    player: Identity = Identity.from_json(request_payload[PLAYER_KEY])
    active_games = [instance for instance in instances.values() if instance.is_started() and not instance.is_done()]
    active_game = next((instance for instance in active_games if instance.has_player(player)), None)
    if active_game is not None:
        game_state, rules = active_game.manager.get_current_game()
        game_state_payload = game_state.to_json()
        rules_payload = rules.to_json()
        return jsonify(success=True, lobbies=open_lobbies_payload, game_state=game_state_payload, rules=rules_payload)
    return jsonify(success=True, lobbies=open_lobbies_payload)

@app.route('/create_lobby', methods=['POST'])
def create_lobby():
    request_payload = request.get_json()
    player: Identity = Identity.from_json(request_payload[PLAYER_KEY])
    rules: Rules = Rules.from_json(request_payload[RULES_KEY])
    lobby_id = f"lid_{player.id}"
    instance = instances.get(lobby_id, None)
    lobby = LobbyState(lobby_id, player, rules)
    instance = Instance(lobby)
    instances[lobby_id] = instance
    
    return jsonify(success=True, lobby_state=instance.lobby_state.to_json())

@app.route('/join_lobby/<string:lobby_id>', methods=['POST'])
def join_lobby(lobby_id: str):
    request_payload = request.get_json()
    player: Identity = Identity.from_json(request_payload[PLAYER_KEY])
    lobby_id: str = request_payload[INSTANCE_KEY]
    instance = instances.get(lobby_id, None)
    if instance is None:
        return jsonify(success=False, reason=RejectionReason.CLOSED)
    instance = instances[lobby_id]

    if instance.is_started():
        if instance.has_player(player):
            game_state, rules = instance.manager.get_current_game()
            game_state_payload = game_state.to_json()
            rules_payload = rules.to_json()
            return jsonify(success=True, game_state=game_state_payload, rules=rules_payload)
        else:
            return jsonify(success=False, reason=RejectionReason.STARTED)
    if instance.is_full():
        return jsonify(success=False, reason=RejectionReason.FULL)
    instance.add_player(player)
    return jsonify(success=True, lobby_state=instance.lobby_state.to_json())

@app.route('/leave_lobby/<string:lobby_id>', methods=['POST'])
def leave_lobby(lobby_id: str):
    instance = instances.get(lobby_id, None)
    if instance is None:
        return get_lobbies()
    request_payload = request.get_json()
    player: Identity = Identity.from_json(request_payload[PLAYER_KEY])

    if instance.is_host(player):
        del instances[lobby_id]
    else:
        instance.remove_player(player)
    return get_lobbies()

@app.route('/update_rules/<string:lobby_id>', methods=['POST'])
def update_rules(lobby_id: str):
    instance = instances.get(lobby_id, None)
    if instance is None: #TODO do I actually need to handle these cases? This is only accessible to the host
        return jsonify(success=False, reason=RejectionReason.CLOSED)
    if instance.is_started():
        return jsonify(success=False, reason=RejectionReason.STARTED)
    request_payload = request.get_json()
    rules_payload = request_payload[RULES_KEY]
    rules = Rules.from_json(rules_payload)
    instance.lobby_state.rules = rules
    return jsonify(success=True, lobby_state=instance.lobby_state.to_json())

@app.route('/start_game/<string:lobby_id>', methods=['POST'])
def start_game(lobby_id: str):
    instance = instances.get(lobby_id, None)
    if instance is None:
        return jsonify(success=False, reason=RejectionReason.CLOSED)
    instance.start_game()
    game_state, rules = instance.manager.get_current_game()
    game_state_payload = game_state.to_json()
    rules_payload = rules.to_json()
    return jsonify(success=True, game_state=game_state_payload, rules=rules_payload)
    

@app.route('/get_lobby_state/<string:lobby_id>', methods=['GET'])
def get_lobby_state(lobby_id: str):
    instance = instances.get(lobby_id, None)
    if instance is None:
        return jsonify(success=False, reason=RejectionReason.CLOSED)
    if instance.is_started():
        game_state, rules = instance.manager.get_current_game()
        game_state_payload = game_state.to_json()
        rules_payload = rules.to_json()
        return jsonify(success=True, game_state=game_state_payload, rules=rules_payload)
    return jsonify(success=True, lobby_state=instance.lobby_state.to_json())


# Game Handlers

@app.route('/action/<string:game_id>', methods=['POST'])
def handle_action(game_id: str):
    instance = instances.get(game_id, None)
    if instance is None:
        return jsonify(success=False, reason=RejectionReason.CLOSED)
    request_payload = request.get_json()
    action_payload = request_payload[ACTION_KEY]
    timestamp = request_payload[TIMESTAMP_KEY]
    action = Action.from_json(action_payload)
    events: list[Event] = instance.manager.handle_action(action, timestamp=timestamp)
    events_payload = [event.to_json() for event in events]
    if len(events) > 0:
        return jsonify(success=True, events=events_payload)
    return jsonify(success=False)

@app.route('/events/<string:game_id>', methods=['GET'])
def get_events(game_id: str):
    instance = instances.get(game_id, None)
    if instance is None:
        return jsonify(success=False, reason=RejectionReason.CLOSED)
    request_payload = request.get_json()
    timestamp = request_payload[TIMESTAMP_KEY]
    events: list[Event] = instance.manager.get_events(timestamp)
    events_payload = [event.to_json() for event in events]
    if len(events) > 0:
        return jsonify(success=True, events=events_payload)
    return jsonify(success=False)

@app.route('/current_game/<string:game_id>', methods=['GET'])
def get_current_game(game_id: str):
    instance = instances.get(game_id, None)
    if instance is None:
        return jsonify(success=False, reason=RejectionReason.CLOSED)
    game_state, rules = instance.manager.get_current_game()
    game_state_payload = game_state.to_json()
    rules_payload = rules.to_json()
    return jsonify(success=True, game_state=game_state_payload, rules=rules_payload)

def get_manager(request_payload: str) -> LocalGameManager:
    instance = instances.get(request_payload[INSTANCE_KEY], None)
    if instance is None:
        return None
    return instances[request_payload[INSTANCE_KEY]].manager

if __name__ == '__main__':
    app.run(debug=True, host=host_ip, port=5000)


