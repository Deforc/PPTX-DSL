from abc import ABC, abstractmethod
from typing import Protocol,List,Dict
from pathlib import Path
from .entities import Presentation, TextRun, Slide, Paragraph

class PdfExtractor(Protocol):
    
    def extract(self, file_path: Path) -> Presentation:
class TextNormalizer(Protocol):
    
    def normalize_symbols(self, raw_chars: List[Dict]) -> List[TextRun]:

class LayoutAnalyzer(Protocol):
    
    def build_paragraphs(self, text_runs: List[TextRun], page_width: float, page_height: float) -> List[Paragraph]:

class PageNumberDetector(Protocol):
    
    def detect_page_numbers(self, slides: List[Slide]) -> List[Slide]:
