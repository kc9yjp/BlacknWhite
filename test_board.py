"""
test_board.py

Test script to create a game board and print it.
"""

from game import Board
from game import Square

if __name__ == "__main__":
    board = Board()
    print(str(board).replace('O', ' '))


    while not board.game_over():
        turn = board.open_moves()
        print(f"\nAvailable moves for {turn['color'].name}:")
        for square in turn['moves'].keys():
            print(f"Square {square} flips {turn['moves'][square]} pieces")

        if board.current_turn == Square.BLACK:
            move_square, move_flips = board.make_smart_move()
        else:
            move_square, move_flips = board.make_maxflips_move()
        if move_square is None:
            print(f"{turn['color'].name} has no moves and must pass.")
        else:
            print(f"Making move at {move_square} flipping {move_flips} pieces")

        print(str(board).replace('O', ' '))


    white_count = board.count(Square.WHITE)
    black_count = board.count(Square.BLACK)
    open_count = board.open_count()
    print(f"White: {white_count}, Black: {black_count}, Open: {open_count}")
    if white_count == black_count:
        print("The game is a tie!")
    elif white_count > black_count:
        print("White is the winner!")
    else:
        print("Black is the winner!")