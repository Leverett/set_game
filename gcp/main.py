from flask import Flask, request, jsonify
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
game_dir = os.path.join(os.path.dirname(current_dir), 'game')
sys.path.insert(0, game_dir)
from game.management import LocalGameManager
from game.game_objects import Player, Rules
from game.constants import *


app = Flask(__name__)

manager = LocalGameManager(Rules.default_rules, {default_id: Player(default_id, default_name)})

@app.route('/action', methods=['POST'])
def handle_action():
    action = request.json['action']
    events = manager.process_action(action)
    if len(events) > 0:
        return jsonify(events, success=True)
    return jsonify(success=False)

@app.route('/events', methods=['GET'])
def get_events():
    events = manager.get_events()
    return jsonify(events)