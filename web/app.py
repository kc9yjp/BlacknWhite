from flask import Flask, render_template, request, jsonify, session
from game.board import Board
from game.square import Square
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')


# Store board in session (simple demo, not for production)
def get_board():
    if 'board' not in session:
        board = Board()
        session['board'] = board.to_json()
    else:
        board = Board.from_json(session['board'])
    return board

@app.route('/api/board', methods=['GET'])
def api_board():
    board = get_board()
    return board.to_json()

@app.route('/api/pass', methods=['POST'])
def api_pass():
    board = get_board()
    board.pass_turn()
    session['board'] = board.to_json()
    return board.to_json()

@app.route('/api/reset', methods=['POST'])
def api_reset():
    data = request.json or {}
    
    session['board'] = None
    board = get_board()  # Initialize new board
   
    return board.to_json()

@app.route('/api/move', methods=['POST'])
def api_move():
    board = get_board()
    strategy = session.get('strategy', 'first')
    
    if strategy == 'random':
        board.make_random_move()
    elif strategy == 'maxflips':
        board.make_maxflips_move()
    elif strategy == 'smart':
        board.make_smart_move()
    else:  # 'first' or default
        moves = board.open_moves()['moves']
        if not moves:
            board.pass_turn()
        else:
            move, flips = next(iter(moves.items()))
            board.make_move(move, flips)
    
    session['board'] = board.to_json()
    return session['board']

if __name__ == '__main__':
    app.run(debug=True)
