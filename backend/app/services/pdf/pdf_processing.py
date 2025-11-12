from pathlib import Path
from app.adapters.pdf.pdfplumber_extractor import PdfPlumberExtractor
from app.services.pdf.normalization import TextNormalizer
from app.services.pdf.layout import LayoutAnalyzer
from app.services.pdf.page_number import PageNumberDetector
from app.domain.entities import Presentation
from typing import Dict, Any

class PdfProcessingService:
    """Главный сервис для обработки PDF"""
    
    def __init__(self):
        self.extractor = PdfPlumberExtractor()
        self.normalizer = TextNormalizer()
        self.layout_analyzer = LayoutAnalyzer()
        self.page_number_detector = PageNumberDetector()
    
    def process_pdf(self, file_path: Path) -> Presentation:
        """Обрабатывает PDF файл через все этапы"""
        # 1. Извлечение сырых данных
        raw_presentation = self.extractor.extract(file_path)
        
        # 2. Нормализация и анализ layout для каждого слайда
        processed_slides = []
        for raw_slide in raw_presentation.slides:
            # Нормализация символов
            text_runs = self.normalizer.normalize_symbols(raw_slide.raw_chars)
            
            # Построение параграфов
            paragraphs = self.layout_analyzer.build_paragraphs(
                text_runs, raw_slide.width, raw_slide.height
            )
            
            # Создаем обработанный слайд
            processed_slide = raw_slide
            processed_slide.blocks = paragraphs
            processed_slides.append(processed_slide)
        
        # 3. Обнаружение номеров страниц
        processed_slides = self.page_number_detector.detect_page_numbers(processed_slides)
        
        # Создаем финальную презентацию
        return Presentation(
            file_path=raw_presentation.file_path,
            slides=processed_slides,
            metadata=raw_presentation.metadata,
            fonts_used=raw_presentation.fonts_used
        )
    
    def get_page_number_analysis(self, presentation: Presentation) -> Dict[str, Any]:
        """Возвращает анализ номеров страниц"""
        return self.page_number_detector.get_page_number_statistics(presentation.slides)