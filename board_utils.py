import config


def print_board(board, board_size, hide_ships=False):
    print("  " + " ".join([chr(ord('A') + i) for i in range(board_size)]))
    for i, row in enumerate(board):
        display_row = [cell if not hide_ships or cell != config.SHIP_CELL else config.EMPTY_CELL for cell in row]
        print(f"{i + 1:2d} " + " ".join(display_row))


def print_board_with_highlights(board, board_size, possible_starts):
    print("  " + " ".join([chr(ord('A') + i) for i in range(board_size)]))
    for r in range(board_size):
        display_row = [config.HIGHLIGHT_CELL if (r, c) in possible_starts else board[r][c] for c in range(board_size)]
        print(f"{r + 1:2d} " + " ".join(display_row))


def display_boards(player_board, computer_board, board_size):
    print("\n" + "=" * 25)
    print("Ваше поле:".ljust(board_size * 2 + 3) + "Поле компьютера:")
    header = "  " + " ".join([chr(ord('A') + i) for i in range(board_size)])
    print(header + "   " + header)
    for i in range(board_size):
        player_row_str = f"{i + 1:2d} " + " ".join(player_board[i])
        comp_row = [cell if cell != config.SHIP_CELL else config.EMPTY_CELL for cell in computer_board[i]]
        comp_row_str = f"{i + 1:2d} " + " ".join(comp_row)
        print(player_row_str + "   " + comp_row_str)
    print("=" * 25 + "\n")


def is_valid_placement(board, size, row, col, orientation, board_size):
    if orientation == 'H':
        if col + size > board_size: return False
    else:  # 'V'
        if row + size > board_size: return False
    # Проверяем клетку и ее окружение
    for r in range(row - 1, row + (size if orientation == 'V' else 1) + 1):
        for c in range(col - 1, col + (size if orientation == 'H' else 1) + 1):
            if 0 <= r < board_size and 0 <= c < board_size:
                if board[r][c] != config.EMPTY_CELL:
                    return False
    return True


def find_ship_at(board, r_start, c_start, board_size):
    """Находит все координаты сбитого корабля, начиная с одной точки попадания."""
    q = [(r_start, c_start)]
    visited = set(q)
    ship_coords = []

    # Ищем все части корабля (клетки 'X' или '■')
    while q:
        r, c = q.pop(0)

        # Частью корабля считаем и подбитые ('X') и целые ('■') клетки
        if board[r][c] in [config.HIT_CELL, config.SHIP_CELL]:
            ship_coords.append((r, c))

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < board_size and 0 <= nc < board_size and \
                        (nr, nc) not in visited and \
                        board[nr][nc] in [config.HIT_CELL, config.SHIP_CELL]:
                    visited.add((nr, nc))
                    q.append((nr, nc))

    return ship_coords