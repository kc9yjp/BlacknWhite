"""
test_stats.py

Plays 100 games with White making random moves and Black making maxflips moves.
Summarizes the final counts for White and Black after all games.
"""

from game import Board, Square

games = 1000
white_wins = 0
black_wins = 0
ties = 0
white_counts = []
black_counts = []

for i in range(games):
    board = Board()
    while not board.game_over():
        if board.current_turn == Square.WHITE:
            move_square, move_flips = board.make_random_move()
        else:
            move_square, move_flips = board.make_maxflips_move()
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

print(f"After {games} games:")
print(f"White wins: {white_wins}")
print(f"Black wins: {black_wins}")
print(f"Ties: {ties}")
print(f"Average White count: {sum(white_counts)/games:.2f}")
print(f"Average Black count: {sum(black_counts)/games:.2f}")
# print(f"Max White count: {max(white_counts)}")
# print(f"Max Black count: {max(black_counts)}")
# print(f"Min White count: {min(white_counts)}")
# print(f"Min Black count: {min(black_counts)}")
