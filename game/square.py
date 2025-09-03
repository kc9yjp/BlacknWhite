"""
square.py

Defines the Square enum representing the state of a square in the game.
"""

from enum import Enum

class Square(Enum):
    """
    Enum representing the state of a square in the game.
    OPEN: The square is empty.
    BLACK: The square is occupied by a black piece.
    WHITE: The square is occupied by a white piece.
    """
    OPEN = 0
    BLACK = 1
    WHITE = 2
