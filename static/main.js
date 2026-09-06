const SIZE = 9;

const LEADERBOARD_KEY = "sudoku-leaderboard";
const THEME_KEY = "sudoku-theme";

let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let completedGame = false;

function updateTimerDisplay() {
    const min = String(Math.floor(elapsedSeconds / 60)).padStart(2, "0");
    const sec = String(elapsedSeconds % 60).padStart(2, "0");

    document.getElementById("timer").innerText =
        `Time: ${min}:${sec}`;
}

function startTimer() {
    stopTimer();

    timerInterval = setInterval(() => {
        elapsedSeconds++;
        updateTimerDisplay();
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function resetTimer() {
    stopTimer();
    elapsedSeconds = 0;
    updateTimerDisplay();
}

function getLeaderboard() {
    return JSON.parse(
        localStorage.getItem(LEADERBOARD_KEY) || "[]"
    );
}

function saveLeaderboard(board) {
    localStorage.setItem(
        LEADERBOARD_KEY,
        JSON.stringify(board)
    );
}

function renderLeaderboard() {
    const tbody = document.getElementById("leaderboard-body");
    tbody.innerHTML = "";
    const board = getLeaderboard();
    
    if (board.length === 0) {
        tbody.innerHTML =
            `<tr><td colspan="5">No scores yet</td></tr>`;
        return;
    }
    
    board.forEach((item, index) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${item.name}</td>
            <td>${item.time}</td>
            <td>${item.difficulty}</td>
            <td>${item.hints}</td>
        `;

        tbody.appendChild(row);
    });
}

function addScore(name, time, difficulty, hints) {
    let board = getLeaderboard();

    board.push({
        name,
        time,
        difficulty,
        hints
    });

    board.sort((a, b) => {
        const [am, as] = a.time.split(":").map(Number);
        const [bm, bs] = b.time.split(":").map(Number);

        return (am * 60 + as) - (bm * 60 + bs);
    });

    board = board.slice(0, 10);

    saveLeaderboard(board);

    renderLeaderboard();
}

function applyTheme(theme) {
    document.body.classList.toggle(
        "dark-mode",
        theme === "dark"
    );

    document.getElementById("theme-toggle").innerText =
        theme === "dark"
            ? "Light Mode"
            : "Dark Mode";
}

function toggleTheme() {
    const next =
        document.body.classList.contains("dark-mode")
            ? "light"
            : "dark";

    localStorage.setItem(THEME_KEY, next);

    applyTheme(next);
}

function createBoard() {
    const board =
        document.getElementById("sudoku-board");

    board.innerHTML = "";

    for (let r = 0; r < SIZE; r++) {
        const row = document.createElement("div");

        row.className = "sudoku-row";

        for (let c = 0; c < SIZE; c++) {
            const input = document.createElement("input");

            input.type = "text";

            input.maxLength = 1;

            input.className = "sudoku-cell";

            input.dataset.row = r;

            input.dataset.col = c;

            const boxColor =
                ((Math.floor(r / 3) + Math.floor(c / 3)) % 2 === 0)
                    ? "box-light"
                    : "box-dark";

            input.classList.add(boxColor);

            row.appendChild(input);
        }

        board.appendChild(row);
    }
}

function renderPuzzle(data) {
    puzzle = data;

    createBoard();

    const cells =
        document.querySelectorAll(".sudoku-cell");

    for (let r = 0; r < SIZE; r++) {
        for (let c = 0; c < SIZE; c++) {
            const index = r * SIZE + c;
            const input = cells[index];

            if (data[r][c] !== 0) {
                input.value = data[r][c];
                input.disabled = true;
                input.classList.add("prefilled");
            } else {
                input.disabled = false;

                input.addEventListener("input", async () => {
                    input.classList.remove("incorrect");

                    if (input.value === "") {
                        return;
                    }

                    try {
                        const response = await fetch("/validate", {
                            method: "POST",

                            headers: {
                                "Content-Type": "application/json"
                            },

                            body: JSON.stringify({
                                row: r,
                                col: c,
                                value: parseInt(input.value)
                            })
                        });

                        const result = await response.json();

                        if (!result.valid) {
                            input.classList.add("incorrect");
                        }
                    } catch (err) {
                        console.error(err);
                    }
                });
            }
        }
    }
}

async function newGame() {
    resetTimer();

    hintsUsed = 0;

    completedGame = false;

    const difficulty =
        document.getElementById("difficulty-select").value;

    try {
        const response = await fetch(
            `/new?difficulty=${encodeURIComponent(difficulty)}`
        );

        if (!response.ok) {
            throw new Error("Unable to create new puzzle");
        }

        const data = await response.json();

        renderPuzzle(data.puzzle);

        document.getElementById("message").style.color =
            "green";

        document.getElementById("message").innerText = "";

        startTimer();
    } catch (err) {
        console.error(err);

        document.getElementById("message").style.color =
            "red";

        document.getElementById("message").innerText =
            "Unable to load puzzle.";
    }
}

async function checkSolution() {
    const cells =
        document.querySelectorAll(".sudoku-cell");

    const board = [];

    for (let r = 0; r < SIZE; r++) {
        board[r] = [];

        for (let c = 0; c < SIZE; c++) {
            const index = r * SIZE + c;

            board[r][c] =
                cells[index].value === ""
                    ? 0
                    : parseInt(cells[index].value);
        }
    }

    try {
        const response = await fetch("/check", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                board: board
            })
        });

        if (!response.ok) {
            throw new Error("Check failed");
        }

        const result = await response.json();

        cells.forEach(cell => {
            cell.classList.remove("incorrect");
        });

        if (result.error) {
            document.getElementById("message").innerText =
                result.error;

            return;
        }

        result.incorrect.forEach(item => {
            const index =
                item[0] * SIZE + item[1];

            if (!cells[index].disabled) {
                cells[index].classList.add("incorrect");
            }
        });

        result.missing.forEach(item => {
            const index =
                item[0] * SIZE + item[1];

            if (!cells[index].disabled) {
                cells[index].classList.add("incorrect");
            }
        });

        if (result.solved) {
            stopTimer();

            completedGame = true;

            const finalTime =
                document.getElementById("timer")
                    .innerText
                    .replace("Time: ", "");

            document.getElementById("message").style.color =
                "green";

            document.getElementById("message").innerText =
                `🎉 Congratulations! You solved the Sudoku in ${finalTime}`;

            // Automatically save the completed game to the leaderboard --
            // don't rely on the player noticing a separate button.
            const difficulty =
                document.getElementById("difficulty-select").value;

            let playerName = window.prompt(
                "Enter your name for the Top 10 leaderboard:",
                ""
            );

            playerName = (playerName || "").trim() || "Anonymous";

            addScore(playerName, finalTime, difficulty, hintsUsed);

            document.getElementById("message").innerText +=
                " Your score has been added to the leaderboard!";
        } else if (result.incorrect.length > 0 || result.missing.length > 0) {
            document.getElementById("message").style.color =
                "red";

            document.getElementById("message").innerText =
                "Some cells are incorrect or still empty -- check the highlighted cells.";
        } else {
            document.getElementById("message").style.color =
                "red";

            document.getElementById("message").innerText =
                "Keep going -- no conflicts yet, but the puzzle isn't finished.";
        }
    } catch (err) {
        console.error(err);

        document.getElementById("message").style.color =
            "red";

        document.getElementById("message").innerText =
            "Unable to validate the puzzle.";
    }
}

async function showHint() {
    try {
        const cells =
            document.querySelectorAll(".sudoku-cell");

        const target = [...cells].find(
            cell => !cell.disabled && cell.value === ""
        );

        if (!target) {
            document.getElementById("message").style.color = "red";

            document.getElementById("message").innerText =
                "No empty cells remain.";

            return;
        }

        const row = target.dataset.row;
        const col = target.dataset.col;

        const response = await fetch(
            `/hint?row=${encodeURIComponent(row)}&col=${encodeURIComponent(col)}`
        );

        if (!response.ok) {
            throw new Error("Unable to get hint");
        }

        const result = await response.json();

        if (result.error) {
            document.getElementById("message").style.color = "red";

            document.getElementById("message").innerText =
                result.error;

            return;
        }

        const index =
            result.row * SIZE + result.col;

        cells[index].value = result.value;

        cells[index].disabled = true;

        cells[index].classList.add("prefilled");

        cells[index].classList.remove("incorrect");

        hintsUsed++;

        document.getElementById("message").style.color =
            "green";

        document.getElementById("message").innerText =
            "Hint revealed!";
    } catch (err) {
        console.error(err);

        document.getElementById("message").style.color =
            "red";

        document.getElementById("message").innerText =
            "Unable to retrieve hint.";
    }
}

function saveScore() {
    const player =
        document.getElementById("player-name").value.trim() ||
        "Anonymous";

    const difficulty =
        document.getElementById("difficulty-select").value;

    const time =
        document.getElementById("timer")
            .innerText
            .replace("Time: ", "");

    addScore(
        player,
        time,
        difficulty,
        hintsUsed
    );

    document.getElementById("player-name").value = "";

    document.getElementById("message").style.color = "green";

    document.getElementById("message").innerText =
        "Score saved successfully.";
}

window.addEventListener("load", () => {
    const savedTheme =
        localStorage.getItem(THEME_KEY) || "light";

    applyTheme(savedTheme);

    renderLeaderboard();

    document
        .getElementById("new-game")
        .addEventListener("click", newGame);

    document
        .getElementById("check-solution")
        .addEventListener("click", checkSolution);

    document
        .getElementById("hint")
        .addEventListener("click", showHint);

    document
        .getElementById("save-score")
        .addEventListener("click", saveScore);

    document
        .getElementById("theme-toggle")
        .addEventListener("click", toggleTheme);

    newGame();
});

window.addEventListener("beforeunload", () => {
    stopTimer();
});