
/** The human player's color ('BLACK' or 'WHITE'), or null before a game is started. */
let playerColor = null;

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

/**
 * Fetch the current game state from the server.
 * @returns {Promise<Object>} Parsed JSON with shape { board, strategy, color }.
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
 * The game is over when two consecutive passes have occurred or no open squares remain.
 * @param {Object} board - The board object from the server response.
 * @returns {boolean}
 */
function isGameOver(board) {
    if (board.consecutive_passes >= 2) return true;
    return board.grid.every(row => row.every(cell => cell !== 'OPEN'));
}

/**
 * Re-render all board squares and update the status line from a server response.
 * Updates CSS classes and piece SVGs in place without rebuilding the DOM.
 * @param {Object} data - Full game state as returned by any API endpoint.
 */
function renderBoard(data) {
    const board = data.board;
    const boardDiv = document.getElementById('board');
    // update each pre-defined square rather than recreating the DOM
    boardDiv.querySelectorAll('.square').forEach(cell => {
        const r = parseInt(cell.dataset.row, 10);
        const c = parseInt(cell.dataset.col, 10);
        const val = VALID_SQUARE_VALUES.has(board.grid[r][c]) ? board.grid[r][c] : 'OPEN';
        // reset classes
        cell.className = 'square ' + val;
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
    // update status line
    const { white, black } = countPieces(board.grid);
    const gameOver = isGameOver(board);
    let statusText = `Turn: ${board.current_turn} | White: ${white}  Black: ${black}`;
    if (gameOver) {
        const winner = white > black ? 'White wins!' : black > white ? 'Black wins!' : 'Tie!';
        statusText += ' | Game Over! ' + winner;
    }
    document.getElementById('status').textContent = statusText;
}

/**
 * Handle a player clicking on a board square.
 * Silently ignores the click if it is not the player's turn.
 * @param {number} r - Row index (0-based).
 * @param {number} c - Column index (0-based).
 */
async function makeMove(r, c) {
    if (!playerColor) {
        showError('Please start a game first.');
        return;
    }
    try {
        // only allow clicking when it's player's turn
        const data = await fetchState();
        if (data.board.current_turn !== playerColor) {
            return; // ignore click
        }
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
    }
}

/** Pass the player's turn and refresh the board. */
document.getElementById('passBtn').onclick = async () => {
    try {
        await fetch('/api/pass', { method: 'POST' });
        await update();
    } catch (e) {
        showError('Network error');
    }
};

/** Reset the game, clear player state, and return to the start screen. */
document.getElementById('resetBtn').onclick = async () => {
    try {
        playerColor = null;
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
    await fetch('/api/opponentmove', { method: 'POST' });
    await update();
}

/**
 * Fetch the latest game state, render it, and trigger an AI move if it is
 * the opponent's turn and the game is still in progress.
 */
async function update() {
    const data = await fetchState();
    renderBoard(data);
    // if game running and it's opponent's turn, trigger AI move
    if (playerColor && !isGameOver(data.board) && data.board.current_turn !== playerColor) {
        // small delay to let UI update
        setTimeout(aiMove, 1000);
    }
}

// start button logic
/** Start a new game as Black with the selected strategy. */
document.getElementById('startBlackBtn').onclick = async () => {
    try {
        const strategy = document.getElementById('strategySelect').value;
        playerColor = 'BLACK';
        await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ color: 'BLACK', strategy })
        });
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
        playerColor = 'WHITE';
        await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ color: 'WHITE', strategy })
        });
        document.getElementById('start-msg').textContent = 'You are playing as White.';
        showControls(true);
        await update();
    } catch (e) {
        showError('Network error');
    }
};

// run initial update so board shows on page load
update();
