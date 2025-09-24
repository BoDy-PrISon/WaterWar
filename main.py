import os
import time
import config
import stats_utils
from Game_class import Game
from colorama import init
init()

def check_win(board):
    """Проверяет, остались ли на поле 'живые' корабли."""
    return not any(config.SHIP_CELL in row for row in board)

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
