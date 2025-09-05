"""
test_stats.py

Plays 100 games with White making random moves and Black making maxflips moves.
Summarizes the final counts for White and Black after all games.
"""

from game import Board, Square

games = 5000


# Play make_random_move, make_maxflips_move, and max_smart_move against each other for 1000 games each
strategies = [
    "make_smart_move", "make_random_move", "make_maxflips_move"
]
def play_games(white_strategy, black_strategy, games):
    white_wins = 0
    black_wins = 0
    ties = 0
    white_counts = []
    black_counts = []

    for i in range(games):
        board = Board()
        if i % 2 == 0:
            board.current_turn = Square.BLACK

        while not board.game_over():
            if board.current_turn == Square.WHITE:
                move_square, move_flips = getattr(board, white_strategy)()
            else:
                move_square, move_flips = getattr(board, black_strategy)()
        white_count = board.count(Square.WHITE)
        black_count = board.count(Square.BLACK)
        white_counts.append(white_count)
        black_counts.append(black_count)
        if white_count > black_count:
            white_wins += 1
        elif black_count > white_count:
            black_wins += 1
        else:
            ties += 1

    print(f"{white_strategy} \t{black_strategy} \t{games} \t{white_wins} \t{black_wins} \t{ties} \t{sum(white_counts)/games:.2f} \t{sum(black_counts)/games:.2f}")


print(f"White Strategy \tBlack Strategy \tGames \tWhite Wins \tBlack Wins \tTies \tWhite Avg \tBlack Avg")
for strategy1 in strategies:
    for strategy2 in strategies:
        play_games(strategy1, strategy2, games)
