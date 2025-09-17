import random
import time

# Импортируем наши модули
import config
from board_utils import (
    print_board,
    print_board_with_highlights,
    display_boards,
    is_valid_placement,
    find_ship_at
)
from ai import (
    initialize_ai_state,
    COMPUTER_MOVE_STRATEGIES
)



def is_ship_sunk(board, ship_coords):
    """Проверяет, потоплен ли корабль по его координатам."""
    for r, c in ship_coords:
        if board[r][c] == config.SHIP_CELL:
            return False  # Найдена целая часть корабля
    return True


def surround_sunk_ship(board, shots, ship_coords, board_size):
    """Обводит потопленный корабль точками и добавляет эти клетки в 'shots'."""
    for r_hit, c_hit in ship_coords:
        for r in range(r_hit - 1, r_hit + 2):
            for c in range(c_hit - 1, c_hit + 2):
                if 0 <= r < board_size and 0 <= c < board_size:
                    if board[r][c] == config.EMPTY_CELL:
                        board[r][c] = config.MISS_CELL
                    # Добавляем в shots, чтобы ИИ сюда больше не стрелял
                    shots.add((r, c))


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


def place_ships_randomly(board, board_size, ships_config):
    """Расставляет корабли случайным образом."""
    for ship_size, count in ships_config.items():
        for _ in range(count):
            placed = False
            # Добавим счетчик, чтобы избежать вечного цикла на всякий случай
            attempts = 0
            while not placed and attempts < 1000:
                orientation = random.choice(['H', 'V'])
                row = random.randint(0, board_size - 1)
                col = random.randint(0, board_size - 1)
                if is_valid_placement(board, ship_size, row, col, orientation, board_size):
                    if orientation == 'H':
                        for i in range(ship_size): board[row][col + i] = config.SHIP_CELL
                    else:
                        for i in range(ship_size): board[row + i][col] = config.SHIP_CELL
                    placed = True
                attempts += 1
            if not placed:
                # Если за 1000 попыток не удалось разместить корабль, что-то не так
                # Можно будет в будущем обработать эту ошибку
                print(f"Не удалось разместить корабль размером {ship_size}!")

    return board


def place_ships_manually(board, board_size, ships_config):
    """Позволяет игроку расставить корабли вручную."""
    print("\n--- Расстановка ваших кораблей ---")
    for ship_size, count in ships_config.items():
        for i in range(count):
            placed = False
            while not placed:
                possible_starts = set()
                for r in range(board_size):
                    for c in range(board_size):
                        if is_valid_placement(board, ship_size, r, c, 'H', board_size) or \
                                is_valid_placement(board, ship_size, r, c, 'V', board_size):
                            possible_starts.add((r, c))

                print(f"\nВаше поле (знаком '{config.HIGHLIGHT_CELL}' отмечены возможные стартовые клетки):")
                print_board_with_highlights(board, board_size, possible_starts)

                print(f"Размещаем {i + 1}-й корабль размером {ship_size} палубы.")
                coord_str = input(f"Введите начальную координату (например, A1): ")
                row, col = parse_coordinate(coord_str, board_size)
                if row is None or (row, col) not in possible_starts:
                    print("Ошибка! Неверная или недоступная координата.")
                    continue

                can_h = is_valid_placement(board, ship_size, row, col, 'H', board_size)
                can_v = is_valid_placement(board, ship_size, row, col, 'V', board_size)
                orientation = ''
                if can_h and can_v:
                    orientation = input("Введите ориентацию (H/V): ").upper()
                elif can_h:
                    orientation = 'H'
                    print("Автоматически выбрана горизонтальная ориентация.")
                else:
                    orientation = 'V'
                    print("Автоматически выбрана вертикальная ориентация.")

                if orientation in ['H', 'V'] and is_valid_placement(board, ship_size, row, col, orientation,
                                                                    board_size):
                    if orientation == 'H':
                        for j in range(ship_size): board[row][col + j] = config.SHIP_CELL
                    else:
                        for j in range(ship_size): board[row + j][col] = config.SHIP_CELL
                    placed = True
                else:
                    print("Ошибка! Неверный ввод или невозможно разместить корабль.")
    return board


def check_win(board):
    """Проверяет, остались ли на поле 'живые' корабли."""
    return not any(config.SHIP_CELL in row for row in board)


# --- Основная логика игры ---

