from flask import Flask, render_template, request, jsonify, session
from game.board import Board
from game.square import Square
import os
import json
import time, random


app = Flask(__name__)
app.secret_key = os.urandom(24)

class GameState:
    def __init__(self, strategy=None, color=None):
        self.board =  Board()
        self.strategy = strategy
        self.color = color

    def to_json(self):
        return json.dumps({
            'board': self.board.to_json(),
            'strategy': self.strategy,
            'color': self.color
        })

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        state = GameState()
        state.board = Board.from_json(data['board'])
        state.strategy = data['strategy']
        state.color = data['color']
        return state

@app.route('/')
def index():
    return render_template('index.html')

SESSION_KEY = 'game_state'

''' API Endpoints '''
@app.route('/api/board', methods=['GET'])
def api_board():
    ''' Return current board state as JSON '''
    if not session.get(SESSION_KEY):
        state = new GameState()
    else:
        state = session[SESSION_KEY]

    return state.to_json()

@app.route('/api/reset', methods=['POST'])
def api_reset():
    session.pop(SESSION_KEY, None)
   
    return api_board()

@app.route('/api/start', methods=['POST'])
def api_start():
    data = request.json or {}
    strategy = data.get('strategy', 'first')
    color = data.get('color', 'black')

    state = GameState(strategy=strategy, color=color)
    session[SESSION_KEY] = state
    return state.to_json()

@app.route('/api/pass', methods=['POST'])
def api_pass():
    if not session.get(SESSION_KEY):
        # if no game state, throw error
        return jsonify({'error': 'No game in progress'}), 400
    else:
        state = session[SESSION_KEY]
    
    if state.color != state.board.current_player:
        return jsonify({'error': 'Not your turn'}), 400

    state.board.pass_turn()
    session[SESSION_KEY] = state
    return state.to_json()

@app.route('/api/move', methods=['POST'])
def api_move():
    data = request.json or {}
    if not session.get(SESSION_KEY):
        # if no game state, throw error
        return jsonify({'error': 'No game in progress'}), 400
    else:
        state = session[SESSION_KEY]
    
    if state.color != state.board.current_player:
        return jsonify({'error': 'Not your turn'}), 400

    row = data.get('row')   
    col = data.get('col')
    if row is None or col is None:
        return jsonify({'error': 'Missing row or col'}), 400

    try:
        state.board.make_move((row, col))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    session[SESSION_KEY] = state
    return state.to_json()

@app.route('/api/opponentmove', methods=['POST'])
def api_opponent_move():
    data = request.json or {}
    if not session.get(SESSION_KEY):
        # if no game state, throw error
        return jsonify({'error': 'No game in progress'}), 400
    else:
        state = session[SESSION_KEY]
    
    if state.color == state.board.current_player:
        return jsonify({'error': 'Not opponent\'s turn'}), 400

    # random sleep up to 2 seconds to simulate thinking time
    time.sleep(random.uniform(0, 2))


    if state.strategy == 'random':
        state.board.make_random_move()
    elif state.strategy == 'maxflips':
        state.board.make_maxflips_move()
    elif state.strategy == 'smart':
        state.board.make_smart_move()
    else:  # 'first' or default
        state.board.make_first_move()
    
    session[SESSION_KEY] = state
    return state.to_json()

if __name__ == '__main__':
    app.run(debug=True)
