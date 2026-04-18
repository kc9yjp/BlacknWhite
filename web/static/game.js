
/** The human player's color ('BLACK' or 'WHITE'), or null before a game is started. */
let playerColor = null;

/** The AI strategy chosen at game start ('random', 'maxflips', 'smart'). */
let currentStrategy = null;

/** Last-fetched game state, used to avoid redundant server round-trips. */
let currentState = null;

/** Prevents overlapping API requests from concurrent clicks or AI calls. */
let isRequestPending = false;

const VALID_SQUARE_VALUES = new Set(['OPEN', 'BLACK', 'WHITE']);

const STRATEGY_NAMES = { random: 'Random', maxflips: 'Max Flips', smart: 'Smart' };

/**
 * Display an error message in the status bar, auto-clearing after 3 seconds.
 * @param {string} msg
 */
function showError(msg) {
    const el = document.getElementById('status');
    el.textContent = 'Error: ' + msg;
    el.classList.add('error');
    setTimeout(() => el.classList.remove('error'), 3000);
}

function setStatus(msg) {
    const el = document.getElementById('status');
    el.textContent = msg;
    el.classList.remove('error');
}

/**
 * Fetch the current game state from the server.
 * @returns {Promise<Object>} Parsed JSON with shape { board, strategy, color, valid_moves }.
 */
async function fetchState() {
    const res = await fetch('/api/board');
    return await res.json();
}

/**
 * Count the number of BLACK and WHITE pieces on the board grid.
 * @param {string[][]} grid
 * @returns {{ white: number, black: number }}
 */
function countPieces(grid) {
    let white = 0, black = 0;
    for (const row of grid) {
        for (const cell of row) {
            if (cell === 'WHITE') white++;
            else if (cell === 'BLACK') black++;
        }
    }
    return { white, black };
}

/**
 * Determine whether the game has ended.
 * @param {Object} board
 * @returns {boolean}
 */
function isGameOver(board) {
    if (board.consecutive_passes >= 2) return true;
    return board.grid.every(row => row.every(cell => cell !== 'OPEN'));
}

/**
 * Re-render all board squares, update the status line, and show/hide
 * the game-over panel based on the server response.
 * @param {Object} data - Full game state as returned by any API endpoint.
 */
function renderBoard(data) {
    const board = data.board;
    const validSet = new Set((data.valid_moves || []).map(([r, c]) => `${r},${c}`));
    const boardDiv = document.getElementById('board');
    boardDiv.querySelectorAll('.square').forEach(cell => {
        const r = parseInt(cell.dataset.row, 10);
        const c = parseInt(cell.dataset.col, 10);
        const val = VALID_SQUARE_VALUES.has(board.grid[r][c]) ? board.grid[r][c] : 'OPEN';
        cell.className = 'square ' + val;
        if (validSet.has(`${r},${c}`)) cell.classList.add('VALID');
        cell.innerHTML = '';
        if (val === 'BLACK' || val === 'WHITE') {
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('class', 'piece ' + (val === 'BLACK' ? 'black' : 'white'));
            const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
            use.setAttributeNS('http://www.w3.org/1999/xlink', 'href', '#disk');
            svg.appendChild(use);
            cell.appendChild(svg);
        }
        cell.onclick = () => makeMove(r, c);
    });

    const { white, black } = countPieces(board.grid);
    const gameOver = isGameOver(board);

    if (gameOver && playerColor) {
        showGameOver(black, white);
    } else {
        document.getElementById('play-controls').style.display = '';
        document.getElementById('game-over-area').style.display = 'none';
        if (board.current_turn === playerColor) {
            setStatus(`Your turn — Black: ${black}  White: ${white}`);
        } else if (playerColor) {
            setStatus(`AI is thinking\u2026 — Black: ${black}  White: ${white}`);
        } else {
            setStatus(`Black: ${black}  White: ${white}`);
        }
    }
}

/**
 * Display the game-over panel with final scores and outcome.
 * @param {number} black
 * @param {number} white
 */
function showGameOver(black, white) {
    document.getElementById('play-controls').style.display = 'none';
    document.getElementById('game-over-area').style.display = '';

    let headline, detail;
    if (black === white) {
        headline = "It's a tie!";
        detail = `Final score: Black ${black} \u2013 White ${white}`;
    } else {
        const winColor = black > white ? 'Black' : 'White';
        const winScore = black > white ? black : white;
        const loseScore = black > white ? white : black;
        const margin = winScore - loseScore;
        const youWon = (winColor === playerColor.charAt(0) + playerColor.slice(1).toLowerCase());
        headline = `${winColor} wins${youWon ? ' \u2014 you won!' : ' \u2014 you lost.'}`;
        detail = `Final score: Black ${black} \u2013 White ${white} (${winColor} leads by ${margin})`;
    }

    document.getElementById('game-over-result').textContent = headline;
    document.getElementById('game-over-score').textContent = detail + '  Want to play again?';
}

