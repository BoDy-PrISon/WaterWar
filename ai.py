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
def easy_move(ai_state, board_size):
    """Стреляет в случайную, ранее не обстрелянную клетку."""
    while True:
        coord = ai_state['random_shots'].pop()
        if coord not in ai_state['shots']:
            return coord


# --- Уровень сложности: СРЕДНИЙ ---
def medium_move(ai_state, board_size):
    """Использует режим "Охоты" (шахматный порядок) и "Добивания"."""
    hits = ai_state['hits']
    shots = ai_state['shots']
    row, col = -1, -1

    # Режим "Добивания"
    if hits:
        potential_targets = []
        # ... (здесь остаётся вся логика добивания, как в предыдущей версии)
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
                c_left, c_right = first_hit[1] - 1, last_hit[1] + 1;
                r = first_hit[0]
                if c_left >= 0 and (r, c_left) not in shots: potential_targets.append((r, c_left))
                if c_right < board_size and (r, c_right) not in shots: potential_targets.append((r, c_right))
            else:
                r_up, r_down = first_hit[0] - 1, last_hit[0] + 1;
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
    return easy_move(ai_state, board_size)


# --- Уровень сложности: ТЯЖЕЛЫЙ ---
def hard_move(ai_state, board_size):
    """Пока что делает то же, что и средний."""
    # TODO: В будущем можно добавить логику анализа оставшихся кораблей
    return medium_move(ai_state, board_size)


# Словарь для выбора функции хода по уровню сложности
COMPUTER_MOVE_STRATEGIES = {
    '1': easy_move,
    '2': medium_move,
    '3': hard_move,
}