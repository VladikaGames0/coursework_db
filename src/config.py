"""
Модуль для работы с конфигурацией базы данных.
Содержит настройки подключения к PostgreSQL.
"""

from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Класс для хранения конфигурации подключения к БД."""

    def __init__(self):
        """Инициализация конфигурации из переменных окружения."""
        self.db_name = os.getenv('DB_NAME', 'coursework')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'postgres')
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')

    def get_db_params(self) -> Dict[str, str]:
        """
        Возвращает параметры подключения к БД.

        Returns:
            Dict[str, str]: Словарь с параметрами подключения
        """
        return {
            'dbname': self.db_name,
            'user': self.db_user,
            'password': self.db_password,
            'host': self.db_host,
            'port': self.db_port
        }