def game_loop():
    board_size = 0
    while not (5 <= board_size <= 26):
        try:
            size_str = input("Введите размер поля (от 5 до 26): ")
            board_size = int(size_str)
            if not (5 <= board_size <= 26):
                print("Размер должен быть в диапазоне от 5 до 26.")
        except ValueError:
            print("Пожалуйста, введите число.")

    # Получаем правильный набор кораблей для этого размера поля
    ships_config = config.get_ship_config(board_size)
    config.SHIPS_CONFIG = ships_config  # Обновляем глобальный конфиг для совместимости

    player_board = [[config.EMPTY_CELL] * board_size for _ in range(board_size)]
    computer_board = [[config.EMPTY_CELL] * board_size for _ in range(board_size)]

    difficulty = ''
    while difficulty not in ['1', '2', '3']:
        difficulty = input(
            "Выберите уровень сложности:\n1. Легкий (случайные выстрелы)\n2. Средний (умная охота)\n3. Сложный\nВаш выбор: ")
    computer_move_func = COMPUTER_MOVE_STRATEGIES[difficulty]

    # Выбор расстановки
    choice = ''
    while choice not in ['1', '2']:
        choice = input("Как расставить корабли?\n1. Вручную\n2. Автоматически\nВаш выбор: ")
    if choice == '1':
        place_ships_manually(player_board, board_size, ships_config)
    else:
        place_ships_randomly(player_board, board_size, ships_config)
    place_ships_randomly(computer_board, board_size, ships_config)

    ai_state = initialize_ai_state(board_size)

    while True:
        # Ход игрока
        display_boards(player_board, computer_board, board_size)

        # --- Блок кода для повторного хода игрока при попадании ---
        player_turn = True
        while player_turn:
            coord_str = input("Ваш выстрел (например, A1): ")
            row, col = parse_coordinate(coord_str, board_size)
            if row is None or computer_board[row][col] in [config.HIT_CELL, config.MISS_CELL]:
                print("Неверный ход. Попробуйте еще раз.")
                continue

            if computer_board[row][col] == config.SHIP_CELL:
                print("Попадание!")
                computer_board[row][col] = config.HIT_CELL

                ship_coords = find_ship_at(computer_board, row, col, board_size)
                if is_ship_sunk(computer_board, ship_coords):
                    print("Корабль потоплен!")
                    surround_sunk_ship(computer_board, set(), ship_coords, board_size)

                if check_win(computer_board):
                    display_boards(player_board, computer_board, board_size)
                    print("\n*** ВЫ ПОБЕДИЛИ! ***")
                    return

                # Игрок попал, он ходит еще раз
                player_turn = True
                display_boards(player_board, computer_board, board_size)
            else:
                print("Промах!")
                computer_board[row][col] = config.MISS_CELL
                # Игрок промахнулся, ход переходит компьютеру
                player_turn = False

        display_boards(player_board, computer_board, board_size)

        # Ход компьютера
        print("\nКомпьютер делает ход...")

        # --- Блок кода для повторного хода компьютера при попадании ---
        computer_turn = True
        while computer_turn:
            row, col = computer_move_func(ai_state, board_size)

            ai_state['shots'].add((row, col))
            print(f"Компьютер стреляет в {chr(ord('A') + col)}{row + 1}...")
            time.sleep(1)

            if player_board[row][col] == config.SHIP_CELL:
                print("Компьютер попал!")
                player_board[row][col] = config.HIT_CELL
                ai_state['hits'].append((row, col))

                ship_coords = find_ship_at(player_board, row, col, board_size)
                if is_ship_sunk(player_board, ship_coords):
                    print("Компьютер потопил ваш корабль!")
                    surround_sunk_ship(player_board, ai_state['shots'], ship_coords, board_size)
                    ai_state['hits'].clear()

                if check_win(player_board):
                    display_boards(player_board, computer_board, board_size)
                    print("\n*** КОМПЬЮТЕР ПОБЕДИЛ! ***")
                    return

                # Компьютер попал, он ходит еще раз
                computer_turn = True
                display_boards(player_board, computer_board, board_size)
            else:
                print("Компьютер промахнулся.")
                player_board[row][col] = config.MISS_CELL
                # Компьютер промахнулся, ход переходит игроку
                computer_turn = False


if __name__ == "__main__":
    game_loop()
