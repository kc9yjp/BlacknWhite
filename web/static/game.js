
/** The human player's color ('BLACK' or 'WHITE'), or null before a game is started. */
let playerColor = null;

/** Last-fetched game state, used to avoid redundant server round-trips. */
let currentState = null;

/** Prevents overlapping API requests from concurrent clicks or AI calls. */
let isRequestPending = false;

const VALID_SQUARE_VALUES = new Set(['OPEN', 'BLACK', 'WHITE']);

/**
 * Display an error message in the status bar, auto-clearing after 3 seconds.
 * @param {string} msg - The error text to show.
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
 * @param {string[][]} grid - 8×8 array of 'BLACK', 'WHITE', or 'OPEN'.
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
 * @param {Object} board - The board object from the server response.
 * @returns {boolean}
 */
function isGameOver(board) {
    if (board.consecutive_passes >= 2) return true;
    return board.grid.every(row => row.every(cell => cell !== 'OPEN'));
}

/**
 * Re-render all board squares and update the status line from a server response.
 * Marks valid move squares with the VALID CSS class so players can see their options.
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
    const score = `White: ${white}  Black: ${black}`;
    if (gameOver) {
        const winner = white > black ? 'White wins!' : black > white ? 'Black wins!' : "It's a tie!";
        setStatus(`Game over — ${score} — ${winner}`);
    } else if (!playerColor) {
        setStatus(score);
    } else if (board.current_turn === playerColor) {
        const colorLabel = playerColor.charAt(0) + playerColor.slice(1).toLowerCase();
        setStatus(`Your turn (${colorLabel}) — ${score}`);
    } else {
        setStatus(`AI is thinking\u2026 — ${score}`);
    }
}

/**
 * Handle a player clicking on a board square.
 * Uses the cached currentState to avoid an extra server round-trip.
 * @param {number} r - Row index (0-based).
 * @param {number} c - Column index (0-based).
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

/** Pass the player's turn and refresh the board. */
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

/** Reset the game, clear player state, and return to the start screen. */
document.getElementById('resetBtn').onclick = async () => {
    try {
        playerColor = null;
        currentState = null;
        await fetch('/api/reset', { method: 'POST' });
        showControls(false);
        await update();
    } catch (e) {
        showError('Network error');
    }
};

/**
 * Toggle between the start screen and the in-game controls.
 * @param {boolean} show - True to show game controls, false to show the start area.
 */
function showControls(show) {
    document.getElementById('game-controls').style.display = show ? '' : 'none';
    document.getElementById('start-area').style.display = show ? 'none' : '';
}

/**
 * Ask the server to make one AI opponent move, then refresh the board.
 * Called automatically by update() when it detects it is the opponent's turn.
 */
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

/**
 * Fetch the latest game state, render it, and trigger an AI move if it is
 * the opponent's turn and the game is still in progress.
 */
async function update() {
    const data = await fetchState();
    currentState = data;
    renderBoard(data);
    if (playerColor && !isGameOver(data.board) && data.board.current_turn !== playerColor) {
        setTimeout(aiMove, 700);
    }
}

/** Start a new game as Black with the selected strategy. */
document.getElementById('startBlackBtn').onclick = async () => {
    try {
        const strategy = document.getElementById('strategySelect').value;
        const res = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ color: 'BLACK', strategy })
        });
        if (!res.ok) throw new Error('Start failed');
        playerColor = 'BLACK';
        document.getElementById('start-msg').textContent = 'You are playing as Black.';
        showControls(true);
        await update();
    } catch (e) {
        showError('Network error');
    }
};

/** Start a new game as White with the selected strategy. */
document.getElementById('startWhiteBtn').onclick = async () => {
    try {
        const strategy = document.getElementById('strategySelect').value;
        const res = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ color: 'WHITE', strategy })
        });
        if (!res.ok) throw new Error('Start failed');
        playerColor = 'WHITE';
        document.getElementById('start-msg').textContent = 'You are playing as White.';
        showControls(true);
        await update();
    } catch (e) {
        showError('Network error');
    }
};

// run initial update so board shows on page load
update();
