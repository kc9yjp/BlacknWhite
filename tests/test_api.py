"""Flask API endpoint tests.

Board() initialises with current_turn = WHITE, so when the player starts as
WHITE it is immediately their turn; when they start as BLACK the AI (WHITE)
must move first.
"""
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def start(client, color='WHITE', strategy='random'):
    return client.post('/api/start', json={'color': color, 'strategy': strategy})


def board(client):
    return client.get('/api/board').get_json()


def first_valid_move(client):
    """Start as WHITE (whose turn it is) and return the first valid move."""
    start(client, 'WHITE', 'random')
    moves = board(client)['valid_moves']
    assert moves, "expected valid moves for WHITE at game start"
    return moves[0]


# ---------------------------------------------------------------------------
# GET /api/board
# ---------------------------------------------------------------------------

class TestGetBoard:
    def test_returns_200(self, client):
        assert client.get('/api/board').status_code == 200

    def test_default_board_structure(self, client):
        data = board(client)
        assert 'board' in data
        assert 'strategy' in data
        assert 'color' in data
        assert 'valid_moves' in data

    def test_default_board_size(self, client):
        assert board(client)['board']['size'] == 8

    def test_default_turn_is_white(self, client):
        assert board(client)['board']['current_turn'] == 'WHITE'

    def test_no_valid_moves_without_active_game(self, client):
        assert board(client)['valid_moves'] == []

    def test_color_and_strategy_none_without_game(self, client):
        data = board(client)
        assert data['color'] is None
        assert data['strategy'] is None


# ---------------------------------------------------------------------------
# POST /api/start
# ---------------------------------------------------------------------------

class TestStart:
    def test_start_as_white(self, client):
        res = start(client, 'WHITE', 'random')
        assert res.status_code == 200
        data = res.get_json()
        assert data['color'] == 'WHITE'
        assert data['strategy'] == 'random'

    def test_start_as_black(self, client):
        res = start(client, 'BLACK', 'smart')
        data = res.get_json()
        assert data['color'] == 'BLACK'
        assert data['strategy'] == 'smart'

    def test_all_valid_strategies(self, client):
        for strat in ('random', 'maxflips', 'smart', 'first'):
            res = start(client, 'WHITE', strat)
            assert res.get_json()['strategy'] == strat

    def test_invalid_strategy_defaults_to_first(self, client):
        data = start(client, 'WHITE', 'telepathy').get_json()
        assert data['strategy'] == 'first'

    def test_invalid_color_defaults_to_black(self, client):
        data = start(client, 'RED', 'random').get_json()
        assert data['color'] == 'BLACK'

    def test_valid_moves_populated_when_player_turn(self, client):
        # WHITE goes first; starting as WHITE → moves immediately available
        start(client, 'WHITE', 'random')
        assert len(board(client)['valid_moves']) == 4

    def test_valid_moves_empty_when_not_player_turn(self, client):
        # BLACK does not move first; valid_moves should be empty until the AI goes
        start(client, 'BLACK', 'random')
        assert board(client)['valid_moves'] == []

    def test_start_resets_previous_game(self, client):
        start(client, 'WHITE', 'random')
        valid = board(client)['valid_moves'][0]
        client.post('/api/move', json={'row': valid[0], 'col': valid[1]})
        # start again — board should reset to the starting position
        start(client, 'WHITE', 'random')
        assert board(client)['board']['current_turn'] == 'WHITE'
        assert len(board(client)['valid_moves']) == 4


# ---------------------------------------------------------------------------
# POST /api/move
# ---------------------------------------------------------------------------

class TestMove:
    def test_valid_move_returns_200(self, client):
        row, col = first_valid_move(client)
        assert client.post('/api/move', json={'row': row, 'col': col}).status_code == 200

    def test_valid_move_places_piece(self, client):
        row, col = first_valid_move(client)
        client.post('/api/move', json={'row': row, 'col': col})
        assert board(client)['board']['grid'][row][col] == 'WHITE'

    def test_valid_move_switches_turn(self, client):
        row, col = first_valid_move(client)
        client.post('/api/move', json={'row': row, 'col': col})
        assert board(client)['board']['current_turn'] == 'BLACK'

    def test_no_session_returns_400(self, client):
        assert client.post('/api/move', json={'row': 2, 'col': 4}).status_code == 400

    def test_missing_row_returns_400(self, client):
        start(client, 'WHITE', 'random')
        assert client.post('/api/move', json={'col': 4}).status_code == 400

    def test_missing_col_returns_400(self, client):
        start(client, 'WHITE', 'random')
        assert client.post('/api/move', json={'row': 2}).status_code == 400

    def test_non_integer_row_returns_400(self, client):
        start(client, 'WHITE', 'random')
        assert client.post('/api/move', json={'row': 'two', 'col': 4}).status_code == 400

    def test_out_of_range_row_returns_400(self, client):
        start(client, 'WHITE', 'random')
        assert client.post('/api/move', json={'row': -1, 'col': 0}).status_code == 400

    def test_out_of_range_col_returns_400(self, client):
        start(client, 'WHITE', 'random')
        assert client.post('/api/move', json={'row': 0, 'col': 8}).status_code == 400

    def test_illegal_square_returns_400(self, client):
        start(client, 'WHITE', 'random')
        # (0,0) is never a valid opening move
        assert client.post('/api/move', json={'row': 0, 'col': 0}).status_code == 400

    def test_wrong_turn_returns_400(self, client):
        # Start as BLACK — it's WHITE's (AI's) turn, so the player cannot move
        start(client, 'BLACK', 'random')
        assert client.post('/api/move', json={'row': 2, 'col': 4}).status_code == 400

    def test_response_includes_valid_moves(self, client):
        row, col = first_valid_move(client)
        data = client.post('/api/move', json={'row': row, 'col': col}).get_json()
        # After WHITE moves it's BLACK's turn; player is WHITE, so valid_moves empty
        assert data['valid_moves'] == []


