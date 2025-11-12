from abc import ABC, abstractmethod
from pathlib import Path
from domain.entities import Presentation

class BaseParser(ABC):
    """Абстрактный базовый класс для всех парсеров"""
    
    @abstractmethod
    def parse(self, file_path: Path) -> Presentation:
        """Парсит файл и возвращает модель Presentation"""
        pass
    
    def can_parse(self, file_path: Path) -> bool:
        """Проверяет, может ли парсер обработать файл"""
        return file_path.suffix.lower() in self.supported_formats()