# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the web app:**
```bash
python web/app.py
```

**Run the CLI:**
```bash
python play.py
```

**Run tests:**
```bash
python test_board.py   # Single game: smart vs maxflips, tests JSON serialization
python test_stats.py   # Tournament: 5000-game comparison of all 3 AI strategies
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

## Architecture

BlacknWhite is an Othello/Reversi game with three interfaces sharing a common core:

**`game/` — Core library**
- `square.py`: `Square` enum with values `OPEN`, `BLACK`, `WHITE`
- `board.py`: `Board` class — all game state, move logic, AI strategies, and JSON serialization
  - `open_moves()` → `dict[tuple, list]` of valid moves and flipped squares
  - `make_move(row, col)` → applies a move and updates state
  - `make_random_move()`, `make_maxflips_move()`, `make_smart_move()` — three AI levels
  - `to_json()` / `from_json()` / `to_dict()` / `from_dict()` — state serialization

**`web/` — Flask web application**
- `app.py`: REST API endpoints (`/api/board`, `/api/move`, `/api/pass`, `/api/reset`, `/api/ai_move`) with session-based board storage
- `static/game.js`: Fetch-based frontend that syncs board state and drives the game loop
- `templates/index.html` + `static/style.css`: Responsive SVG board UI (CSS Grid, viewport-relative sizing)

**`play.py`** — CLI adapter translating user input to `Board` API calls

## Code Conventions

- Follow PEP8; add docstrings to all classes and public methods
- Use existing `Board` and `Square` classes — avoid duplicating logic already in `game/`
- No formal test framework; test scripts are standalone Python files in the project root
- `PYTHONPATH` must include the project root so `import game` resolves (set automatically in the dev container)
