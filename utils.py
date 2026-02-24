"""
Вспомогательные функции для обработки данных.
"""

from typing import Dict, Any, List, Optional


def parse_salary(salary_data: Optional[Dict[str, Any]]) -> Optional[int]:
    """
    Парсинг зарплаты из данных вакансии.

    Args:
        salary_data: Данные о зарплате из API

    Returns:
        Optional[int]: Средняя зарплата или None
    """
    if not salary_data:
        return None

    salary_from = salary_data.get('from')
    salary_to = salary_data.get('to')

    if salary_from and salary_to:
        return (salary_from + salary_to) // 2
    elif salary_from:
        return salary_from
    elif salary_to:
        return salary_to
    return None


def prepare_employer_data(employer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Подготовка данных работодателя для сохранения в БД.

    Args:
        employer: Данные работодателя из API

    Returns:
        Dict[str, Any]: Подготовленные данные
    """
    return {
        'id': employer['id'],
        'name': employer['name'],
        'description': employer.get('description', ''),
        'site_url': employer.get('site_url', ''),
        'alternate_url': employer.get('alternate_url', ''),
        'open_vacancies': employer.get('open_vacancies', 0)
    }


def prepare_vacancy_data(vacancy: Dict[str, Any], employer_id: int) -> Dict[str, Any]:
    """
    Подготовка данных вакансии для сохранения в БД.

    Args:
        vacancy: Данные вакансии из API
        employer_id: ID работодателя

    Returns:
        Dict[str, Any]: Подготовленные данные
    """
    salary = parse_salary(vacancy.get('salary'))

    # Получаем описание из разных возможных полей
    description = ''
    if vacancy.get('snippet'):
        description = vacancy['snippet'].get('responsibility', '')
    elif vacancy.get('description'):
        description = vacancy['description']

    return {
        'id': vacancy['id'],
        'employer_id': employer_id,
        'name': vacancy['name'],
        'description': description,
        'salary': salary,
        'url': vacancy.get('alternate_url', ''),
        'published_at': vacancy.get('published_at', '')
    }


# Актуальные ID компаний на hh.ru (проверенные)
EMPLOYER_IDS = [
    1455,    # Яндекс
    3529,    # Сбер
    3776,    # VK (бывший Mail.ru)
    633,     # Ростелеком
    2180,    # Ozon
    87021,   # Wildberries
    78638,   # Тинькофф
    8554,    # Газпром нефть
    80,      # Альфа-Банк
    15478    # VK (дополнительный)
]

# Альтернативный вариант - искать компании по названию
def search_companies_by_name(api_client, company_names: List[str]) -> List[Dict]:
    """
    Поиск компаний по названию.

    Args:
        api_client: Экземпляр HeadHunterAPI
        company_names: Список названий компаний

    Returns:
        List[Dict]: Найденные компании
    """
    found_companies = []

    for name in company_names:
        try:
            response = api_client.session.get(
                f'{api_client.BASE_URL}employers',
                params={'text': name, 'only_with_vacancies': True}
            )

            if response.status_code == 200:
                items = response.json().get('items', [])
                if items:
                    # Берем первую найденную компанию
                    company = items[0]
                    found_companies.append(company)
                    print(f"Найдена компания '{name}': ID {company['id']}")
                else:
                    print(f"Компания '{name}' не найдена")

        except Exception as e:
            print(f"Ошибка при поиске компании {name}: {e}")

    return found_companies