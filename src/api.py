"""
Модуль для взаимодействия с API hh.ru.
Содержит класс для получения данных о работодателях и вакансиях.
"""

import requests
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class BaseAPIClient(ABC):
    """Абстрактный базовый класс для работы с API."""

    @abstractmethod
    def get_employers(self, employer_ids: List[int]) -> List[Dict[str, Any]]:
        """Получение информации о работодателях."""
        pass

    @abstractmethod
    def get_vacancies(self, employer_id: int) -> List[Dict[str, Any]]:
        """Получение вакансий работодателя."""
        pass


class HeadHunterAPI(BaseAPIClient):
    """Класс для работы с API HeadHunter."""

    BASE_URL = 'https://api.hh.ru/'

    def __init__(self):
        """Инициализация клиента API."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Coursework/1.0 (test@example.com)'
        })

    def get_employers(self, employer_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Получение информации о работодателях по их ID.

        Args:
            employer_ids: Список ID работодателей

        Returns:
            List[Dict[str, Any]]: Список данных о работодателях
        """
        employers = []
        for emp_id in employer_ids:
            try:
                response = self.session.get(f'{self.BASE_URL}employers/{emp_id}')
                response.raise_for_status()
                employers.append(response.json())
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении данных о работодателе {emp_id}: {e}")
        return employers

    def get_vacancies(self, employer_id: int) -> List[Dict[str, Any]]:
        """
        Получение вакансий работодателя.

        Args:
            employer_id: ID работодателя

        Returns:
            List[Dict[str, Any]]: Список вакансий
        """
        vacancies = []
        page = 0
        per_page = 100

        try:
            while True:
                params = {
                    'employer_id': employer_id,
                    'page': page,
                    'per_page': per_page,
                    'only_with_salary': True
                }

                response = self.session.get(
                    f'{self.BASE_URL}vacancies',
                    params=params
                )
                response.raise_for_status()

                data = response.json()
                items = data.get('items', [])

                if not items:
                    break

                vacancies.extend(items)
                page += 1

                if page >= data.get('pages', 1):
                    break

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении вакансий для работодателя {employer_id}: {e}")

        return vacancies