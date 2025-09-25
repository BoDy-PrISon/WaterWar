from pyclbr import Class
import time
import os
from unittest import result

import config
import board_utils
import ai
import stats_utils


class Player:
    """Базовый класс для любого игрока """
    def __init__(self, board_size, ships_config, is_human=False):
        self.is_human = is_human
        self.board_size = board_size
        self.ships_config = ships_config
        self.board = [[config.EMPTY_CELL] * board_size for _ in range(board_size)]
        self.shots = set()
        self.ships = []
        self.sunk_ships_count = 0
        
        ship_class_map = {
            5: Heavy_Lincor, 
            4: Lincor,
            3: Kreyser,
            2: Esminec,
            1: Kater,
        }
        for size, count in ships_config.items():
            for _ in range(count):
                ship_class = ship_class_map.get(size, Ship)
                self.ships.append(ship_class())
            

    def place_ships(self):
        """
        метод расстановки кораблей.
        в зависимости от флага is_human.
        """
        if self.is_human:
            choice = ''
            while choice not in ['1', '2']:
                os.system('cls' if os.name == 'nt' else 'clear')
                choice = input("Как вы хотите расставить корабли?\n1. Вручную\n2. Автоматически\nВаш выбор: ")
            if choice == '1':
                board_utils.place_ships_manually(self.board, self.board_size, self.ships)
            else:
                print("Расставляю корабли автоматически...")
                board_utils.place_ships_randomly(self.board, self.board_size, self.ships)
                time.sleep(1)
        else:
            board_utils.place_ships_randomly(self.board, self.board_size, self.ships)

    def is_defeated(self):
        return not any(config.SHIP_CELL in row for row in self.board)


class HumanPlayer(Player):
    """
    Класс игрока-человека
    Наследует всё от Player
    """
    def __init__(self, board_size, ships_config):
       super().__init__(board_size, ships_config, is_human=True)
    def take_turn(self, opponent):
        player_turn = True
        while player_turn:
            board_utils.display_boards(self.board, opponent.board, self.board_size)
            coord_str = input("Ваш выстрел (например, A1): ")

            if not coord_str:
                print("Ошибка! Вы ничего не ввели. Попробуйте еще раз.")
                continue

            row, col = board_utils.parse_coordinate(coord_str, self.board_size)

            if row is None:
                print("Ошибка! Неверный формат координат (например, A1).")
                time.sleep(2)
                continue

            if (row, col) in self.shots:
                print("Вы уже стреляли в эту клетку. Попробуйте еще раз.")
                time.sleep(2)
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
                    return False
                player_turn = True
            else:
                print("Промах!")
                opponent.board[row][col] = config.MISS_CELL
                player_turn = False
        return True


class ComputerPlayer(Player):
    """Класс для игрока-компьютера."""
    def __init__(self, board_size, ships_config, difficulty):
        super().__init__(board_size, ships_config, is_human=False)
        self.ai_state = ai.initialize_ai_state(board_size)
        self.ai_move_func = ai.COMPUTER_MOVE_STRATEGIES[difficulty]

    

    def take_turn(self, opponent):
        print("\nКомпьютер делает ход...")
        time.sleep(1)

        computer_turn = True
        while computer_turn:
            opponent_ships_alive = [ship.size for ship in opponent.ships if not ship.is_sunk()]
            self.ai_state['player_ships_alive'] = opponent_ships_alive
            
            row, col = self.ai_move_func(opponent.board, self.ai_state, self.board_size)
            self.shots.add((row, col))
            self.ai_state['shots'].add((row, col))
            print(f"Компьютер стреляет в клетку {chr(ord('A') + col)}{row + 1}...")
            time.sleep(1)

            if opponent.board[row][col] == config.SHIP_CELL:
                print("Компьютер попал!")
                opponent.board[row][col] = config.HIT_CELL
                self.ai_state['hits'].append((row, col))
                ship_coords = board_utils.find_ship_at(opponent.board, row, col, self.board_size)
                sunk_this_shot = board_utils.is_ship_sunk(opponent.board, ship_coords)
                if sunk_this_shot:
                    print("Компьютер потопил ваш корабль!")
                    self.sunk_ships_count += 1
                    board_utils.surround_sunk_ship(opponent.board, self.shots, ship_coords, self.board_size,self.sunk_ships_count)
                    self.ai_state['hits'].clear() 

                if opponent.is_defeated():
                    return False
                if sunk_this_shot:
                    computer_turn = False 
                else:
                    computer_turn = True
            else:
                print("Компьютер промахнулся!")
                opponent.board[row][col] = config.MISS_CELL
                computer_turn = False
        return True
