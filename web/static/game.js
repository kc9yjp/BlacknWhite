let playerColor = null; // 'BLACK' or 'WHITE' once user selects

async function fetchBoard() {
    const res = await fetch('/api/board');
    return await res.json();
}

function renderBoard(data) {
    const boardDiv = document.getElementById('board');
    const availableMoves = new Set(data.available_moves.map(move => `${move[0]},${move[1]}`));
    
    // update each pre-defined square rather than recreating the DOM
    boardDiv.querySelectorAll('.square').forEach(cell => {
        const r = parseInt(cell.dataset.row, 10);
        const c = parseInt(cell.dataset.col, 10);
        const val = data.grid[r][c];
        const moveKey = `${r},${c}`;
        const isAvailableMove = availableMoves.has(moveKey);
        
        // reset classes
        cell.className = 'square ' + val;
        if (isAvailableMove) {
            cell.classList.add('available');
        }
        
        cell.innerHTML = '';
        if (val === 'BLACK' || val === 'WHITE') {
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('class', 'piece ' + (val === 'BLACK' ? 'black' : 'white'));
            const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
            use.setAttributeNS('http://www.w3.org/1999/xlink', 'href', '#disk');
            svg.appendChild(use);
            cell.appendChild(svg);
            cell.onclick = null; // no click on occupied squares
        } else if (isAvailableMove && playerColor && !data.game_over && data.current_turn === playerColor) {
            cell.onclick = () => makeMove(r, c);
        } else {
            cell.onclick = null;
        }
    });
    
    // update status line
    let statusText = `Pieces - White: ${data.white_count} | Black: ${data.black_count}`;
    
    if (data.game_over) {
        if (data.winner === 'TIE') {
            statusText += ' | GAME OVER: Tie!';
        } else {
            statusText += ` | GAME OVER: ${data.winner} wins!`;
        }
    } else if (playerColor) {
        if (data.current_turn === playerColor) {
            statusText += ` | Your turn (${playerColor})`;
        } else {
            statusText += ` | Opponent's turn (${data.current_turn})`;
        }
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
    if (boardData.current_turn !== playerColor || boardData.game_over) {
        return; // ignore click
    }
    const res = await fetch('/api/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row: r, col: c })
    });
    if (res.ok) {
        document.getElementById('status').textContent = 'Move made! Checking game state...';
        await update();
        
        // Check if game is over after player's move
        const newData = await fetchBoard();
        if (newData.game_over) {
            // Game ended after player's move
            return;
        }
        
        // Trigger AI move with a small delay to simulate thinking
        document.getElementById('status').textContent = `${newData.current_turn} (AI - ${document.getElementById('strategySelect').value}) is thinking...`;
        setTimeout(aiMove, 1000);
    } else {
        alert('Invalid move!');
    }
}

document.getElementById('passBtn').onclick = async () => {
    const res = await fetch('/api/pass', { method: 'POST' });
    if (res.ok) {
        document.getElementById('status').textContent = 'You passed. Checking opponent options...';
        await update();
        
        // Check board state after pass
        const data = await fetchBoard();
        if (data.game_over) {
            // Game ended after pass
            return;
        }
        
        // If it's still opponent's turn (player has no moves), trigger AI move
        if (data.current_turn !== playerColor) {
            document.getElementById('status').textContent = `${data.current_turn} (AI) is thinking...`;
            setTimeout(aiMove, 1000);
        }
    }
};
document.getElementById('resetBtn').onclick = async () => {
    const strategy = document.getElementById('strategySelect').value;
    await fetch('/api/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy: strategy })
    });
    // Reset playerColor so user can select color again
    playerColor = null;
    document.getElementById('start-msg').textContent = 'Select black or white to begin play.';
    showControls(false);
    update();
};

function showControls(show) {
    document.querySelector('#info .controls').style.display = show ? '' : 'none';
    document.getElementById('start-area').style.display = show ? 'none' : '';
}

async function aiMove() {
    const res = await fetch('/api/ai_move', { method: 'POST' });
    if (res.ok) {
        await update();
        // After AI move, check if game is over or if player can move
        const data = await fetchBoard();
        if (data.game_over) {
            // Game ended after AI move
            return;
        }
        if (data.current_turn === playerColor) {
            document.getElementById('status').textContent = `AI made its move. Your turn (${playerColor})!`;
        }
    }
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

async function startGame(color) {
    playerColor = color;
    const strategy = document.getElementById('strategySelect').value;
    document.getElementById('start-msg').textContent = `Starting game with ${strategy} strategy...`;
    showControls(true);
    
    // Send strategy selection to backend
    await fetch('/api/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy: strategy })
    });
    
    await update();
    
    // If user selected WHITE, AI (BLACK) moves first
    if (playerColor === 'WHITE') {
        document.getElementById('status').textContent = `Playing as WHITE. ${strategy} AI (BLACK) is thinking...`;
        setTimeout(async () => {
            await aiMove();
            document.getElementById('status').textContent = `Playing as WHITE. AI made its move. Your turn!`;
        }, 500);
    } else {
        document.getElementById('status').textContent = `Playing as BLACK. Your turn! Make the first move.`;
    }
}

startBlackBtn.onclick = () => startGame('BLACK');
startWhiteBtn.onclick = () => startGame('WHITE');

// run initial update so board shows
update();