/**
 * Handle a player clicking on a board square.
 * Uses the cached currentState to avoid an extra server round-trip.
 */
async function makeMove(r, c) {
    if (!playerColor || isRequestPending) return;
    if (!currentState || currentState.board.current_turn !== playerColor) return;

    isRequestPending = true;
    try {
        const res = await fetch('/api/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ row: r, col: c })
        });
        if (res.ok) {
            await update();
        } else {
            const body = await res.json().catch(() => ({}));
            showError(body.error || 'Invalid move');
        }
    } catch (e) {
        showError('Network error');
    } finally {
        isRequestPending = false;
    }
}

document.getElementById('passBtn').onclick = async () => {
    if (isRequestPending) return;
    isRequestPending = true;
    try {
        const res = await fetch('/api/pass', { method: 'POST' });
        if (!res.ok) {
            const body = await res.json().catch(() => ({}));
            showError(body.error || 'Cannot pass');
        }
        await update();
    } catch (e) {
        showError('Network error');
    } finally {
        isRequestPending = false;
    }
};

/** Return to the start screen without restarting automatically. */
function goToStartScreen() {
    playerColor = null;
    currentStrategy = null;
    currentState = null;
    document.getElementById('game-controls').style.display = 'none';
    document.getElementById('start-area').style.display = '';
}

document.getElementById('resetBtn').onclick = async () => {
    try {
        await fetch('/api/reset', { method: 'POST' });
        goToStartScreen();
        await update();
    } catch (e) {
        showError('Network error');
    }
};

document.getElementById('newGameBtn').onclick = async () => {
    try {
        await fetch('/api/reset', { method: 'POST' });
        goToStartScreen();
        await update();
    } catch (e) {
        showError('Network error');
    }
};

document.getElementById('playAgainBtn').onclick = async () => {
    if (!playerColor || !currentStrategy) return;
    try {
        await startGame(playerColor, currentStrategy);
    } catch (e) {
        showError('Network error');
    }
};

/**
 * Toggle between the start screen and the in-game controls.
 * @param {boolean} show
 */
function showControls(show) {
    document.getElementById('game-controls').style.display = show ? '' : 'none';
    document.getElementById('start-area').style.display = show ? 'none' : '';
}

/**
 * Populate the persistent "game-info" label with the current player/strategy.
 */
function updateGameInfo() {
    const colorLabel = playerColor === 'BLACK' ? 'Black' : 'White';
    const oppLabel = playerColor === 'BLACK' ? 'White' : 'Black';
    const stratLabel = STRATEGY_NAMES[currentStrategy] || currentStrategy;
    document.getElementById('game-info').textContent =
        `You: ${colorLabel}  \u00b7  Opponent (${stratLabel}): ${oppLabel}`;
}

/**
 * Start or restart a game with the given color and strategy.
 * @param {string} color - 'BLACK' or 'WHITE'
 * @param {string} strategy
 */
async function startGame(color, strategy) {
    const res = await fetch('/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ color, strategy })
    });
    if (!res.ok) throw new Error('Start failed');
    playerColor = color;
    currentStrategy = strategy;
    updateGameInfo();
    // reset to play-controls view in case we're coming from game-over
    document.getElementById('play-controls').style.display = '';
    document.getElementById('game-over-area').style.display = 'none';
    showControls(true);
    await update();
}

async function aiMove() {
    if (isRequestPending) return;
    isRequestPending = true;
    try {
        await fetch('/api/opponentmove', { method: 'POST' });
    } catch (e) {
        showError('Network error');
    } finally {
        isRequestPending = false;
    }
    await update();
}

async function update() {
    const data = await fetchState();
    currentState = data;
    renderBoard(data);
    if (playerColor && !isGameOver(data.board) && data.board.current_turn !== playerColor) {
        setTimeout(aiMove, 700);
    }
}

document.getElementById('startBlackBtn').onclick = async () => {
    try {
        const strategy = document.getElementById('strategySelect').value;
        await startGame('BLACK', strategy);
    } catch (e) {
        showError('Network error');
    }
};

document.getElementById('startWhiteBtn').onclick = async () => {
    try {
        const strategy = document.getElementById('strategySelect').value;
        await startGame('WHITE', strategy);
    } catch (e) {
        showError('Network error');
    }
};

// run initial update so board shows on page load
update();
