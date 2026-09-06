import copy
import random

SIZE = 9
EMPTY = 0

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def find_best_empty_cell(board):
    best = None
    best_candidates = None
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                candidates = [num for num in range(1, SIZE + 1) if is_safe(board, row, col, num)]
                if best is None or len(candidates) < len(best_candidates):
                    best = (row, col)
                    best_candidates = candidates
                    if len(best_candidates) == 1:
                        return best[0], best[1], best_candidates
    if best is None:
        return None, None, []
    return best[0], best[1], best_candidates


def count_solutions(board, limit=2):
    row, col, candidates = find_best_empty_cell(board)
    if row is None:
        return 1

    count = 0
    for num in candidates:
        board[row][col] = num
        count += count_solutions(board, limit)
        board[row][col] = EMPTY
        if count >= limit:
            return count
    return count


def remove_cells(board, clues):
    target_removals = SIZE * SIZE - clues
    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)

    removed = 0
    for row, col in positions:
        if removed >= target_removals:
            break
        if board[row][col] == EMPTY:
            continue

        saved = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) != 1:
            board[row][col] = saved
        else:
            removed += 1


def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution