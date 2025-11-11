"""The ``game`` package for the BlacknWhite project.

This package exposes the core game types used across the project:

- ``Square``: an enum describing the state of a single board cell.
- ``Board``: the game board implementation, move generation, and
	simple opponent strategies.

Import these from the package root for convenience::

		from game import Board, Square

"""

from .square import Square
from .board import Board

__all__ = [
		"Square",
		"Board",
]
