import os

from flask import Flask, render_template, request, jsonify, session
import sudoku_logic

app = Flask(__name__)
app.secret_key = os.environ.get("SUDOKU_SECRET_KEY", "dev-secret-key-change-me")

DIFFICULTY_CLUES = {
    "easy": 40,
    "medium": 32,
    "hard": 26
}


def find_empty_cell(board):
    """Return first empty cell in the puzzle."""
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if board[row][col] == 0:
                return row, col
    return None, None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new")
def new_game():
    """Generate a new Sudoku puzzle."""

    difficulty = request.args.get("difficulty", "").lower()
    clues_param = request.args.get("clues")

    try:
        if clues_param:
            clues = int(clues_param)
        else:
            clues = DIFFICULTY_CLUES.get(difficulty, 35)
    except ValueError:
        clues = 35

    try:
        puzzle, solution = sudoku_logic.generate_puzzle(clues)

        session["puzzle"] = puzzle
        session["solution"] = solution

        return jsonify({
            "puzzle": puzzle
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/check", methods=["POST"])
def check_solution():
    """Check complete Sudoku board."""

    data = request.get_json(silent=True)

    if not data or "board" not in data:
        return jsonify({
            "error": "Invalid request"
        }), 400

    board = data["board"]

    solution = session.get("solution")

    if solution is None:
        return jsonify({
            "error": "No game in progress"
        }), 400

    incorrect = []
    missing = []

    for r in range(sudoku_logic.SIZE):
        for c in range(sudoku_logic.SIZE):

            value = board[r][c]

            if value == 0:
                # Still blank -- flag it too, so every missing or
                # wrong cell is visibly highlighted, not just wrong
                # ones.
                missing.append([r, c])
            elif value != solution[r][c]:
                incorrect.append([r, c])

    solved = all(
        board[r][c] == solution[r][c]
        for r in range(sudoku_logic.SIZE)
        for c in range(sudoku_logic.SIZE)
    )

    return jsonify({
        "incorrect": incorrect,
        "missing": missing,
        "solved": solved
    })


@app.route("/validate", methods=["POST"])
def validate_cell():
    """Validate one cell immediately."""

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Invalid request"
        }), 400

    row = data.get("row")
    col = data.get("col")
    value = data.get("value")

    if row is None or col is None or value is None:
        return jsonify({
            "error": "Missing parameters"
        }), 400

    solution = session.get("solution")

    if solution is None:
        return jsonify({
            "error": "No game in progress"
        }), 400

    return jsonify({
        "valid": value == solution[row][col]
    })


@app.route("/hint")
def hint():
    """Reveal one correct cell at the row/col the player's board shows as empty."""

    puzzle = session.get("puzzle")
    solution = session.get("solution")

    if puzzle is None or solution is None:
        return jsonify({
            "error": "No game in progress"
        }), 400

    row = request.args.get("row", type=int)
    col = request.args.get("col", type=int)

    if row is None or col is None:
        # No specific cell requested -- fall back to the first empty
        # cell in the server's own puzzle copy.
        row, col = find_empty_cell(puzzle)

        if row is None:
            return jsonify({
                "error": "Puzzle already complete"
            }), 400
    else:
        if (
            row not in range(sudoku_logic.SIZE)
            or col not in range(sudoku_logic.SIZE)
        ):
            return jsonify({
                "error": "Invalid hint cell"
            }), 400

        if puzzle[row][col] != 0:
            # The client's requested cell isn't empty in the server's
            # record either -- fall back to a genuinely empty cell so
            # Hint never overwrites a filled-in value.
            row, col = find_empty_cell(puzzle)

            if row is None:
                return jsonify({
                    "error": "Puzzle already complete"
                }), 400

    puzzle[row][col] = solution[row][col]
    session["puzzle"] = puzzle

    return jsonify({
        "row": row,
        "col": col,
        "value": solution[row][col]
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Page not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error"
    }), 500


if __name__ == "__main__":
    app.run(debug=True)