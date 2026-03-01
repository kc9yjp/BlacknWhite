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
    session['strategy'] = 'first'  # default strategy
    return render_template('index.html')

@app.route('/api/board', methods=['GET'])
def api_board():
    board = get_board()
    grid = [[sq.name for sq in row] for row in board.grid]
    
    # Get available moves for the current player
    available_moves = []
    game_over = board.game_over()
    if not game_over:
        try:
            moves = board.open_moves()
            available_moves = list(moves['moves'].keys())
        except:
            pass
    
    # Get winner info
    winner = None
    if game_over:
        winner_sq = board.winner()
        if winner_sq:
            winner = winner_sq.name
        else:
            winner = 'TIE'
    
    info = {
        'grid': grid,
        'current_turn': board.current_turn.name,
        'white_count': board.count(Square.WHITE),
        'black_count': board.count(Square.BLACK),
        'available_moves': available_moves,
        'game_over': game_over,
        'winner': winner
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
    data = request.json or {}
    strategy = data.get('strategy', 'first')
    session['board'] = Board()
    session['strategy'] = strategy
    return jsonify({'success': True})

@app.route('/api/ai_move', methods=['POST'])
def api_ai_move():
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
    
    session['board'] = board
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
