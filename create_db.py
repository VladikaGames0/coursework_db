"""
Отдельный скрипт для создания базы данных.
Можно запускать отдельно от основной программы.
"""

from src.db_manager import DBManager
from src.config import Config


def init_database():
    """Инициализация базы данных."""
    print("=" * 60)
    print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 60)

    config = Config()
    db_manager = DBManager(config)

    # Создаем базу данных
    print(f"\n1. Проверка базы данных '{config.db_name}'...")
    if not db_manager.database_exists():
        print(f"   База данных не найдена. Создаем...")
        db_manager.create_database()
    else:
        print(f"   База данных уже существует")

    # Создаем таблицы
    print(f"\n2. Создание таблиц...")
    db_manager.create_tables()

    print(f"\n✅ База данных успешно инициализирована!")

    db_manager.close()


if __name__ == "__main__":
    init_database()