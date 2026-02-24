"""
Улучшенный тест API hh.ru
"""

from src.api import HeadHunterAPI
import time

def test_api_connection():
    """Тестирование подключения к API с правильным User-Agent."""

    print("=" * 60)
    print("ТЕСТИРОВАНИЕ API HH.RU (исправленная версия)")
    print("=" * 60)

    api = HeadHunterAPI()

    # Тест 1: Проверка доступности API
    print("\n1. Проверка доступности API...")
    try:
        response = api.session.get("https://api.hh.ru/")
        if response.status_code == 200:
            print("✅ API доступен")
            print(f"   Версия API: {response.json().get('hh', {}).get('version', 'Неизвестно')}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # Тест 2: Поиск компаний по названию
    print("\n2. Поиск компаний...")
    companies_to_find = [
        "Яндекс",
        "Сбер",
        "Тинькофф",
        "VK",
        "Wildberries",
        "Ozon"
    ]

    found_companies = []
    for company_name in companies_to_find:
        print(f"\n   Поиск: {company_name}")
        results = api.search_employers(company_name)

        if results:
            company = results[0]
            print(f"   ✅ Найдена: {company.get('name')} (ID: {company.get('id')})")
            found_companies.append(company)
        else:
            print(f"   ❌ Не найдена")

        time.sleep(0.5)

    # Тест 3: Получение информации о конкретных компаниях
    print("\n3. Получение детальной информации о компаниях...")

    # Используем найденные ID или стандартные
    test_ids = [company.get('id') for company in found_companies if company.get('id')]

    if not test_ids:
        # Если ничего не нашли, используем тестовые ID
        test_ids = [1455, 3529, 3776]

    for emp_id in test_ids[:3]:  # Тестируем первые 3
        print(f"\n   Запрос компании ID: {emp_id}")
        employers = api.get_employers([emp_id])
        if employers:
            emp = employers[0]
            print(f"   ✅ {emp.get('name')}")
            print(f"      Открытых вакансий: {emp.get('open_vacancies', 0)}")

            # Тест 4: Получение вакансий для этой компании
            print(f"\n   4. Получение вакансий для {emp.get('name')}...")
            vacancies = api.get_vacancies(emp_id)
            print(f"      ✅ Найдено вакансий: {len(vacancies)}")

            if vacancies:
                # Покажем пример первой вакансии
                vac = vacancies[0]
                print(f"      Пример: {vac.get('name')}")
        else:
            print(f"   ❌ Не удалось получить данные")

        time.sleep(1)

if __name__ == "__main__":
    test_api_connection()