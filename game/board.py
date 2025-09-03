"""
board.py

Defines the Board class for the game.
"""

from .square import Square

class Board:
    """
    Represents the game board.
    """
    def __init__(self):
        """
        Initialize the board with the given size (default 8x8).
        All squares are set to Square.OPEN.
        """
        self.size = 8
        self.grid = [[Square.OPEN for _ in range(8)] for _ in range(8)]
        self.current_turn = Square.WHITE
        self.grid[3][3] = Square.WHITE
        self.grid[3][4] = Square.BLACK
        self.grid[4][3] = Square.BLACK
        self.grid[4][4] = Square.WHITE



    def __str__(self):
        return '\n'.join(' '.join(square.name[0] for square in row) for row in self.grid)
