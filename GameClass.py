import time

import config
import board_utils
import ai
import stats_utils


class Player:
    def __init__(self, board_size, ships_config):
        self.board_size = board_size
        self.ships_config = ships_config
        # Создаем доску для игрока
        self.board = [[config.EMPTY_CELL] * board_size for _ in range(board_size)]
        # Множество для хранения выстрелов этого игрока
        self.shots = set()
        # Список живых кораблей, который будет уменьшаться
        self.ships_alive = []
        self.sunk_ships_count = 0
        for size, count in ships_config.items():
            self.ships_alive.extend([size] * count)

    def place_ships(self):
        # Этот метод будет содержать логику расстановки кораблей
        # Для человека - ручная, для компьютера - автоматическая
        pass

    def take_turn(self, opponent):
        # Этот метод будет обрабатывать ход игрока
        # `opponent` - это будет экземпляр другого игрока (чтобы стрелять по его доске)
        pass

    def is_defeated(self):
        # Проверяет, проиграл ли игрок (остались ли у него корабли)
        return not any(config.SHIP_CELL in row for row in self.board)


class HumanPlayer(Player):
    def place_ships(self):
        board_utils.place_ships_manually(self.board, self.board_size, self.ships_config)

    def take_turn(self, opponent):
        """Обрабатывает ход человека. Возвращает True, если был сделан успешный ход, False если игра должна закончиться."""
        player_turn = True
        while player_turn:
            # Отображаем доски перед каждым выстрелом
            board_utils.display_boards(self.board, opponent.board, self.board_size)

            coord_str = input("Ваш выстрел (например, A1): ")

            if not coord_str:
                print("Ошибка! Вы ничего не ввели. Попробуйте еще раз.")
                continue

            row, col = board_utils.parse_coordinate(coord_str, self.board_size)

            if row is None:
                print("Ошибка! Неверный формат координат (например, A1).")
                continue

            if (row, col) in self.shots:
                print("Вы уже стреляли в эту клетку. Попробуйте еще раз.")
                continue

            self.shots.add((row, col))

            if opponent.board[row][col] == config.SHIP_CELL:
                print("Попадание!")
                opponent.board[row][col] = config.HIT_CELL

                ship_coords = board_utils.find_ship_at(opponent.board, row, col, self.board_size)
                if board_utils.is_ship_sunk(opponent.board, ship_coords):
                    print("Корабль потоплен!")
                    self.sunk_ships_count += 1
                    board_utils.surround_sunk_ship(opponent.board, self.shots, ship_coords, self.board_size,self.sunk_ships_count)


                if opponent.is_defeated():
                    return False  # Сигнал о том, что игра окончена

                # Игрок попал, он ходит еще раз
                player_turn = True
            else:
                print("Промах!")
                opponent.board[row][col] = config.MISS_CELL
                player_turn = False  # Промах, ход переходит компьютеру

        return True  # Ход завершен, игра продолжается


class ComputerPlayer(Player):
    def __init__(self, board_size, ships_config, difficulty):
        super().__init__(board_size, ships_config)
        self.ai_state = ai.initialize_ai_state(board_size)
        self.ai_move_func = ai.COMPUTER_MOVE_STRATEGIES[difficulty]

    def place_ships(self):
        # Компьютер всегда расставляет корабли случайно
        board_utils.place_ships_randomly(self.board, self.board_size, self.ships_config)

    def take_turn(self, opponent):
        print("\nКомпьютер делает ход...")
        time.sleep(1)

        computer_turn = True
        while computer_turn:
            print(f"[DEBUG] Вызываю функцию ИИ: {self.ai_move_func.__name__}")
            row, col = self.ai_move_func(
                opponent.board,
                self.ai_state,
                self.board_size
            )
            self.shots.add((row, col))
            print(f"Компьютер стреляет в клетку {chr(ord('A') + col)}{row + 1}...")
            time.sleep(1)
            if opponent.board[row][col] == config.SHIP_CELL:
                print("Компьютер попал!")
                opponent.board[row][col] = config.HIT_CELL
                ship_coords = board_utils.find_ship_at(opponent.board, row, col, self.board_size)
                if board_utils.is_ship_sunk(opponent.board, ship_coords):
                    print("Корабль потоплен!")
                    self.sunk_ships_count += 1
                    board_utils.surround_sunk_ship(opponent.board, self.shots, ship_coords, self.board_size,
                                                   self.sunk_ships_count)
                if opponent.is_defeated():
                    return False
                computer_turn = True
            else:
                print("Компьютер промахнулся!")
                opponent.board[row][col] = config.MISS_CELL
                computer_turn = False

        return True

class Game:
    def __init__(self):
        self.player = None
        self.computer = None
        self.board_size = 0
        self.stats = stats_utils.load_stats()

    def setup_game(self):
        board_size = 0
        while not (5 <= board_size <= 26):
            try:
                size_str = input("Введите размер поля (от 5 до 26): ")
                board_size = int(size_str)
                if not (5 <= board_size <= 26):
                    print("Размер должен быть в диапазоне от 5 до 26.")
            except ValueError:
                print("Пожалуйста, введите число.")
        self.board_size = board_size

        ships_config = config.get_ship_config(self.board_size)

        # --- Выбор сложности ---
        difficulty = ''
        while difficulty not in ['1', '2', '3']:
            difficulty = input(
                "Выберите уровень сложности:\n1. Легкий (случайные выстрелы)\n2. Средний (умная охота)\n3. Сложный\nВаш выбор: ")

        self.player = HumanPlayer(self.board_size, ships_config)
        self.computer = ComputerPlayer(self.board_size, ships_config, difficulty)

        # --- Расстановка кораблей ---
        print("\n--- Расстановка ваших кораблей ---")
        self.player.place_ships()

        print("\nКомпьютер расставляет свои корабли...")
        self.computer.place_ships()

    def run(self):
        # Основной игровой цикл
        while True:
            # Ход игрока
            game_continues = self.player.take_turn(self.computer)
            if not game_continues:
                board_utils.display_boards(self.player.board, self.computer.board, self.board_size)
                print("\n*** K.O! Вы победили! ***")
                self.stats['games_played'] += 1
                self.stats['player_wins'] += 1
                self.stats['total_ships_sunk_by_player'] += self.player.sunk_ships_count
                self.stats['total_ships_sunk_by_computer'] += self.computer.sunk_ships_count
                stats_utils.save_stats(self.stats)
                break

            # Ход компьютера
            game_continues = self.computer.take_turn(self.player)
            if not game_continues:
                board_utils.display_boards(self.player.board, self.computer.board, self.board_size)
                print("\n*** Вы не победили! ***")
                self.stats['games_played'] += 1
                self.stats['computer_wins'] += 1
                self.stats['total_ships_sunk_by_player'] += self.player.sunk_ships_count
                self.stats['total_ships_sunk_by_computer'] += self.computer.sunk_ships_count
                stats_utils.save_stats(self.stats)
                break
        pass