# ---------------------------------------------------------------------------
# POST /api/pass
# ---------------------------------------------------------------------------

class TestPass:
    def test_no_session_returns_400(self, client):
        assert client.post('/api/pass').status_code == 400

    def test_wrong_turn_returns_400(self, client):
        # Start as BLACK — it's WHITE's turn, player (BLACK) cannot pass
        start(client, 'BLACK', 'random')
        assert client.post('/api/pass').status_code == 400

    def test_pass_on_player_turn_returns_200(self, client):
        start(client, 'WHITE', 'random')
        assert client.post('/api/pass').status_code == 200

    def test_pass_switches_turn(self, client):
        start(client, 'WHITE', 'random')
        client.post('/api/pass')
        assert board(client)['board']['current_turn'] == 'BLACK'

    def test_pass_increments_consecutive_passes(self, client):
        start(client, 'WHITE', 'random')
        client.post('/api/pass')
        assert board(client)['board']['consecutive_passes'] == 1


# ---------------------------------------------------------------------------
# POST /api/opponentmove
# ---------------------------------------------------------------------------

class TestOpponentMove:
    def test_no_session_returns_400(self, client):
        assert client.post('/api/opponentmove').status_code == 400

    def test_player_turn_returns_400(self, client):
        # Start as WHITE — it's WHITE's (player's) turn, so opponent cannot move
        start(client, 'WHITE', 'random')
        assert client.post('/api/opponentmove').status_code == 400

    def test_opponent_move_returns_200(self, client):
        # Start as BLACK — it's WHITE's (AI's) turn
        start(client, 'BLACK', 'random')
        assert client.post('/api/opponentmove').status_code == 200

    def test_opponent_move_switches_turn_to_player(self, client):
        start(client, 'BLACK', 'random')
        client.post('/api/opponentmove')
        assert board(client)['board']['current_turn'] == 'BLACK'

    def test_opponent_move_valid_moves_populated(self, client):
        start(client, 'BLACK', 'random')
        client.post('/api/opponentmove')
        # Now it's BLACK's (player's) turn — valid_moves should be populated
        assert len(board(client)['valid_moves']) > 0

    def test_all_strategies_work(self, client):
        for strat in ('random', 'maxflips', 'smart', 'first'):
            start(client, 'BLACK', strat)
            res = client.post('/api/opponentmove')
            assert res.status_code == 200, f"strategy {strat!r} failed"


# ---------------------------------------------------------------------------
# POST /api/reset
# ---------------------------------------------------------------------------

class TestReset:
    def test_reset_returns_200(self, client):
        assert client.post('/api/reset').status_code == 200

    def test_reset_clears_color(self, client):
        start(client, 'WHITE', 'random')
        client.post('/api/reset')
        assert board(client)['color'] is None

    def test_reset_clears_strategy(self, client):
        start(client, 'WHITE', 'random')
        client.post('/api/reset')
        assert board(client)['strategy'] is None

    def test_reset_clears_valid_moves(self, client):
        start(client, 'WHITE', 'random')
        client.post('/api/reset')
        assert board(client)['valid_moves'] == []

    def test_reset_restores_default_board(self, client):
        start(client, 'WHITE', 'random')
        row, col = board(client)['valid_moves'][0]
        client.post('/api/move', json={'row': row, 'col': col})
        client.post('/api/reset')
        b = board(client)['board']
        assert b['current_turn'] == 'WHITE'
        assert b['consecutive_passes'] == 0


# ---------------------------------------------------------------------------
# GET / (index page)
# ---------------------------------------------------------------------------

class TestIndexPage:
    def test_serves_html(self, client):
        res = client.get('/')
        assert res.status_code == 200
        assert b'BlacknWhite' in res.data

    def test_references_game_js(self, client):
        res = client.get('/')
        assert b'game.js' in res.data

    def test_static_js_accessible(self, client):
        assert client.get('/static/game.js').status_code == 200

    def test_static_css_accessible(self, client):
        assert client.get('/static/style.css').status_code == 200
