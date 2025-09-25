import random
import config
import os



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


def display_boards(player_board, computer_board, board_size,reveal_computer_ships=False):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "=" * 25)
    print("Ваше поле:".ljust(board_size * 2 + 3) + "Поле компьютера:")
    header = "  " + " ".join([chr(ord('A') + i) for i in range(board_size)])
    print(header + "   " + header)

    for i in range(board_size):
        player_row_parts = []
        for cell in player_board[i]:
            if cell == config.SHIP_CELL:
                player_row_parts.append((f"{config.COLOR_SHIP}{cell}{config.COLOR_RESET}"))
            elif cell == config.HIT_CELL:
                player_row_parts.append((f"{config.COLOR_HIT}{cell}{config.COLOR_RESET}"))
            elif cell == config.SUNK_CELL:
                player_row_parts.append((f"{config.COLOR_SUNK}{cell}{config.COLOR_RESET}"))
            elif cell == config.MISS_CELL:
                player_row_parts.append((f"{config.COLOR_MISS}{cell}{config.COLOR_RESET}"))
            else:
                player_row_parts.append(cell)
        player_row_str = f"{i + 1:2d} " + " ".join(player_row_parts)

        comp_row_parts = []
        for cell in computer_board[i]:
            if cell == config.HIT_CELL:
                comp_row_parts.append(f"{config.COLOR_HIT}{cell}{config.COLOR_RESET}")
            elif cell == config.SUNK_CELL:
                comp_row_parts.append((f"{config.COLOR_SUNK}{cell}{config.COLOR_RESET}"))
            elif cell == config.MISS_CELL:
                comp_row_parts.append(f"{config.COLOR_MISS}{cell}{config.COLOR_RESET}")
            elif cell == config.SHIP_CELL:
                if reveal_computer_ships:
                    comp_row_parts.append((f"{config.COLOR_SHIP}{cell}{config.COLOR_RESET}"))
                else:
                    comp_row_parts.append(config.EMPTY_CELL)
            else:
                comp_row_parts.append(cell)

        comp_row_str = f"{i+1:2d}" + " ".join(comp_row_parts)
        print(player_row_str + "  " + comp_row_str)
    print("="*25 + "\n")

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

def parse_coordinate(coord_str, board_size):
    """Преобразует строку типа 'A1' в кортеж (строка, столбец)."""
    coord_str = coord_str.upper()
    if not ('A' <= coord_str[0] <= chr(ord('A') + board_size - 1)) or not coord_str[1:].isdigit():
        return None, None
    col = ord(coord_str[0]) - ord('A')
    row = int(coord_str[1:]) - 1
    if not (0 <= row < board_size and 0 <= col < board_size):
        return None, None
    return row, col

def place_ships_manually(board, board_size, ships_list):
    """Позволяет игроку расставить корабли вручную."""
    for ship in ships_list: 
        placed = False
        while not placed:
            possible_starts = set()
            for r in range(board_size):
                for c in range(board_size):
                    if is_valid_placement(board, ship.size, r, c, 'H', board_size) or \
                            is_valid_placement(board, ship.size, r, c, 'V', board_size):
                        possible_starts.add((r, c))

            print(f"\nВаше поле (знаком '{config.HIGHLIGHT_CELL}' отмечены возможные стартовые клетки):")
            print_board_with_highlights(board, board_size, possible_starts)
            
            print(f"Размещаем корабль: {ship.type} ({ship.size} палубы).")
            coord_str = input(f"Введите начальную координату (например, A1): ")
            row, col = parse_coordinate(coord_str, board_size)
            if row is None or (row, col) not in possible_starts:
                print("Ошибка! Неверная или недоступная координата.")
                continue

            can_h = is_valid_placement(board, ship.size, row, col, 'H', board_size)
            can_v = is_valid_placement(board, ship.size, row, col, 'V', board_size)
            orientation = ''
            if can_h and can_v:
                orientation = input("Введите ориентацию (H/V): ").upper()
            elif can_h:
                orientation = 'H'
                print("Автоматически выбрана горизонтальная ориентация.")
            else:
                orientation = 'V'
                print("Автоматически выбрана вертикальная ориентация.")

            if orientation in ['H', 'V'] and is_valid_placement(board, ship.size, row, col, orientation,
                                                                board_size):
                ship_coords = []
                if orientation == 'H':
                    for j in range(ship.size):
                        board[row][col + j] = config.SHIP_CELL
                        ship_coords.append((row, col + j))
                else:
                    for j in range(ship.size):
                        board[row + j][col] = config.SHIP_CELL
                        ship_coords.append((row + j, col))

                ship.coords = ship_coords
                placed = True
            else:
                print("Ошибка! Неверный ввод или невозможно разместить корабль.")
    return board

def place_ships_randomly(board, board_size, ships_list):
    """Расставляет корабли из списка объектов Ship случайным образом."""
    for ship in ships_list:
        placed = False
        attempts = 0
        while not placed and attempts < 1000:
            orientation = random.choice(['H', 'V'])
            row = random.randint(0, board_size - 1)
            col = random.randint(0, board_size - 1)
            if is_valid_placement(board, ship.size, row, col, orientation, board_size):
                if orientation == 'H':
                    for i in range(ship.size): board[row][col + i] = config.SHIP_CELL
                else:
                    for i in range(ship.size): board[row + i][col] = config.SHIP_CELL
                placed = True
            attempts += 1
        if not placed:
            print(f"Не удалось разместить корабль размером {ship.size}!")
    return board

def is_ship_sunk(board, ship_coords):
    """Проверяет, потоплен ли корабль по его координатам."""
    for r, c in ship_coords:
        if board[r][c] == config.SHIP_CELL:
            return False  # Найдена целая часть корабля
    return True


def surround_sunk_ship(board, shots, ship_coords, board_size,sunk_ships_count):
    """Обводит потопленный корабль точками и добавляет эти клетки в 'shots'."""
    ship_cells = set(ship_coords)
    for r_ship, c_ship in ship_coords:
        board[r_ship][c_ship] = config.SUNK_CELL

    for r_hit, c_hit in ship_coords:
        for r in range(r_hit - 1, r_hit + 2):
            for c in range(c_hit - 1, c_hit + 2):
                if 0 <= r < board_size and 0 <= c < board_size:
                    current_coord = (r, c)
                    if current_coord not in ship_cells:
                        if board[r][c] == config.EMPTY_CELL:
                            board[r][c] = config.MISS_CELL
                    shots.add(current_coord)