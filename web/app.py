from flask import Flask, render_template, request, jsonify, session
from game.board import Board
from game.square import Square
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store board in session (simple demo, not for production)
def get_board():
    if 'board' not in session:
        session['board'] = Board()
    return session['board']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/board', methods=['GET'])
def api_board():
    board = get_board()
    grid = [[sq.name for sq in row] for row in board.grid]
    info = {
        'grid': grid,
        'current_turn': board.current_turn.name,
        'white_count': board.count(Square.WHITE),
        'black_count': board.count(Square.BLACK)
    }
    return jsonify(info)

@app.route('/api/move', methods=['POST'])
def api_move():
    board = get_board()
    data = request.json
    row, col = data.get('row'), data.get('col')
    moves = board.open_moves()['moves']
    if (row, col) not in moves:
        return jsonify({'error': 'Invalid move'}), 400
    board.make_move((row, col), moves[(row, col)])
    session['board'] = board
    return jsonify({'success': True})

@app.route('/api/pass', methods=['POST'])
def api_pass():
    board = get_board()
    board.pass_turn()
    session['board'] = board
    return jsonify({'success': True})

@app.route('/api/reset', methods=['POST'])
def api_reset():
    session['board'] = Board()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
