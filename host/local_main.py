from flask import Flask, request, jsonify
import os
import sys
sys.path.append(os.getcwd())
from game.management import LocalGameManager
from game.game_objects import Player, Rules
from game.globals import *
from mp.lobby_events import *
from game.events import Action, Event
from typing import List
from game.game_state import GameState


    
app = Flask(__name__)

manager = LocalGameManager(Rules.default_rules(), {default_id: Player(default_id, default_name)})

# Game Handlers
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify(success=True)

@app.route('/action', methods=['POST'])
def handle_action():
    action_payload = request.json['action']
    action = Action(**action_payload)
    events: List[Event] = manager.process_action(action)
    if len(events) > 0:
        return jsonify(events, success=True)
    return jsonify(success=False)

@app.route('/events', methods=['GET'])
def get_events():
    timestamp = request.json['timestamp']
    events = manager.get_events(timestamp)
    return jsonify(events)


@app.route('/game_state', methods=['GET'])
def get_game_state():
    game_state: GameState = manager.get_game_state()
    response = game_state.to_json()
    return jsonify(response)

if __name__ == '__main__':
    # app.run(debug=True, host='127.0.0.1', port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000)

