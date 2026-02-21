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

    return {
        'id': vacancy['id'],
        'employer_id': employer_id,
        'name': vacancy['name'],
        'description': vacancy.get('snippet', {}).get('responsibility', ''),
        'salary': salary,
        'url': vacancy.get('alternate_url', ''),
        'published_at': vacancy.get('published_at', '')
    }


# Список ID интересных компаний для сбора данных
EMPLOYER_IDS = [
    1740,   # Яндекс
    3529,   # Сбер
    78638,  # Тинькофф
    3776,   # Mail.ru Group
    8554,   # Газпром нефть
    80,     # Альфа-Банк
    87021,  # Wildberries
    1122462,# Ozon
    633,    # Ростелеком
    15478   # VK
]