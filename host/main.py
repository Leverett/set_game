from flask import Flask, request, jsonify
import os
import sys
sys.path.append(os.getcwd())
from game.management import LocalGameManager
from game.game_objects import Player, Rules
from game.globals import *
from mp.lobby_events import *
from host.lobby_instance import LobbyInstance


app = Flask(__name__)

game_instances = {}
lobby_instances = {}

manager = LocalGameManager(Rules.default_rules(), {default_id: Player(default_id, default_name)})

def get_instances():
    return [lobby_instances.values(), game_instances.values()]

@app.route('/lobbies', methods=['GET'])
def get_lobbies():
    return jsonify(Lobbies(*get_instances()))

@app.route('/start_lobby', methods=['POST'])
def start_lobby():
    player = request.json['player']
    rules = request.json['rules']
    lobby_instance = LobbyInstance(player, rules)
    return jsonify(LobbyEvent(lobby_instance.get_lobby()))

@app.route('/join_lobby', methods=['POST'])
def join_lobby():
    player = request.json['player']
    lobby_id = request.json['lobby_id']
    lobby_instance = lobby_instances[lobby_id]
    if lobby_instance == None:
        return jsonify(LobbyRejected(*get_instances(), Reason.CLOSED), success=False)
    result = lobby_instance.add_player(player)
    success = isinstance(result, LobbyRejected)
    return jsonify(result, success=success)

@app.route('/leave_lobby', methods=['POST'])
def leave_lobby():
    player = request.json['player']
    lobby_id = request.json['lobby_id']
    lobby_instance = lobby_instances[lobby_id]
    lobby_instance.remove_player(player)
    return get_lobbies()

@app.route('/lobby_update', methods=['GET'])
def lobby_update():
    lobby_id = request.json['lobby_id']
    lobby_instance = lobby_instances[lobby_id]
    if lobby_instance is None:
        game_instance = game_instances[lobby_id]
        if game_instance is None:
            return jsonify(LobbyRejected(*get_instances(), Reason.CLOSED))
        return GameStarting(game_instance)
    return get_lobbies()

# Game Handlers

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

if __name__ == '__main__':
    app.run(debug=True)