"""Square enum used by the BlacknWhite game.

This module defines the :class:`Square` enum which represents the state
of a single board cell. Values are:

- ``OPEN``: the square is empty
- ``BLACK``: occupied by a black piece
- ``WHITE``: occupied by a white piece

The enum is used by :mod:`game.board` to populate and query the grid.
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
