"""
board.py

Defines the Board class for the game.
"""
import random
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
        self.pass_count = 0
        self.consecutive_passes = 0


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

    def pass_turn(self):
        if self.game_over():
            raise Exception("Game is over, cannot pass turn.")
        self.pass_count += 1
        self.consecutive_passes += 1
        self.current_turn = Square.BLACK if self.current_turn == Square.WHITE else Square.WHITE

    def game_over(self):
        return self.consecutive_passes >= 2 or self.open_count() == 0

    def open_moves(self):
        if self.game_over():
            raise Exception("Game is over, cannot make a move.")
        results = {"color": self.current_turn, "moves": {}}

        for sq in self.open_squares():
            paths = [self.north_coords(sq), self.south_coords(sq), self.east_coords(sq), self.west_coords(sq),
                          self.northeast_coords(sq), self.northwest_coords(sq), self.southeast_coords(sq),
                          self.southwest_coords(sq)]
            # foreach path, get the valid moves
            flip_list = []
            for path in paths:
                flips = self.get_flips(path)
                if flips:
                    flip_list.extend(flips)
            if flip_list:
                results["moves"][sq] = flip_list

        return results
    
    def get_flips(self, square_list):
        if not square_list or len(square_list) < 1:
            return []
        moves = []
        anchor = False
        for  pos in square_list:
            sq = self.grid[pos[0]][pos[1]]

            if sq == Square.OPEN:
                break
            elif sq == self.current_turn:
                anchor = True
                break
            else:
                moves.append(pos)

        if anchor and moves:
            return moves
        return []
    
    def make_move(self, pos, flips):
        if self.game_over():
            raise Exception("Game is over, cannot make a move.")
        if not flips:
            raise ValueError("No pieces to flip for this move.")
        self.grid[pos[0]][pos[1]] = self.current_turn
        for flip in flips:
            self.grid[flip[0]][flip[1]] = self.current_turn
        self.current_turn = Square.BLACK if self.current_turn == Square.WHITE else Square.WHITE
        self.consecutive_passes = 0

    def make_random_move(self):
        moves = self.open_moves()
        if not moves["moves"]:
            self.pass_turn()
            return None, None
        move_square = random.choice(list(moves['moves'].keys()))
        move_flips = moves['moves'][move_square]    
        self.make_move(move_square, move_flips)
        return move_square, move_flips