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
        self.grid = [[Square.OPEN for _ in range(self.size)] for _ in range(self.size)]
        self.current_turn = Square.WHITE
        self.grid[3][3] = Square.WHITE
        self.grid[3][4] = Square.BLACK
        self.grid[4][3] = Square.BLACK
        self.grid[4][4] = Square.WHITE

    def north_coords(self, pos):
        row, col = pos
        results = []
        while row > 0:
            row -= 1
            results.append((row, col))

        return results
    
    def south_coords(self, pos):
        row, col = pos
        results = []
        while row < self.size - 1:
            row += 1
            results.append((row, col))
        return results

    def east_coords(self, pos):
        row, col = pos
        results = []
        while col < self.size - 1:
            col += 1
            results.append((row, col))
        return results
    
    def west_coords(self, pos):
        row, col = pos
        results = []
        while col > 0:
            col -= 1
            results.append((row, col))
        return results
    
    def northeast_coords(self, pos):
        row, col = pos
        results = []
        while row > 0 and col < self.size - 1:
            row -= 1
            col += 1
            results.append((row, col))
        return results
    
    def northwest_coords(self, pos):
        row, col = pos
        results = []
        while row > 0 and col > 0:
            row -= 1
            col -= 1
            results.append((row, col))
        return results
    
    def southeast_coords(self, pos):
        row, col = pos
        results = []
        while row < self.size - 1 and col < self.size - 1:
            row += 1
            col += 1
            results.append((row, col))
        return results
    
    def southwest_coords(self, pos):
        row, col = pos
        results = []
        while row < self.size - 1 and col > 0:
            row += 1
            col -= 1
            results.append((row, col))
        return results
    
    def open_squares(self):
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.grid[r][c] == Square.OPEN]
    
    def __str__(self):
        return '\n'.join(' '.join(square.name[0] for square in row) for row in self.grid)

    def open_count(self):
        count = 0
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == Square.OPEN:
                    count += 1
        return count
    
    def count(self, square_type):
        count = 0
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == square_type:
                    count += 1
        return count