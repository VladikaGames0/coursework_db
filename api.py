"""
Модуль для взаимодействия с API hh.ru.
Содержит класс для получения данных о работодателях и вакансиях.
"""

import requests
import time
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
        # Важно! Используем корректный User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
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
                # Добавляем задержку между запросами
                time.sleep(0.5)

                url = f'{self.BASE_URL}employers/{emp_id}'
                print(f"Запрос к: {url}")

                response = self.session.get(url)

                print(f"Статус код: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    employers.append(data)
                    print(f"✅ Успешно: {data.get('name', 'Неизвестно')}")
                elif response.status_code == 404:
                    print(f"❌ Работодатель {emp_id} не найден (404)")
                else:
                    print(f"❌ Ошибка {response.status_code} для работодателя {emp_id}")
                    print(f"Ответ: {response.text[:200]}")

            except requests.exceptions.RequestException as e:
                print(f"❌ Ошибка при получении данных о работодателе {emp_id}: {e}")
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")

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
                    'only_with_salary': False
                }

                response = self.session.get(
                    f'{self.BASE_URL}vacancies',
                    params=params
                )

                if response.status_code != 200:
                    print(f"Ошибка при получении вакансий: {response.status_code}")
                    break

                data = response.json()
                items = data.get('items', [])

                if not items:
                    break

                vacancies.extend(items)
                page += 1

                if page >= data.get('pages', 1):
                    break

                # Задержка между страницами
                time.sleep(0.3)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении вакансий для работодателя {employer_id}: {e}")

        return vacancies

    def search_employers(self, query: str) -> List[Dict[str, Any]]:
        """
        Поиск работодателей по названию.

        Args:
            query: Поисковый запрос

        Returns:
            List[Dict[str, Any]]: Список найденных работодателей
        """
        try:
            params = {
                'text': query,
                'only_with_vacancies': True,
                'per_page': 10
            }

            response = self.session.get(
                f'{self.BASE_URL}employers',
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                print(f"Ошибка при поиске: {response.status_code}")
                return []

        except Exception as e:
            print(f"Ошибка при поиске работодателей: {e}")
            return []