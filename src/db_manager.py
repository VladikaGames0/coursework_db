"""
Модуль для управления базой данных.
Содержит класс DBManager для работы с данными в PostgreSQL.
"""

import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict, Any, Optional
from src.config import Config


class DBManager:
    """Класс для управления базой данных вакансий."""

    def __init__(self, config: Config):
        """
        Инициализация менеджера базы данных.

        Args:
            config: Конфигурация подключения к БД
        """
        self.config = config
        self.conn = None

    def connect(self):
        """Установка соединения с базой данных."""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(**self.config.get_db_params())

    def close(self):
        """Закрытие соединения с базой данных."""
        if self.conn and not self.conn.closed:
            self.conn.close()

    def create_tables(self):
        """Создание таблиц в базе данных."""
        self.connect()
        cursor = self.conn.cursor()

        try:
            # Создание таблицы employers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employers (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    site_url VARCHAR(255),
                    alternate_url VARCHAR(255),
                    open_vacancies INTEGER DEFAULT 0
                )
            """)

            # Создание таблицы vacancies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                    id INTEGER PRIMARY KEY,
                    employer_id INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    salary INTEGER,
                    url VARCHAR(255),
                    published_at TIMESTAMP,
                    FOREIGN KEY (employer_id) REFERENCES employers(id)
                        ON DELETE CASCADE
                )
            """)

            self.conn.commit()
            print("Таблицы успешно созданы")

        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def insert_employers(self, employers_data: List[Dict[str, Any]]):
        """
        Вставка данных о работодателях.

        Args:
            employers_data: Список данных о работодателях
        """
        self.connect()
        cursor = self.conn.cursor()

        try:
            for emp in employers_data:
                cursor.execute("""
                    INSERT INTO employers (id, name, description, site_url, alternate_url, open_vacancies)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        site_url = EXCLUDED.site_url,
                        alternate_url = EXCLUDED.alternate_url,
                        open_vacancies = EXCLUDED.open_vacancies
                """, (
                    emp['id'],
                    emp['name'],
                    emp['description'],
                    emp['site_url'],
                    emp['alternate_url'],
                    emp['open_vacancies']
                ))

            self.conn.commit()
            print(f"Успешно добавлено/обновлено {len(employers_data)} работодателей")

        except Exception as e:
            print(f"Ошибка при вставке работодателей: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def insert_vacancies(self, vacancies_data: List[Dict[str, Any]]):
        """
        Вставка данных о вакансиях.

        Args:
            vacancies_data: Список данных о вакансиях
        """
        self.connect()
        cursor = self.conn.cursor()

        try:
            for vac in vacancies_data:
                cursor.execute("""
                    INSERT INTO vacancies (id, employer_id, name, description, salary, url, published_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        salary = EXCLUDED.salary,
                        url = EXCLUDED.url,
                        published_at = EXCLUDED.published_at
                """, (
                    vac['id'],
                    vac['employer_id'],
                    vac['name'],
                    vac['description'],
                    vac['salary'],
                    vac['url'],
                    vac['published_at']
                ))

            self.conn.commit()
            print(f"Успешно добавлено/обновлено {len(vacancies_data)} вакансий")

        except Exception as e:
            print(f"Ошибка при вставке вакансий: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Returns:
            List[Dict[str, Any]]: Список компаний с количеством вакансий
        """
        self.connect()
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT e.name, COUNT(v.id) as vacancies_count
                FROM employers e
                LEFT JOIN vacancies v ON e.id = v.employer_id
                GROUP BY e.id, e.name
                ORDER BY vacancies_count DESC
            """)

            results = cursor.fetchall()
            return [{'company': row[0], 'count': row[1]} for row in results]

        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
        finally:
            cursor.close()

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.

        Returns:
            List[Dict[str, Any]]: Список всех вакансий
        """
        self.connect()
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    e.name as company_name,
                    v.name as vacancy_name,
                    v.salary,
                    v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                ORDER BY e.name, v.salary DESC NULLS LAST
            """)

            results = cursor.fetchall()
            return [
                {
                    'company': row[0],
                    'vacancy': row[1],
                    'salary': row[2],
                    'url': row[3]
                }
                for row in results
            ]

        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
        finally:
            cursor.close()

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям.

        Returns:
            float: Средняя зарплата
        """
        self.connect()
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT AVG(salary) as avg_salary
                FROM vacancies
                WHERE salary IS NOT NULL
            """)

            result = cursor.fetchone()
            return round(result[0], 2) if result[0] else 0

        except Exception as e:
            print(f"Ошибка при получении средней зарплаты: {e}")
            return 0
        finally:
            cursor.close()

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.

        Returns:
            List[Dict[str, Any]]: Список вакансий с зарплатой выше средней
        """
        self.connect()
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    e.name as company_name,
                    v.name as vacancy_name,
                    v.salary,
                    v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE v.salary > (SELECT AVG(salary) FROM vacancies WHERE salary IS NOT NULL)
                ORDER BY v.salary DESC
            """)

            results = cursor.fetchall()
            return [
                {
                    'company': row[0],
                    'vacancy': row[1],
                    'salary': row[2],
                    'url': row[3]
                }
                for row in results
            ]

        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
        finally:
            cursor.close()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные слова.

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            List[Dict[str, Any]]: Список вакансий, содержащих ключевое слово
        """
        self.connect()
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    e.name as company_name,
                    v.name as vacancy_name,
                    v.salary,
                    v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE LOWER(v.name) LIKE %s
                ORDER BY e.name, v.salary DESC
            """, (f'%{keyword.lower()}%',))

            results = cursor.fetchall()
            return [
                {
                    'company': row[0],
                    'vacancy': row[1],
                    'salary': row[2],
                    'url': row[3]
                }
                for row in results
            ]

        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
        finally:
            cursor.close()