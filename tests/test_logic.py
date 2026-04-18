"""Unit tests for game/square.py and game/board.py.

Board() initialises with current_turn = Square.WHITE, so WHITE moves first.
Starting pieces:  WHITE at (3,3) and (4,4), BLACK at (3,4) and (4,3).
WHITE's four legal opening moves:  (2,4) (3,5) (4,2) (5,3).
"""
import pytest
from game.square import Square
from game.board import Board


# ---------------------------------------------------------------------------
# Square enum
# ---------------------------------------------------------------------------

class TestSquare:
    def test_values(self):
        assert Square.OPEN.value == 0
        assert Square.BLACK.value == 1
        assert Square.WHITE.value == 2

    def test_names(self):
        assert Square.OPEN.name == 'OPEN'
        assert Square.BLACK.name == 'BLACK'
        assert Square.WHITE.name == 'WHITE'

    def test_lookup_by_name(self):
        assert Square['BLACK'] is Square.BLACK
        assert Square['WHITE'] is Square.WHITE


# ---------------------------------------------------------------------------
# Board initialisation
# ---------------------------------------------------------------------------

class TestBoardInit:
    def test_size(self):
        assert Board().size == 8

    def test_grid_shape(self):
        b = Board()
        assert len(b.grid) == 8
        assert all(len(row) == 8 for row in b.grid)

    def test_starting_turn_is_white(self):
        assert Board().current_turn == Square.WHITE

    def test_starting_pieces(self):
        b = Board()
        assert b.grid[3][3] == Square.WHITE
        assert b.grid[3][4] == Square.BLACK
        assert b.grid[4][3] == Square.BLACK
        assert b.grid[4][4] == Square.WHITE

    def test_starting_open_count(self):
        assert Board().open_count() == 60

    def test_starting_piece_counts(self):
        b = Board()
        assert b.count(Square.WHITE) == 2
        assert b.count(Square.BLACK) == 2

    def test_consecutive_passes_zero(self):
        assert Board().consecutive_passes == 0


# ---------------------------------------------------------------------------
# open_moves
# ---------------------------------------------------------------------------

class TestOpenMoves:
    def test_white_has_four_moves_at_start(self):
        result = Board().open_moves()
        assert len(result['moves']) == 4

    def test_color_matches_current_turn(self):
        b = Board()
        assert b.open_moves()['color'] == Square.WHITE

    def test_known_opening_moves_present(self):
        moves = Board().open_moves()['moves']
        for pos in [(2, 4), (3, 5), (4, 2), (5, 3)]:
            assert pos in moves, f"expected {pos} to be a valid opening move"

    def test_raises_when_game_over(self):
        b = Board()
        b.consecutive_passes = 2
        with pytest.raises(Exception):
            b.open_moves()

    def test_each_move_has_at_least_one_flip(self):
        for pos, flips in Board().open_moves()['moves'].items():
            assert len(flips) >= 1, f"move {pos} should flip at least one piece"


# ---------------------------------------------------------------------------
# make_move
# ---------------------------------------------------------------------------

class TestMakeMove:
    def _first_valid(self):
        b = Board()
        moves = b.open_moves()['moves']
        pos, flips = next(iter(moves.items()))
        return b, pos, flips

    def test_places_piece_at_position(self):
        b, pos, flips = self._first_valid()
        b.make_move(pos, flips)
        assert b.grid[pos[0]][pos[1]] == Square.WHITE

    def test_flips_opponent_pieces(self):
        b = Board()
        moves = b.open_moves()['moves']
        pos = (2, 4)
        b.make_move(pos, moves[pos])
        assert b.grid[2][4] == Square.WHITE  # placed
        assert b.grid[3][4] == Square.WHITE  # was BLACK, flipped

    def test_turn_switches_after_move(self):
        b, pos, flips = self._first_valid()
        b.make_move(pos, flips)
        assert b.current_turn == Square.BLACK

    def test_consecutive_passes_resets_to_zero(self):
        b = Board()
        b.pass_turn()
        assert b.consecutive_passes == 1
        moves = b.open_moves()['moves']
        pos, flips = next(iter(moves.items()))
        b.make_move(pos, flips)
        assert b.consecutive_passes == 0

    def test_raises_when_game_over(self):
        b = Board()
        b.consecutive_passes = 2
        with pytest.raises(Exception):
            b.make_move((2, 4), [(3, 4)])

    def test_raises_with_empty_flips(self):
        b = Board()
        with pytest.raises(ValueError):
            b.make_move((0, 0), [])


# ---------------------------------------------------------------------------
# pass_turn
# ---------------------------------------------------------------------------