class Ship:
    """Абстрактный класс для кораблей"""
    def __init__(self,size,ship_type):
        self.size = size
        self.type = ship_type
        self.coords = [] #координаты
        self.hits = 0
        self.ability_name = "Нет"
        self.ability_cooldown = 0
        self.current_cooldown = 0
    def is_sunk(self):
        return self.hits >= self.size
    def is_ability_ready(self):
        """готова ли способность к использованию."""
        return self.current_cooldown == 0
    def use_ability(self, oppnent_board, target_coords):
        """Метод для использования способности. Будет переопределен в дочерних классах."""
        print("У этого корабля нет активной способности.")
        return None
    def tick_cooldown(self):
        """Уменьшает кулдаун в конце хода"""
        if self.current_cooldown >0:
            self.current_cooldown -= 1

class Heavy_Lincor(Ship):
    def __init__(self):
        super().__init__(size=5, ship_type ="Сверхтяжелый Линкор")
        self.ability_name = "Массированный удар"
        self.ability_cooldown = 5

    def use_ability(self, opponent_board, target_row, target_col, board_size):
        """Атака по площади 5x5."""
        #print(f"{self.type} использует '{self.ability_name}'!")
        #self.current_cooldown = self.ability_cooldown + 1
        #result = []
        #for r in range(target_row - 1, target_row + 2):
        #    for c in range(target_col - 1, target_col+2):
        #        if 0 <= r < board_size and 0 <= c < board_size:
        #            pass
        #return result
        pass
class Lincor(Ship):
    def __init__(self):
        super().__init__(size=4, ship_type ="Линкор")
        self.ability_name = "Артиллерийский удар"
        self.ability_cooldown = 3
    def use_ability(self, opponent_board, target_row, target_col, board_size):
        """Атака по площади 3x3."""
        #print(f"{self.type} использует '{self.ability_name}'!")
        #self.current_cooldown = self.ability_cooldown + 1
        #result = []
        #for r in range(target_row - 1, target_row + 2):
        #    for c in range(target_col - 1, target_col+2):
        #        if 0 <= r < board_size and 0 <= c < board_size:
        #            pass
        #return result
        pass
class Kreyser(Ship):
    def __init__(self):
        super().__init__(size=3, ship_type ="Крейсер")
        self.ability_name = "Разведка боем"
        self.ability_cooldown = 2
    def use_ability(self, opponent_board, target_row, target_col, board_size):
        pass
        #return result

class Esminec(Ship):
    def __init__(self):
        super().__init__(size=2, ship_type ="Эсминец")
        self.ability_name = "Двойной выстрел"
        self.ability_cooldown = 2
    def use_ability(self, opponent_board, target_row, target_col, board_size):
        #return result
        pass
class Kater(Ship):
    def __init__(self):
        super().__init__(size=1, ship_type ="Эсминец")
        self.ability_name = "Маневр"
        self.ability_cooldown = 2
    def use_ability(self, opponent_board, target_row, target_col, board_size):
        #return result
        pass


class Game:
    """класс, управляющий всем игровым процессом."""
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

        difficulty = ''
        while difficulty not in ['1', '2', '3']:
            difficulty = input(
                "Выберите уровень сложности:\n1. Легкий\n2. Средний\n3. Сложный\nВаш выбор: ")

        self.player = HumanPlayer(self.board_size, ships_config)
        self.computer = ComputerPlayer(self.board_size, ships_config, difficulty)
        
        self.player.place_ships()
        print("\nКомпьютер расставляет свои корабли...")
        self.computer.place_ships()
        time.sleep(1)


    def run(self):
        while True:
            
            if not self.player.take_turn(self.computer):
                print("\n*** K.O! Вы победили! ***")
                self.update_stats(winner='player')
                board_utils.display_boards(self.player.board, self.computer.board, self.board_size,reveal_computer_ships=True)
                break

            if not self.computer.take_turn(self.player):
                board_utils.display_boards(self.player.board, self.computer.board, self.board_size,reveal_computer_ships=True)
                print("\n*** Вы не победили! ***")
                self.update_stats(winner='computer')
                break

    def update_stats(self, winner):
        """Обновляет и сохраняет статистику в конце игры."""
        self.stats['games_played'] += 1
        if winner == 'player':
            self.stats['player_wins'] += 1
        else:
            self.stats['computer_wins'] += 1
        
        self.stats['total_ships_sunk_by_player'] += self.player.sunk_ships_count
        self.stats['total_ships_sunk_by_computer'] += self.computer.sunk_ships_count
        stats_utils.save_stats(self.stats)
