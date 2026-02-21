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


def create_database():
    """Создание базы данных и таблиц."""
    print("=" * 50)
    print("Создание базы данных и таблиц...")
    print("=" * 50)

    config = Config()
    db_manager = DBManager(config)

    try:
        db_manager.create_tables()
        return db_manager
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        return None


def fetch_and_save_data(db_manager):
    """Получение данных с API и сохранение в БД."""
    print("\n" + "=" * 50)
    print("Получение данных с hh.ru...")
    print("=" * 50)

    api = HeadHunterAPI()

    # Получение данных о работодателях
    print("\nПолучение информации о работодателях...")
    employers_data = api.get_employers(EMPLOYER_IDS)

    if not employers_data:
        print("Не удалось получить данные о работодателях")
        return False

    # Подготовка и сохранение работодателей
    prepared_employers = [prepare_employer_data(emp) for emp in employers_data]
    db_manager.insert_employers(prepared_employers)

    # Получение и сохранение вакансий
    print("\nПолучение вакансий...")
    all_vacancies = []

    for employer in employers_data:
        emp_id = employer['id']
        emp_name = employer['name']
        print(f"  Получение вакансий для {emp_name}...")

        vacancies = api.get_vacancies(emp_id)
        prepared_vacancies = [prepare_vacancy_data(vac, emp_id) for vac in vacancies]
        all_vacancies.extend(prepared_vacancies)

    if all_vacancies:
        db_manager.insert_vacancies(all_vacancies)
        print(f"\nВсего сохранено вакансий: {len(all_vacancies)}")
    else:
        print("\nНе удалось получить данные о вакансиях")
        return False

    return True


def print_companies_and_vacancies(db_manager):
    """Вывод списка компаний и количества вакансий."""
    print("\n" + "=" * 50)
    print("СПИСОК КОМПАНИЙ И КОЛИЧЕСТВО ВАКАНСИЙ")
    print("=" * 50)

    data = db_manager.get_companies_and_vacancies_count()

    for item in data:
        print(f"🏢 {item['company']}: {item['count']} вакансий")


def print_all_vacancies(db_manager):
    """Вывод всех вакансий."""
    print("\n" + "=" * 50)
    print("ВСЕ ВАКАНСИИ")
    print("=" * 50)

    data = db_manager.get_all_vacancies()

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
        print("Ключевое слово не может быть пустым")
        return

    data = db_manager.get_vacancies_with_keyword(keyword)

    if not data:
        print(f"\nВакансии с ключевым словом '{keyword}' не найдены")
        return

    print(f"\nНайдено вакансий: {len(data)}")
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
    print("0. Выход")
    print("-" * 50)


def main():
    """Главная функция программы."""
    print("Добро пожаловать в программу для работы с вакансиями hh.ru!")

    # Создание базы данных и таблиц
    db_manager = create_database()
    if not db_manager:
        print("Не удалось создать базу данных. Программа завершена.")
        return

    # Первоначальная загрузка данных
    print("\nВыполняется первоначальная загрузка данных...")
    if not fetch_and_save_data(db_manager):
        print("Не удалось загрузить данные. Программа завершена.")
        return

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
            print("\nОбновление данных...")
            fetch_and_save_data(db_manager)
        elif choice == '0':
            print("\nСпасибо за использование программы! До свидания!")
            break
        else:
            print("\nНеверный выбор. Пожалуйста, выберите пункт из меню.")

    # Закрытие соединения с БД
    db_manager.close()


if __name__ == "__main__":
    main()