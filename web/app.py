from flask import Flask, render_template, request, jsonify, session
from game.board import Board
from game.square import Square
import os
import json


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


class GameState:
    """Holds all per-session game data: the board, the player's color, and the AI strategy.

    Instances are serialised to JSON for storage in the Flask session cookie and
    deserialised on each request via :meth:`from_json`.
    """

    def __init__(self, strategy=None, color=None):
        """Create a fresh game with a new board.

        Args:
            strategy: AI strategy for the opponent — ``'random'``, ``'maxflips'``,
                ``'smart'``, or ``'first'`` (default).
            color: The human player's color as an uppercase string — ``'BLACK'`` or
                ``'WHITE'``.
        """
        self.board = Board()
        self.strategy = strategy
        self.color = color

    def to_json(self):
        """Serialise the game state to a JSON string suitable for session storage.

        The board is embedded as a plain dict (not a nested JSON string) so the
        client can read all fields without a second ``JSON.parse`` call.
        """
        return json.dumps(
            {
                "board": self.board.to_dict(),
                "strategy": self.strategy,
                "color": self.color,
            }
        )

    @staticmethod
    def from_json(json_str):
        """Deserialise a JSON string produced by :meth:`to_json` back into a GameState.

        Args:
            json_str: The JSON string from the session cookie.

        Returns:
            A fully reconstructed :class:`GameState` instance.
        """
        data = json.loads(json_str)
        state = GameState()
        state.board = Board.from_dict(data["board"])
        state.strategy = data["strategy"]
        state.color = data["color"]
        return state


@app.route("/")
def index():
    """Serve the main game page."""
    return render_template("index.html")


SESSION_KEY = "game_state"

""" API Endpoints """


@app.route("/api/board", methods=["GET"])
def api_board():
    """Return the current game state as JSON.

    If no session exists, returns a default (unstarted) board.
    """
    if not session.get(SESSION_KEY):
        state = GameState()
    else:
        state = GameState.from_json(session[SESSION_KEY])

    return state.to_json()


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Clear the session and return a fresh default board."""
    session.pop(SESSION_KEY, None)

    return api_board()


@app.route("/api/start", methods=["POST"])
def api_start():
    """Start a new game with the chosen player color and AI strategy.

    Request body (JSON):
        color    -- ``'BLACK'`` or ``'WHITE'`` (default ``'BLACK'``)
        strategy -- ``'random'``, ``'maxflips'``, ``'smart'``, or ``'first'`` (default)
    """
    data = request.json or {}
    strategy = data.get("strategy", "first")
    color = data.get("color", "BLACK").upper()

    state = GameState(strategy=strategy, color=color)
    session[SESSION_KEY] = state.to_json()
    return state.to_json()


@app.route("/api/pass", methods=["POST"])
def api_pass():
    """Pass the current player's turn.

    Returns 400 if there is no active game or it is not the player's turn.
    """
    if not session.get(SESSION_KEY):
        # if no game state, throw error
        return jsonify({"error": "No game in progress"}), 400
    else:
        state = GameState.from_json(session[SESSION_KEY])

    if state.color != state.board.current_turn.name:
        return jsonify({"error": "Not your turn"}), 400

    state.board.pass_turn()
    session[SESSION_KEY] = state.to_json()
    return state.to_json()


@app.route("/api/move", methods=["POST"])
def api_move():
    """Apply the player's move at the given board position.

    Request body (JSON):
        row -- zero-based row index
        col -- zero-based column index

    Returns 400 if there is no active game, it is not the player's turn,
    the game is already over, or the chosen square is not a legal move.
    """
    data = request.json or {}
    if not session.get(SESSION_KEY):
        # if no game state, throw error
        return jsonify({"error": "No game in progress"}), 400
    else:
        state = GameState.from_json(session[SESSION_KEY])

    if state.color != state.board.current_turn.name:
        return jsonify({"error": "Not your turn"}), 400

    row = data.get("row")
    col = data.get("col")
    if row is None or col is None:
        return jsonify({"error": "Missing row or col"}), 400

    if state.board.game_over():
        return jsonify({"error": "Game is over"}), 400
    moves = state.board.open_moves()["moves"]
    pos = (row, col)
    if pos not in moves:
        return jsonify({"error": "Invalid move"}), 400
    try:
        state.board.make_move(pos, moves[pos])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    session[SESSION_KEY] = state.to_json()
    return state.to_json()


@app.route("/api/opponentmove", methods=["POST"])
def api_opponent_move():
    """Make one move for the AI opponent using the session's chosen strategy.

    Includes a random delay of up to 2 seconds to simulate thinking time.
    Returns 400 if there is no active game, it is the player's turn, or
    the game is already over.
    """
    if not session.get(SESSION_KEY):
        # if no game state, throw error
        return jsonify({"error": "No game in progress"}), 400
    else:
        state = GameState.from_json(session[SESSION_KEY])

    if state.color == state.board.current_turn.name:
        return jsonify({"error": "Not opponent's turn"}), 400

    if state.board.game_over():
        return jsonify({"error": "Game is over"}), 400

    if state.strategy == "random":
        state.board.make_random_move()
    elif state.strategy == "maxflips":
        state.board.make_maxflips_move()
    elif state.strategy == "smart":
        state.board.make_smart_move()
    else:  # 'first' or default
        moves = state.board.open_moves()["moves"]
        if moves:
            pos, flips = next(iter(moves.items()))
            state.board.make_move(pos, flips)
        else:
            state.board.pass_turn()

    session[SESSION_KEY] = state.to_json()
    return state.to_json()


if __name__ == "__main__":
    app.run(debug=True)
