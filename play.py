"""
CLI for playing the BlacknWhite board game.

This module provides a simple command line interface (CLI) to play the
BlacknWhite board game locally. It prompts the human player for a color
(Black or White), asks them to choose an opponent strategy, and runs the
main game loop until the game ends.

Main responsibilities:
  - Display the board in a readable text format.
  - Prompt and validate human moves.
  - Delegate opponent moves to `Board` strategy methods.
  - Print the final score and the winner.

Usage:
    python play.py

Dependencies:
    - game.board.Board
    - game.square.Square

Opponent strategy mapping:
    'first'   : pick the first available move
    'random'  : Board.make_random_move()
    'maxflips': Board.make_maxflips_move()
    'smart'   : Board.make_smart_move()

This file only updates documentation and user-facing CLI prompts; it does
not change game logic or Board APIs.
"""
import sys
from game.board import Board
from game.square import Square


def print_board(board):
    """Print the board to stdout in a human-readable ASCII format.

    Format example for a 8x8 board:
      0 1 2 3 4 5 6 7   <- column indices
    0 . . . . . . . .
    1 . . B W . . . .  <- row index followed by cells (B=Black, W=White, .=empty)

    Args:
        board: an instance of `Board` with attributes `size` and `grid`.
    """
    print("  " + " ".join(str(i) for i in range(board.size)))
    for r in range(board.size):
        row = []
        for c in range(board.size):
            sq = board.grid[r][c]
            if sq == Square.BLACK:
                row.append('B')
            elif sq == Square.WHITE:
                row.append('W')
            else:
                row.append('.')
        print(f"{r} " + " ".join(row))


def get_opponent_move(board, strategy):
    """Select and apply an opponent move using the chosen strategy.

    The function calls the corresponding `Board` helper for the strategy
    (when available). For the fallback 'first' strategy it queries
    `board.open_moves()` and picks the first available move.

    Args:
        board: Board instance whose turn is the opponent's.
        strategy: strategy name (one of 'first', 'random', 'maxflips', 'smart').

    Returns:
        A tuple (move_square, move_flips) describing the move that was made,
        or (None, None) if the opponent had to pass (no valid moves).
    """
    # Use Board's move methods for strategies
    if strategy == 'random':
        move_square, move_flips = board.make_random_move()
    elif strategy == 'maxflips':
        move_square, move_flips = board.make_maxflips_move()
    elif strategy == 'smart':
        move_square, move_flips = board.make_smart_move()
    else:  # default to 'first' (pick first available)
        moves = board.open_moves()
        # `moves` is expected to be a dict with a 'moves' key mapping squares to flip lists
        if not moves['moves']:
            board.pass_turn()
            return None, None
        move_square = list(moves['moves'].keys())[0]
        move_flips = moves['moves'][move_square]
        board.make_move(move_square, move_flips)
    return move_square, move_flips


def main():
    """Main CLI entry point.

    Interacts with the user to select a color and opponent strategy, then
    runs the game loop until the game finishes. At the end it prints the
    final counts and winner.
    """

    print("Welcome to BlacknWhite CLI!")
    color = input("Choose your color (B for Black, W for White): ").strip().upper()
    while color not in ('B', 'W'):
        color = input("Invalid color. Choose 'B' or 'W': ").strip().upper()
    player_color = Square.BLACK if color == 'B' else Square.WHITE
    opponent_color = Square.WHITE if player_color == Square.BLACK else Square.BLACK

    print("Opponent strategies: first, random, maxflips, smart")
    strategy = input("Choose opponent strategy: ").strip().lower()
    if strategy not in ('first', 'random', 'maxflips', 'smart'):
        strategy = 'random'
        print("Unknown strategy, defaulting to 'random'.")

    board = Board()

    while not board.game_over():
        print_board(board)
        print(f"Current turn: {'B' if board.current_turn == Square.BLACK else 'W'}")
        moves = board.open_moves()
        # `moves['moves']` is a mapping: square -> list_of_flipped_squares
        valid_moves = moves['moves']
        if not valid_moves:
            print(f"No valid moves for {'B' if board.current_turn == Square.BLACK else 'W'}. Passing turn.")
            board.pass_turn()
            continue
        if board.current_turn == player_color:
            print(f"Your turn ({'B' if player_color == Square.BLACK else 'W'})")
            print("Available moves:")
            for sq, flips in valid_moves.items():
                print(f"  {sq} flips {len(flips)} pieces")
            move = input("Enter your move as 'row col' or type 'pass': ").strip()
            if move.lower() == 'pass':
                board.pass_turn()
                continue
            try:
                x, y = map(int, move.split())
                if (x, y) not in valid_moves:
                    print("Invalid move. Try again.")
                    continue
                board.make_move((x, y), valid_moves[(x, y)])
            except Exception:
                print("Invalid input. Enter as 'row col' or 'pass'.")
                continue
        else:
            print(f"Opponent's turn ({'B' if board.current_turn == Square.BLACK else 'W'}) [{strategy}]")
            move_square, move_flips = get_opponent_move(board, strategy)
            if move_square is not None:
                print(f"Opponent plays: {move_square} flipping {len(move_flips)} pieces")
            else:
                print("Opponent passes.")

    print_board(board)
    winner = board.winner()
    white_count = board.count(Square.WHITE)
    black_count = board.count(Square.BLACK)
    print(f"White: {white_count}, Black: {black_count}")
    if winner == player_color:
        print("You win!")
    elif winner == opponent_color:
        print("Opponent wins!")
    else:
        print("It's a tie!")

if __name__ == "__main__":
    main()
