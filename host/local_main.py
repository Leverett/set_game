from flask import Flask, request, jsonify
import os
import sys
sys.path.append(os.getcwd())
from game.management import LocalGameManager
from game.game_objects import Player, Identity, Rules
from game.globals import *
from mp.lobby_events import *
from game.events import Action, Event


    
app = Flask(__name__)

# manager = LocalGameManager(Rules.default_rules(), {default_id: Player(default_id, default_name)})
default_identity = Identity(default_id, default_name)
manager = LocalGameManager(Rules(False, False, True, True), [Player(default_identity)])

# Game Handlers
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify(success=True)

@app.route('/action', methods=['POST'])
def handle_action():
    request_payload = request.get_json()
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
    timestamp = request_payload[TIMESTAMP_KEY]
    events: list[Event] = manager.get_events(timestamp)
    events_payload = [event.to_json() for event in events]
    if len(events) > 0:
        return jsonify(events=events_payload, success=True)
    return jsonify(success=False)


@app.route('/current_game', methods=['GET'])
def get_current_game():
    game_state, rules = manager.get_current_game()
    game_state_payload = game_state.to_json()
    rules_payload = rules.to_json()
    return jsonify(game_state=game_state_payload, rules=rules_payload)

if __name__ == '__main__':
    app.run(debug=True, host=host_ip, port=5000)