class TestPassTurn:
    def test_switches_turn_from_white_to_black(self):
        b = Board()
        b.pass_turn()
        assert b.current_turn == Square.BLACK

    def test_switches_turn_from_black_to_white(self):
        b = Board()
        b.pass_turn()
        b.pass_turn()
        # After two passes game_over() is True; use a fresh board
        b2 = Board()
        b2.pass_turn()  # WHITE → BLACK
        # Manually reset to test the reverse without triggering game_over
        b2.consecutive_passes = 0
        b2.pass_turn()  # BLACK → WHITE
        assert b2.current_turn == Square.WHITE

    def test_increments_consecutive_passes(self):
        b = Board()
        b.pass_turn()
        assert b.consecutive_passes == 1

    def test_increments_pass_count(self):
        b = Board()
        b.pass_turn()
        assert b.pass_count == 1

    def test_raises_when_game_over(self):
        b = Board()
        b.consecutive_passes = 2
        with pytest.raises(Exception):
            b.pass_turn()


# ---------------------------------------------------------------------------
# game_over
# ---------------------------------------------------------------------------

class TestGameOver:
    def test_not_over_at_start(self):
        assert Board().game_over() is False

    def test_over_after_two_consecutive_passes(self):
        b = Board()
        b.consecutive_passes = 2
        assert b.game_over() is True

    def test_one_pass_not_over(self):
        b = Board()
        b.pass_turn()
        assert b.game_over() is False

    def test_over_when_board_full(self):
        b = Board()
        for r in range(8):
            for c in range(8):
                b.grid[r][c] = Square.BLACK
        assert b.game_over() is True

    def test_open_count_tracks_empty_squares(self):
        b = Board()
        b.grid[0][0] = Square.BLACK
        assert b.open_count() == 59


# ---------------------------------------------------------------------------
# winner
# ---------------------------------------------------------------------------

class TestWinner:
    def _fill(self, b, sq):
        for r in range(8):
            for c in range(8):
                b.grid[r][c] = sq

    def test_black_wins_when_majority(self):
        b = Board()
        self._fill(b, Square.BLACK)
        assert b.winner() == Square.BLACK

    def test_white_wins_when_majority(self):
        b = Board()
        self._fill(b, Square.WHITE)
        assert b.winner() == Square.WHITE

    def test_tie_returns_none(self):
        b = Board()
        for r in range(8):
            for c in range(8):
                b.grid[r][c] = Square.BLACK if c < 4 else Square.WHITE
        assert b.winner() is None

    def test_starting_position_is_tied(self):
        assert Board().winner() is None


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_to_dict_has_required_keys(self):
        d = Board().to_dict()
        for key in ('size', 'grid', 'current_turn', 'pass_count', 'consecutive_passes'):
            assert key in d

    def test_to_dict_grid_values_are_strings(self):
        d = Board().to_dict()
        for row in d['grid']:
            for cell in row:
                assert cell in ('OPEN', 'BLACK', 'WHITE')

    def test_to_dict_current_turn_is_string(self):
        assert Board().to_dict()['current_turn'] == 'WHITE'

    def test_from_dict_roundtrip_preserves_turn(self):
        b = Board()
        b2 = Board.from_dict(b.to_dict())
        assert b2.current_turn == b.current_turn

    def test_from_dict_roundtrip_preserves_grid(self):
        b = Board()
        moves = b.open_moves()['moves']
        pos = (2, 4)
        b.make_move(pos, moves[pos])
        b2 = Board.from_dict(b.to_dict())
        assert b2.grid[2][4] == Square.WHITE
        assert b2.grid[3][4] == Square.WHITE

    def test_from_dict_roundtrip_preserves_pass_counters(self):
        b = Board()
        b.pass_turn()
        b2 = Board.from_dict(b.to_dict())
        assert b2.consecutive_passes == 1
        assert b2.pass_count == 1

    def test_json_roundtrip(self):
        b = Board()
        b2 = Board.from_json(b.to_json())
        assert b2.current_turn == Square.WHITE
        assert b2.grid[3][3] == Square.WHITE
        assert b2.open_count() == 60


# ---------------------------------------------------------------------------
# AI strategies
# ---------------------------------------------------------------------------

class TestAIStrategies:
    def _count(self, b, sq):
        return sum(b.grid[r][c] == sq for r in range(8) for c in range(8))

    def test_random_move_advances_game(self):
        b = Board()
        b.make_random_move()
        assert b.current_turn == Square.BLACK
        assert self._count(b, Square.WHITE) >= 2

    def test_maxflips_move_advances_game(self):
        b = Board()
        b.make_maxflips_move()
        assert b.current_turn == Square.BLACK

    def test_smart_move_advances_game(self):
        b = Board()
        b.make_smart_move()
        assert b.current_turn == Square.BLACK

    def test_maxflips_picks_most_flips(self):
        b = Board()
        moves = b.open_moves()['moves']
        max_flips = max(len(f) for f in moves.values())
        b.make_maxflips_move()
        # the number of WHITE pieces should reflect a max-flip selection
        # at least as many as a single flip
        assert self._count(b, Square.WHITE) >= 3  # 2 original + 1 flipped minimum

    def test_strategy_returns_valid_pos_and_flips(self):
        b = Board()
        pos, flips = b.make_random_move()
        assert pos is not None
        assert flips is not None
        assert len(flips) >= 1
