"""
test_board.py

Test script to create a game board and print it.
"""

from game import Board

if __name__ == "__main__":
    board = Board()
    print(board)

    for s in board.empty_squares():
        print(s)
