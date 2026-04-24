"""
BaseExtractor — абстрактный класс для всех экстракторов браузеров.
Каждый браузер наследует этот класс и реализует метод extract().
"""

from abc import ABC, abstractmethod
from core.models import BrowserData


class BaseExtractor(ABC):
    """Базовый класс для извлечения данных из браузера."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Название браузера."""

    @abstractmethod
    def extract(self) -> BrowserData:
        """Извлечь все артефакты и вернуть BrowserData."""
