from colorama import Fore,Style

COLOR_SHIP = Fore.YELLOW
COLOR_HIT = Fore.RED
COLOR_MISS = Fore.BLUE
COLOR_SUNK = Fore.MAGENTA
COLOR_RESET = Style.RESET_ALL

EMPTY_CELL = 'O'
SHIP_CELL = '■'
HIT_CELL = 'X'
MISS_CELL = 'T'
HIGHLIGHT_CELL = '+'
SUNK_CELL = '#'

SHIPS_CONFIG_TEMPLATES = {
    # Для полей до 6x6 включительно
    'small': {3: 1, 2: 1, 1: 2},
    # Для полей 7x7 и 8x8
    'medium': {4: 1, 3: 1, 2: 2, 1: 3},
    # Для полей 9x9 и больше
    'large': {4: 1, 3: 2, 2: 3, 1: 4}
}

def get_ship_config(board_size):
    """Возвращает конфигурацию кораблей в зависимости от размера поля."""
    if board_size <= 6:
        return SHIPS_CONFIG_TEMPLATES['small'].copy()
    elif board_size <= 8:
        return SHIPS_CONFIG_TEMPLATES['medium'].copy()
    else:
        return SHIPS_CONFIG_TEMPLATES['large'].copy()

# Этот словарь больше не нужен как основная константа,
# но его можно оставить для обратной совместимости или удалить.
# Пока что просто заменим его на пустой, чтобы не сломать импорты.
SHIPS_CONFIG = {}

