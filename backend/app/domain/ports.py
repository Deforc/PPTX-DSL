from abc import ABC, abstractmethod
from typing import Protocol,List,Dict
from pathlib import Path
from .entities import Presentation, TextRun, Slide, Paragraph

class PdfExtractor(Protocol):
    """Интерфейс для извлечения сырых данных из PDF"""
    
    def extract(self, file_path: Path) -> Presentation:
        """
        Извлекает сырые данные из PDF файла
        
        """
class TextNormalizer(Protocol):
    """Интерфейс для нормализации текста"""
    
    def normalize_symbols(self, raw_chars: List[Dict]) -> List[TextRun]:
        """Преобразует сырые символы в TextRun с очищенными шрифтами"""

class LayoutAnalyzer(Protocol):
    """Интерфейс для анализа layout"""
    
    def build_paragraphs(self, text_runs: List[TextRun], page_width: float, page_height: float) -> List[Paragraph]:
        """Группирует TextRun в ParagraphBlock с вычислением bbox"""


class PageNumberDetector(Protocol):
    """Интерфейс для анализа layout"""
    
    def detect_page_numbers(self, slides: List[Slide]) -> List[Slide]:
        """Обнаруживает номера страниц на всех слайдах"""