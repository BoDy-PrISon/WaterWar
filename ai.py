import random
import time
import config


def initialize_ai_state(board_size):
    """Создает начальное состояние 'памяти' для ИИ."""
    smart_shots = []
    for r in range(board_size):
        for c in range(board_size):
            if (r + c) % 2 == (board_size % 2):  # Улучшенный шахматный порядок
                smart_shots.append((r, c))
    random.shuffle(smart_shots)

    all_shots = [(r, c) for r in range(board_size) for c in range(board_size)]
    random.shuffle(all_shots)

    return {
        'shots': set(),
        'smart_shots': smart_shots,
        'random_shots': all_shots,
        'hits': [],
    }


# --- Уровень сложности: ЛЕГКИЙ ---
def easy_move(player_board,ai_state, board_size):
    """Стреляет в случайную, ранее не обстрелянную клетку."""
    while True:
        # Проверяем, есть ли еще случайные выстрелы
        if not ai_state['random_shots']:
            # Если нет, ищем любую еще не обстрелянную клетку
            all_cells = {(r, c) for r in range(board_size) for c in range(board_size)}
            available_cells = list(all_cells - ai_state['shots'])
            if not available_cells: return (0, 0)  # Аварийный выход
            return random.choice(available_cells)

        coord = ai_state['random_shots'].pop()
        if coord not in ai_state['shots']:
            return coord


# --- Уровень сложности: СРЕДНИЙ ---
def medium_move(player_board, ai_state, board_size):
    """Использует режим "Охоты" (шахматный порядок) и "Добивания"."""
    hits = ai_state['hits']
    shots = ai_state['shots']
    row, col = -1, -1

    # Режим "Добивания"
    if hits:
        potential_targets = []
        if len(hits) == 1:
            r_hit, c_hit = hits[0]
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                r, c = r_hit + dr, c_hit + dc
                if 0 <= r < board_size and 0 <= c < board_size and (r, c) not in shots:
                    potential_targets.append((r, c))
        else:
            hits.sort()
            first_hit, last_hit = hits[0], hits[-1]
            is_horizontal = first_hit[0] == last_hit[0]
            if is_horizontal:
                c_left, c_right = first_hit[1] - 1, last_hit[1] + 1
                r = first_hit[0]
                if c_left >= 0 and (r, c_left) not in shots: potential_targets.append((r, c_left))
                if c_right < board_size and (r, c_right) not in shots: potential_targets.append((r, c_right))
            else:
                r_up, r_down = first_hit[0] - 1, last_hit[0] + 1
                c = first_hit[1]
                if r_up >= 0 and (r_up, c) not in shots: potential_targets.append((r_up, c))
                if r_down < board_size and (r_down, c) not in shots: potential_targets.append((r_down, c))

        if potential_targets:
            return random.choice(potential_targets)
        else:
            hits.clear()  # Корабль окружен, переходим к охоте

    # Режим "Охоты"
    while ai_state['smart_shots']:
        coord = ai_state['smart_shots'].pop()
        if coord not in shots:
            return coord

    # Если умные ходы кончились, переходим на случайные
    return easy_move(player_board,ai_state, board_size)


# --- Уровень сложности: ТЯЖЕЛЫЙ ---
def hard_move(player_board, ai_state, board_size):
    """Использует "тепловую карту" для охоты и логику "добивания"."""
    # Если есть раненый корабль, добиваем его
    if ai_state['hits']:
        return medium_move(player_board, ai_state, board_size)

    # --- Режим "Охоты" с помощью тепловой карты ---
    heatmap = [[0] * board_size for _ in range(board_size)]
    ships_alive = ai_state.get('player_ships_alive', [])

    # Для каждого типа корабля, который еще на плаву
    for ship_size in ships_alive:
        # Пробуем разместить его в каждой клетке
        for r in range(board_size):
            for c in range(board_size):
                # Горизонтально
                if c + ship_size <= board_size:
                    is_possible = True
                    for i in range(ship_size):
                        if player_board[r][c + i] in [config.MISS_CELL, config.SUNK_CELL,config.HIT_CELL]:
                            is_possible = False
                            break
                    if is_possible:
                        for i in range(ship_size):
                            heatmap[r][c + i] += 1
                # Вертикально
                if r + ship_size <= board_size:
                    is_possible = True
                    for i in range(ship_size):
                        if player_board[r + i][c] in [config.MISS_CELL, config.SUNK_CELL,config.HIT_CELL]:
                            is_possible = False
                            break
                    if is_possible:
                        for i in range(ship_size):
                            heatmap[r + i][c] += 1

    # Ищем самые "горячие" клетки, в которые еще не стреляли
    max_heat = -1
    best_moves = []
    for r in range(board_size):
        for c in range(board_size):
            if (r, c) in ai_state['shots']:
                continue  # Пропускаем уже обстрелянные клетки
            if heatmap[r][c] > max_heat:
                max_heat = heatmap[r][c]
                best_moves = [(r, c)]
            elif heatmap[r][c] == max_heat:
                best_moves.append((r, c))

    # Если есть хорошие ходы - выбираем случайный из лучших
    if best_moves:
        return random.choice(best_moves)
    else:
        return medium_move(player_board, ai_state, board_size)

# Словарь для выбора функции хода по уровню сложности
COMPUTER_MOVE_STRATEGIES = {
    '1': easy_move,
    '2': medium_move,
    '3': hard_move,
}