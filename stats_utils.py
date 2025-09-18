import json
import os

STATS_FILE = 'stats.json'

def load_stats():
    """Загружает статистику из файла. Если файл не найден или пуст, возвращает пустую статистику."""
    if not os.path.exists(STATS_FILE):
        # Если файла нет, возвращаем структуру по умолчанию
        return {
            "games_played": 0,
            "player_wins": 0,
            "computer_wins": 0,
            "total_ships_sunk_by_player": 0,
            "total_ships_sunk_by_computer": 0
        }
    try:
        # Открываем файл и читаем из него JSON
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            stats = json.load(f)
            # Проверка, что все ключи на месте, на случай если файл был изменен вручную
            if stats.keys() != {"games_played", "player_wins", "computer_wins", "total_ships_sunk_by_player", "total_ships_sunk_by_computer"}:
                raise json.JSONDecodeError("Incorrect keys in stats file", "", 0)
            return stats
    except (json.JSONDecodeError, FileNotFoundError):
        # Если файл пустой, поврежден или исчез, возвращаем дефолтную структуру
        return {
            "games_played": 0,
            "player_wins": 0,
            "computer_wins": 0,
            "total_ships_sunk_by_player": 0,
            "total_ships_sunk_by_computer": 0
        }


def save_stats(stats_data):
    """Сохраняет словарь со статистикой в JSON-файл."""
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        # `indent=4` делает файл красивым и читабельным
        json.dump(stats_data, f, indent=4, ensure_ascii=False)


def display_stats():
    """Загружает и выводит статистику в консоль."""
    stats = load_stats()

    print("\n--- Статистика Игр ---")
    print(f"Всего сыграно партий: {stats['games_played']}")
    print(f"Побед игрока: {stats['player_wins']}")
    print(f"Побед компьютера: {stats['computer_wins']}")

    # Считаем процент побед, избегая деления на ноль
    if stats['games_played'] > 0:
        win_rate = (stats['player_wins'] / stats['games_played']) * 100
        print(f"Процент побед: {win_rate:.1f}%")
    else:
        print("Процент побед: Н/Д")

    print(f"\nПотоплено кораблей игроком: {stats['total_ships_sunk_by_player']}")
    print(f"Потоплено кораблей компьютером: {stats['total_ships_sunk_by_computer']}")
    print("------------------------")
