async function fetchBoard() {
    const res = await fetch('/api/board');
    return await res.json();
}

function renderBoard(data) {
    const boardDiv = document.getElementById('board');
    boardDiv.innerHTML = '';
    data.grid.forEach((row, r) => {
        row.forEach((sq, c) => {
            const d = document.createElement('div');
            d.className = 'square ' + sq;
            d.textContent = sq === 'BLACK' ? '●' : sq === 'WHITE' ? '○' : '';
            d.onclick = () => makeMove(r, c);
            boardDiv.appendChild(d);
        });
    });
    document.getElementById('info').textContent = `Turn: ${data.current_turn} | White: ${data.white_count} Black: ${data.black_count}`;
    if (data.game_over) {
        document.getElementById('info').textContent += ' | Game Over!';
    }
}

async function makeMove(r, c) {
    const res = await fetch('/api/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row: r, col: c })
    });
    if (res.ok) {
        update();
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

async function update() {
    const data = await fetchBoard();
    renderBoard(data);
}

update();
