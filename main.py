"""
Главный модуль программы.
Точка входа для взаимодействия с пользователем.
"""

import sys
from src.api import HeadHunterAPI
from src.db_manager import DBManager
from src.config import Config
from src.utils import (
    prepare_employer_data,
    prepare_vacancy_data,
    EMPLOYER_IDS
)


def setup_database():
    """
    Настройка базы данных: создание БД и таблиц.

    Returns:
        DBManager: Экземпляр менеджера БД или None при ошибке
    """
    print("=" * 50)
    print("НАСТРОЙКА БАЗЫ ДАННЫХ")
    print("=" * 50)

    config = Config()
    db_manager = DBManager(config)

    # Проверяем существование базы данных
    if not db_manager.database_exists():
        print(f"База данных {config.db_name} не найдена. Создаем...")
        db_manager.create_database()
    else:
        print(f"База данных {config.db_name} уже существует")

    # Создаем таблицы
    print("\nСоздание таблиц...")
    db_manager.create_tables()

    return db_manager


def reset_database():
    """Сброс базы данных (удаление и создание заново)."""
    print("=" * 50)
    print("СБРОС БАЗЫ ДАННЫХ")
    print("=" * 50)

    config = Config()
    db_manager = DBManager(config)

    # Спрашиваем подтверждение
    response = input(f"Вы уверены, что хотите удалить базу данных {config.db_name}? (да/нет): ")

    if response.lower() in ['да', 'yes', 'y']:
        print("Удаление базы данных...")
        db_manager.drop_database()
        print("Создание новой базы данных...")
        db_manager.create_database()
        db_manager.create_tables()
        print("База данных успешно пересоздана")
    else:
        print("Операция отменена")

    return db_manager


def fetch_and_save_data(db_manager):
    """Получение данных с API и сохранение в БД."""
    print("\n" + "=" * 50)
    print("ПОЛУЧЕНИЕ ДАННЫХ С HH.RU")
    print("=" * 50)

    api = HeadHunterAPI()

    # Получение данных о работодателях
    print("\n1. Получение информации о работодателях...")
    employers_data = api.get_employers(EMPLOYER_IDS)

    if not employers_data:
        print("❌ Не удалось получить данные о работодателях")
        return False

    print(f"✅ Получено данных о {len(employers_data)} работодателях")

    # Подготовка и сохранение работодателей
    prepared_employers = [prepare_employer_data(emp) for emp in employers_data]
    db_manager.insert_employers(prepared_employers)

    # Получение и сохранение вакансий
    print("\n2. Получение вакансий...")
    all_vacancies = []
    total_companies = len(employers_data)

    for idx, employer in enumerate(employers_data, 1):
        emp_id = employer['id']
        emp_name = employer['name']
        print(f"   [{idx}/{total_companies}] {emp_name}...")

        vacancies = api.get_vacancies(emp_id)
        prepared_vacancies = [prepare_vacancy_data(vac, emp_id) for vac in vacancies]
        all_vacancies.extend(prepared_vacancies)

        print(f"      → Найдено вакансий: {len(vacancies)}")

    if all_vacancies:
        db_manager.insert_vacancies(all_vacancies)
        print(f"\n✅ Всего сохранено вакансий: {len(all_vacancies)}")
    else:
        print("\n❌ Не удалось получить данные о вакансиях")
        return False

    return True


def print_companies_and_vacancies(db_manager):
    """Вывод списка компаний и количества вакансий."""
    print("\n" + "=" * 50)
    print("СПИСОК КОМПАНИЙ И КОЛИЧЕСТВО ВАКАНСИЙ")
    print("=" * 50)

    data = db_manager.get_companies_and_vacancies_count()

    if not data:
        print("Нет данных для отображения")
        return

    for item in data:
        print(f"🏢 {item['company']}: {item['count']} вакансий")


def print_all_vacancies(db_manager):
    """Вывод всех вакансий."""
    print("\n" + "=" * 50)
    print("ВСЕ ВАКАНСИИ")
    print("=" * 50)

    data = db_manager.get_all_vacancies()

    if not data:
        print("Нет данных для отображения")
        return

    for item in data:
        salary = f"{item['salary']} руб." if item['salary'] else "Не указана"
        print(f"\n🏢 {item['company']}")
        print(f"📋 {item['vacancy']}")
        print(f"💰 Зарплата: {salary}")
        print(f"🔗 {item['url']}")


def print_avg_salary(db_manager):
    """Вывод средней зарплаты."""
    print("\n" + "=" * 50)
    print("СРЕДНЯЯ ЗАРПЛАТА")
    print("=" * 50)

    avg_salary = db_manager.get_avg_salary()
    print(f"💰 Средняя зарплата по всем вакансиям: {avg_salary} руб.")


def print_vacancies_higher_salary(db_manager):
    """Вывод вакансий с зарплатой выше средней."""
    print("\n" + "=" * 50)
    print("ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ")
    print("=" * 50)

    data = db_manager.get_vacancies_with_higher_salary()

    if not data:
        print("Нет данных для отображения")
        return

    for item in data:
        print(f"\n🏢 {item['company']}")
        print(f"📋 {item['vacancy']}")
        print(f"💰 Зарплата: {item['salary']} руб.")
        print(f"🔗 {item['url']}")


