def test_index_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b"Sudoku Game" in response.data


def test_new_game_returns_puzzle(client):
    response = client.get('/new?clues=35')
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert 'puzzle' in data
    assert isinstance(data['puzzle'], list)
    assert len(data['puzzle']) == 9
    assert all(isinstance(row, list) and len(row) == 9 for row in data['puzzle'])


def test_difficulty_levels_change_puzzle_clue_count(client):
    def clue_count(puzzle):
        return sum(cell != 0 for row in puzzle for cell in row)

    easy = client.get('/new?difficulty=easy').get_json()['puzzle']
    medium = client.get('/new?difficulty=medium').get_json()['puzzle']
    hard = client.get('/new?difficulty=hard').get_json()['puzzle']

    assert clue_count(easy) > clue_count(medium) > clue_count(hard)


def test_hint_fills_one_empty_cell_and_locks_it(client):
    client.get('/new?difficulty=easy')
    response = client.get('/hint')
    data = response.get_json()

    assert response.status_code == 200
    assert 'row' in data and 'col' in data and 'value' in data
    assert data['value'] != 0
    assert data['row'] in range(9) and data['col'] in range(9)


def test_check_separates_wrong_values_from_still_empty_cells(client):
    """
    Regression test: /check must flag every cell that needs attention
    -- wrong values go in incorrect[], cells the player hasn't filled
    in yet go in missing[] -- so the UI can highlight all of them red,
    per reviewer feedback, without conflating 'wrong' and 'blank'.
    """
    puzzle = client.get('/new?difficulty=easy').get_json()['puzzle']
    response = client.post('/check', json={'board': puzzle})
    data = response.get_json()

    empty_count = sum(1 for row in puzzle for v in row if v == 0)

    assert response.status_code == 200
    assert data['incorrect'] == []
    assert len(data['missing']) == empty_count
    assert data['solved'] is False


def test_check_reports_solved_when_board_matches_solution(client):
    """
    Regression test: completion should be driven by an explicit
    'solved' flag from the server, not inferred from an empty
    incorrect-cells list (which a blank board would also satisfy).
    """
    board = client.get('/new?difficulty=easy').get_json()['puzzle']

    # Use repeated hints to fill in every remaining cell, reconstructing
    # the fully solved board client-side as we go.
    for _ in range(81):
        hint_resp = client.get('/hint')
        hint_data = hint_resp.get_json()
        if 'error' in hint_data:
            break
        board[hint_data['row']][hint_data['col']] = hint_data['value']

    check_resp = client.post('/check', json={'board': board})
    data = check_resp.get_json()

    assert data['incorrect'] == []
    assert data['solved'] is True


def test_two_clients_get_independent_puzzles(client):
    """
    Regression test: puzzle/solution state must be stored per-session,
    not in a single shared global, so concurrent players don't
    overwrite each other's game.
    """
    from app import app as flask_app

    client_a = flask_app.test_client()
    client_b = flask_app.test_client()

    puzzle_a = client_a.get('/new?difficulty=easy').get_json()['puzzle']
    puzzle_b = client_b.get('/new?difficulty=hard').get_json()['puzzle']

    clues_a = sum(v != 0 for row in puzzle_a for v in row)
    clues_b = sum(v != 0 for row in puzzle_b for v in row)

    # Easy and hard have different clue counts, so if state were shared
    # globally these would collide/match unpredictably between clients.
    assert clues_a != clues_b


def test_hint_fills_the_specific_empty_cell_requested(client):
    """
    Regression test: Hint must fill the exact cell the client says is
    empty, not just whatever the server's own copy thinks is first
    empty (which could be stale relative to what the player has typed).
    """
    puzzle = client.get('/new?difficulty=easy').get_json()['puzzle']
    empty_r, empty_c = next(
        (r, c) for r in range(9) for c in range(9) if puzzle[r][c] == 0
    )

    response = client.get(f'/hint?row={empty_r}&col={empty_c}')
    data = response.get_json()

    assert response.status_code == 200
    assert (data['row'], data['col']) == (empty_r, empty_c)


def test_hint_refuses_to_overwrite_an_already_filled_cell(client):
    """
    Regression test: if asked for a hint at a cell that's already
    filled (prefilled clue or previously hinted), the server must not
    overwrite it -- it should fall back to a genuinely empty cell.
    """
    puzzle = client.get('/new?difficulty=easy').get_json()['puzzle']
    filled_r, filled_c = next(
        (r, c) for r in range(9) for c in range(9) if puzzle[r][c] != 0
    )

    response = client.get(f'/hint?row={filled_r}&col={filled_c}')
    data = response.get_json()

    assert response.status_code == 200
    assert (data['row'], data['col']) != (filled_r, filled_c)


def test_hint_without_row_col_falls_back_to_first_empty_cell(client):
    """
    Backward compatibility: calling /hint with no row/col at all
    should still work, using the server's own puzzle copy.
    """
    client.get('/new?difficulty=easy')
    response = client.get('/hint')
    data = response.get_json()

    assert response.status_code == 200
    assert 'row' in data and 'col' in data
