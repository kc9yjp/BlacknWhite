let playerColor = null; // 'BLACK' or 'WHITE' once user selects

async function fetchBoard() {
    const res = await fetch('/api/board');
    return await res.json();
}

function renderBoard(data) {
    const boardDiv = document.getElementById('board');
    // update each pre-defined square rather than recreating the DOM
    boardDiv.querySelectorAll('.square').forEach(cell => {
        const r = parseInt(cell.dataset.row, 10);
        const c = parseInt(cell.dataset.col, 10);
        const val = data.grid[r][c];
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
    // update status line rather than overwrite entire info container
    let statusText = `Turn: ${data.current_turn} | White: ${data.white_count} Black: ${data.black_count}`;
    if (data.game_over) {
        statusText += ' | Game Over!';
    }
    document.getElementById('status').textContent = statusText;
}

async function makeMove(r, c) {
    if (!playerColor) {
        alert('Please start a game first.');
        return;
    }
    // only allow clicking when it's player's turn
    const boardData = await fetchBoard();
    if (boardData.current_turn !== playerColor) {
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
        alert('Invalid move!');
    }
}

document.getElementById('passBtn').onclick = async () => {
    await fetch('/api/pass', { method: 'POST' });
    update();
};
document.getElementById('resetBtn').onclick = async () => {
    await fetch('/api/reset', { method: 'POST' });
    update();
};

function showControls(show) {
    document.querySelector('#info .controls').style.display = show ? '' : 'none';
    document.getElementById('start-area').style.display = show ? 'none' : '';
}

async function aiMove() {
    await fetch('/api/ai_move', { method: 'POST' });
    await update();
}

async function update() {
    const data = await fetchBoard();
    renderBoard(data);
    // if game running and it's opponent's turn, trigger AI move
    if (playerColor && !data.game_over && data.current_turn !== playerColor) {
        // small delay to let UI update
        setTimeout(aiMove, 200);
    }
}

// start button logic
const startBlackBtn = document.getElementById('startBlackBtn');
const startWhiteBtn = document.getElementById('startWhiteBtn');
startBlackBtn.onclick = () => {
    playerColor = 'BLACK';
    document.getElementById('start-msg').textContent = 'You are playing as Black.';
    showControls(true);
    update();
};
startWhiteBtn.onclick = () => {
    playerColor = 'WHITE';
    document.getElementById('start-msg').textContent = 'You are playing as White.';
    showControls(true);
    update();
};

// run initial update so board shows
update();
