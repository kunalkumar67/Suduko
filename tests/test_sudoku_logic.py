import copy
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sudoku_logic as sudoku


def _rows_cols_boxes_valid(board):
    for i in range(9):
        row = [v for v in board[i] if v != 0]
        col = [board[r][i] for r in range(9) if board[r][i] != 0]
        if len(row) != len(set(row)):
            return False
        if len(col) != len(set(col)):
            return False

    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = [
                board[r][c]
                for r in range(br, br + 3)
                for c in range(bc, bc + 3)
                if board[r][c] != 0
            ]
            if len(box) != len(set(box)):
                return False
    return True


def test_create_empty_board_is_9x9_of_zeros():
    board = sudoku.create_empty_board()
    assert len(board) == 9
    assert all(len(row) == 9 for row in board)
    assert all(v == 0 for row in board for v in row)


def test_is_safe_detects_row_conflict():
    board = sudoku.create_empty_board()
    board[0][0] = 5
    assert not sudoku.is_safe(board, 0, 1, 5)


def test_is_safe_detects_column_conflict():
    board = sudoku.create_empty_board()
    board[0][0] = 7
    assert not sudoku.is_safe(board, 1, 0, 7)


def test_is_safe_detects_box_conflict():
    board = sudoku.create_empty_board()
    board[0][0] = 3
    assert not sudoku.is_safe(board, 1, 1, 3)


def test_is_safe_allows_non_conflicting_value():
    board = sudoku.create_empty_board()
    board[0][0] = 1
    assert sudoku.is_safe(board, 4, 4, 1)


def test_fill_board_produces_a_complete_valid_board():
    board = sudoku.create_empty_board()
    assert sudoku.fill_board(board) is True
    assert all(v != 0 for row in board for v in row)
    assert _rows_cols_boxes_valid(board)


def test_count_solutions_is_exactly_one_for_a_full_board():
    board = sudoku.create_empty_board()
    sudoku.fill_board(board)
    assert sudoku.count_solutions(copy.deepcopy(board), limit=2) == 1


def test_count_solutions_stops_early_at_limit():
    # A blank board has many solutions -- count_solutions should stop
    # counting once it hits the limit rather than exhaustively
    # searching all of them.
    board = sudoku.create_empty_board()
    result = sudoku.count_solutions(board, limit=2)
    assert result >= 2


def test_generate_puzzle_has_a_unique_solution():
    puzzle, solution = sudoku.generate_puzzle(clues=30)
    assert sudoku.count_solutions(copy.deepcopy(puzzle), limit=2) == 1

    # The solver's unique solution should match the stored solution.
    solved_copy = copy.deepcopy(puzzle)
    sudoku.fill_board(solved_copy)
    assert solved_copy == solution


def test_generate_puzzle_respects_requested_clue_count():
    for clues in (26, 32, 40):
        puzzle, _ = sudoku.generate_puzzle(clues=clues)
        filled = sum(1 for row in puzzle for v in row if v != 0)
        # Uniqueness constraints can occasionally force a couple of
        # extra clues to remain, so allow a small tolerance.
        assert abs(filled - clues) <= 4


def test_remove_cells_never_breaks_uniqueness():
    board = sudoku.create_empty_board()
    sudoku.fill_board(board)
    sudoku.remove_cells(board, clues=30)
    assert sudoku.count_solutions(copy.deepcopy(board), limit=2) == 1
