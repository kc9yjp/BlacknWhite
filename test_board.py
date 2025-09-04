"""
test_board.py

Test script to create a game board and print it.
"""

from game import Board

if __name__ == "__main__":
    board = Board()
    print(board)

    for s in board.open_squares():
        print(s)

    moves = board.open_moves()
    print(f"\nAvailable moves for {moves['color'].name}:")
    for square in moves['moves'].keys():
        print(f"Square: {square}:")
        for flips in moves['moves'][square]:
            print(f"   Flips: {flips}")

