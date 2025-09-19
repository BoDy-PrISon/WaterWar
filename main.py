import os
import time
import config
import stats_utils
from GameClass import Game
from colorama import init
init()




def check_win(board):
    """Проверяет, остались ли на поле 'живые' корабли."""
    return not any(config.SHIP_CELL in row for row in board)


# --- Основная логика игры ---

# def game_loop():
#     global player_sunk_count,computer_sunk_count
#     player_sunk_count = 0
#     computer_sunk_count = 0
#
#     board_size = 0
#     while not (5 <= board_size <= 26):
#         try:
#             size_str = input("Введите размер поля (от 5 до 26): ")
#             board_size = int(size_str)
#             if not (5 <= board_size <= 26):
#                 print("Размер должен быть в диапазоне от 5 до 26.")
#         except ValueError:
#             print("Пожалуйста, введите число.")
#
#     # Получаем правильный набор кораблей для этого размера поля
#     ships_config = config.get_ship_config(board_size)
#     config.SHIPS_CONFIG = ships_config  # Обновляем глобальный конфиг для совместимости
#
#     player_board = [[config.EMPTY_CELL] * board_size for _ in range(board_size)]
#     computer_board = [[config.EMPTY_CELL] * board_size for _ in range(board_size)]
#
#     difficulty = ''
#     while difficulty not in ['1', '2', '3']:
#         difficulty = input(
#             "Выберите уровень сложности:\n1. Легкий \n2. Средний \n3. Сложный\nВаш выбор: ")
#     computer_move_func = COMPUTER_MOVE_STRATEGIES[difficulty]
#
#     # Выбор расстановки
#     choice = ''
#     while choice not in ['1', '2']:
#         choice = input("Как расставить корабли?\n1. Вручную\n2. Автоматически\nВаш выбор: ")
#     if choice == '1':
#         place_ships_manually(player_board, board_size, ships_config)
#     else:
#         place_ships_randomly(player_board, board_size, ships_config)
#     place_ships_randomly(computer_board, board_size, ships_config)
#
#     player_ships_alive = []
#     for size, count in ships_config.items():
#         player_ships_alive.extend([size] * count)
#     ai_state = initialize_ai_state(board_size)
#     ai_state['player_ships_alive'] = player_ships_alive
#
#     player_shots = set()
#
#     while True:
#         # Ход игрока
#         display_boards(player_board, computer_board, board_size)
#
#         # --- Блок кода для повторного хода игрока при попадании ---
#         player_turn = True
#         while player_turn:
#             coord_str = input("Ваш выстрел (например, A1): ")
#
#             if not coord_str:  # Проверка на пустую строку
#                 print("Ошибка! Вы ничего не ввели. Попробуйте еще раз.")
#                 continue
#
#             row, col = parse_coordinate(coord_str, board_size)
#
#             # Проверка на корректность координат (возврат из parse_coordinate)
#             if row is None:
#                 print("Ошибка! Неверный формат координат (например, A1).")
#                 continue
#
#             # Проверка, что в клетку еще не стреляли
#             if (row, col) in player_shots:
#                 print("Вы уже стреляли в эту клетку. Попробуйте еще раз.")
#                 continue
#             # --- Конец блока проверок ---
#             player_shots.add((row, col))
#
#             # Если все проверки пройдены, обрабатываем выстрел
#             if computer_board[row][col] == config.SHIP_CELL:
#                 print("Попадание!")
#                 computer_board[row][col] = config.HIT_CELL # замена пустого значения на попадание (Х)
#
#                 ship_coords = find_ship_at(computer_board, row, col, board_size)
#                 if is_ship_sunk(computer_board, ship_coords):
#                     print("Корабль потоплен!")
#                     surround_sunk_ship(computer_board, player_shots, ship_coords, board_size)
#                     computer_sunk_count += 1
#
#                 if check_win(computer_board):
#                     display_boards(player_board, computer_board, board_size)
#                     print("\n*** K.O! ***")
#                     stats = stats_utils.load_stats()
#                     stats['games_played'] += 1
#                     stats['player_wins'] += 1
#                     stats['total_ships_sunk_by_player'] += computer_sunk_count
#                     stats['total_ships_sunk_by_computer'] += player_sunk_count
#                     stats_utils.save_stats(stats)
#                     return
#
#                 # Игрок попал, он ходит еще раз
#                 player_turn = True
#                 display_boards(player_board, computer_board, board_size)
#             else:
#                 print("Промах!")
#                 computer_board[row][col] = config.MISS_CELL
#                 # Игрок промахнулся, ход переходит компьютеру
#                 player_turn = False
#
#         display_boards(player_board, computer_board, board_size)
#
#         # Ход компьютера
#         print("\nКомпьютер делает ход...")
#
#         # --- Блок кода для повторного хода компьютера при попадании ---
#         computer_turn = True
#         while computer_turn:
#             row, col = computer_move_func(player_board, ai_state, board_size)
#
#             ai_state['shots'].add((row, col))
#             print(f"Компьютер стреляет в {chr(ord('A') + col)}{row + 1}...")
#             time.sleep(1)
#
#             if player_board[row][col] == config.SHIP_CELL:
#                 print("Компьютер попал!")
#                 player_board[row][col] = config.HIT_CELL
#                 ai_state['hits'].append((row, col))
#
#                 ship_coords = find_ship_at(player_board, row, col, board_size)
#                 if is_ship_sunk(player_board, ship_coords):
#                     print("Компьютер потопил ваш корабль!")
#                     surround_sunk_ship(player_board, ai_state['shots'], ship_coords, board_size)
#                     player_sunk_count += 1
#                     ai_state['hits'].clear()
#
#                 if check_win(player_board):
#                     display_boards(player_board, computer_board, board_size)
#                     print("\n*** Вы не победили! ***")
#                     stats = stats_utils.load_stats()
#                     stats['games_played'] += 1
#                     stats['computer_wins'] += 1
#                     stats['total_ships_sunk_by_player'] += computer_sunk_count
#                     stats['total_ships_sunk_by_computer'] += player_sunk_count
#                     stats_utils.save_stats(stats)
#                     return
#
#                 # Компьютер попал, он ходит еще раз
#                 computer_turn = True
#                 display_boards(player_board, computer_board, board_size)
#             else:
#                 print("Компьютер промахнулся.")
#                 player_board[row][col] = config.MISS_CELL
#                 # Компьютер промахнулся, ход переходит игроку
#                 computer_turn = False

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n--- МОРСКОЙ БОЙ ---")
        print("1. Начать новую игру")
        print("2. Статистика")
        print("3. Выйти")
        choice = input("Ваш выбор: ")

        if choice == '1':
            game = Game()
            game.setup_game()
            game.run()
            input("\nНажмите Enter, чтобы вернуться в главное меню...")
        elif choice == '2':
            stats_utils.display_stats()
            input("\nНажмите Enter, чтобы вернуться в главное меню...")
        elif choice == '3':
            print("До свидания!")
            break
        else:
            print("Неверный ввод, попробуйте еще раз.")
            time.sleep(1)
if __name__ == "__main__":
    main()
