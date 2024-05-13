from flask import Flask, request, jsonify
import os
import sys
sys.path.append(os.getcwd())
from game.management import LocalGameManager
from game.game_objects import Identity, Rules
from game.globals import *
from host.instance import Instance, LobbyInstance, GameInstance
from game.events import Action, Event


app = Flask(__name__)

game_instances = {}
lobby_instances = {}

default_identity = Identity(default_id, default_name)
game_instances[local_game_id] = GameInstance(local_game_id, default_identity, Rules(False, False, True, True), [default_identity])

def get_instance(request_payload: dict) -> Instance:
    return game_instances[request_payload[GAME_ID_KEY]]

# Game Handlers
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify(success=True)

@app.route('/action', methods=['POST'])
def handle_action():
    request_payload = request.get_json()
    manager: LocalGameManager = get_instance(request_payload).manager
    action_payload = request_payload[ACTION_KEY]
    timestamp = request_payload[TIMESTAMP_KEY]
    action = Action.from_json(action_payload)
    events: list[Event] = manager.handle_action(action, timestamp=timestamp)
    events_payload = [event.to_json() for event in events]
    if len(events) > 0:
        return jsonify(events=events_payload, success=True)
    return jsonify(success=False)

@app.route('/events', methods=['GET'])
def get_events():
    request_payload = request.get_json()
    manager: LocalGameManager = get_instance(request_payload).manager
    timestamp = request_payload[TIMESTAMP_KEY]
    events: list[Event] = manager.get_events(timestamp)
    events_payload = [event.to_json() for event in events]
    if len(events) > 0:
        return jsonify(events=events_payload, success=True)
    return jsonify(success=False)


@app.route('/current_game', methods=['GET'])
def get_current_game():
    request_payload = request.get_json()
    manager: LocalGameManager = get_instance(request_payload).manager
    game_state, rules = manager.get_current_game()
    game_state_payload = game_state.to_json()
    rules_payload = rules.to_json()
    return jsonify(game_state=game_state_payload, rules=rules_payload)

if __name__ == '__main__':
    app.run(debug=True, host=host_ip, port=5000)




# def get_instances():
#     return [lobby_instances.values(), game_instances.values()]

# @app.route('/lobbies', methods=['GET'])
# def get_lobbies():
#     return jsonify(Lobbies(*get_instances()))

# @app.route('/start_lobby', methods=['POST'])
# def start_lobby():
#     player = request.json['player']
#     rules = request.json['rules']
#     lobby_instance = LobbyInstance(player, rules)
#     return jsonify(LobbyEvent(lobby_instance.get_lobby()))

# @app.route('/join_lobby', methods=['POST'])
# def join_lobby():
#     player = request.json['player']
#     lobby_id = request.json['lobby_id']
#     lobby_instance = lobby_instances[lobby_id]
#     if lobby_instance == None:
#         return jsonify(LobbyRejected(*get_instances(), Reason.CLOSED), success=False)
#     result = lobby_instance.add_player(player)
#     success = isinstance(result, LobbyRejected)
#     return jsonify(result, success=success)

# @app.route('/leave_lobby', methods=['POST'])
# def leave_lobby():
#     player = request.json['player']
#     lobby_id = request.json['lobby_id']
#     lobby_instance = lobby_instances[lobby_id]
#     lobby_instance.remove_player(player)
#     return get_lobbies()

# @app.route('/lobby_update', methods=['GET'])
# def lobby_update():
#     lobby_id = request.json['lobby_id']
#     lobby_instance = lobby_instances[lobby_id]
#     if lobby_instance is None:
#         game_instance = game_instances[lobby_id]
#         if game_instance is None:
#             return jsonify(LobbyRejected(*get_instances(), Reason.CLOSED))
#         return GameStarting(game_instance)
#     return get_lobbies()