def search_vacancies_by_keyword(db_manager):
    """Поиск вакансий по ключевому слову."""
    print("\n" + "=" * 50)
    print("ПОИСК ВАКАНСИЙ ПО КЛЮЧЕВОМУ СЛОВУ")
    print("=" * 50)

    keyword = input("Введите ключевое слово для поиска: ").strip()

    if not keyword:
        print("❌ Ключевое слово не может быть пустым")
        return

    data = db_manager.get_vacancies_with_keyword(keyword)

    if not data:
        print(f"\n❌ Вакансии с ключевым словом '{keyword}' не найдены")
        return

    print(f"\n✅ Найдено вакансий: {len(data)}")
    for item in data:
        salary = f"{item['salary']} руб." if item['salary'] else "Не указана"
        print(f"\n🏢 {item['company']}")
        print(f"📋 {item['vacancy']}")
        print(f"💰 Зарплата: {salary}")
        print(f"🔗 {item['url']}")


def print_menu():
    """Вывод меню."""
    print("\n" + "=" * 50)
    print("ГЛАВНОЕ МЕНЮ")
    print("=" * 50)
    print("1. Показать список компаний и количество вакансий")
    print("2. Показать все вакансии")
    print("3. Показать среднюю зарплату")
    print("4. Показать вакансии с зарплатой выше средней")
    print("5. Поиск вакансий по ключевому слову")
    print("6. Обновить данные с hh.ru")
    print("7. Сбросить базу данных (удалить и создать заново)")
    print("8. Проверить статус базы данных")
    print("0. Выход")
    print("-" * 50)


def check_database_status(db_manager):
    """Проверка статуса базы данных."""
    print("\n" + "=" * 50)
    print("СТАТУС БАЗЫ ДАННЫХ")
    print("=" * 50)

    # Проверяем существование БД
    exists = db_manager.database_exists()
    print(f"📊 База данных '{db_manager.config.db_name}': {'✅ существует' if exists else '❌ не существует'}")

    if exists:
        # Проверяем наличие таблиц
        db_manager.connect()
        cursor = db_manager.conn.cursor()

        try:
            # Проверяем таблицу employers
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'employers'
            """)
            employers_table = cursor.fetchone()[0] > 0
            print(f"📋 Таблица 'employers': {'✅ существует' if employers_table else '❌ не существует'}")

            # Проверяем таблицу vacancies
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'vacancies'
            """)
            vacancies_table = cursor.fetchone()[0] > 0
            print(f"📋 Таблица 'vacancies': {'✅ существует' if vacancies_table else '❌ не существует'}")

            if employers_table:
                cursor.execute("SELECT COUNT(*) FROM employers")
                employers_count = cursor.fetchone()[0]
                print(f"👥 Количество работодателей: {employers_count}")

            if vacancies_table:
                cursor.execute("SELECT COUNT(*) FROM vacancies")
                vacancies_count = cursor.fetchone()[0]
                print(f"📝 Количество вакансий: {vacancies_count}")

        except Exception as e:
            print(f"Ошибка при проверке таблиц: {e}")
        finally:
            cursor.close()
            db_manager.close()


def main():
    """Главная функция программы."""
    print("Добро пожаловать в программу для работы с вакансиями hh.ru!")
    print("Автор: Курсовая работа по базам данных\n")

    # Настройка базы данных
    db_manager = setup_database()
    if not db_manager:
        print("❌ Не удалось настроить базу данных. Программа завершена.")
        return

    # Проверяем, есть ли данные в БД
    db_manager.connect()
    cursor = db_manager.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employers")
    employers_count = cursor.fetchone()[0]
    cursor.close()
    db_manager.close()

    # Если данных нет, загружаем
    if employers_count == 0:
        print("\nБаза данных пуста. Выполняется загрузка данных...")
        if not fetch_and_save_data(db_manager):
            print("❌ Не удалось загрузить данные. Проверьте подключение к интернету.")
            return
    else:
        print(f"\n✅ В базе данных уже есть {employers_count} работодателей")

    # Основной цикл программы
    while True:
        print_menu()

        choice = input("\nВыберите пункт меню: ").strip()

        if choice == '1':
            print_companies_and_vacancies(db_manager)
        elif choice == '2':
            print_all_vacancies(db_manager)
        elif choice == '3':
            print_avg_salary(db_manager)
        elif choice == '4':
            print_vacancies_higher_salary(db_manager)
        elif choice == '5':
            search_vacancies_by_keyword(db_manager)
        elif choice == '6':
            print("\n🔄 Обновление данных...")
            fetch_and_save_data(db_manager)
        elif choice == '7':
            db_manager = reset_database()
            print("\n🔄 Загрузка данных в новую базу...")
            fetch_and_save_data(db_manager)
        elif choice == '8':
            check_database_status(db_manager)
        elif choice == '0':
            print("\n👋 Спасибо за использование программы! До свидания!")
            break
        else:
            print("\n❌ Неверный выбор. Пожалуйста, выберите пункт из меню.")

    # Закрытие соединения с БД
    db_manager.close()


if __name__ == "__main__":
    main()