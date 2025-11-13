from pathlib import Path
from app.adapters.pdf.pdfplumber_extractor import PdfPlumberExtractor
from app.services.pdf.normalization import TextNormalizer
from app.services.pdf.layout import LayoutAnalyzer
from app.services.pdf.page_number import PageNumberDetector
from app.domain.entities import Presentation

class PdfProcessingService:
    
    def __init__(self):
        self.extractor = PdfPlumberExtractor()
        self.normalizer = TextNormalizer()
        self.layout_analyzer = LayoutAnalyzer()
        self.page_number_detector = PageNumberDetector()
    
    def process_pdf(self, file_path: Path) -> Presentation:

        raw_presentation = self.extractor.extract(file_path)
        
        processed_slides = []
        for raw_slide in raw_presentation.slides:
            text_runs = self.normalizer.normalize_symbols(raw_slide.raw_chars)
            
            paragraphs = self.layout_analyzer.build_paragraphs(
                text_runs, raw_slide.width, raw_slide.height
            )
            
            processed_slide = raw_slide
            processed_slide.blocks = paragraphs
            processed_slides.append(processed_slide)
        
        processed_slides = self.page_number_detector.detect_page_numbers(processed_slides)
        
        return Presentation(
            file_path=raw_presentation.file_path,
            slides=processed_slides,
            metadata=raw_presentation.metadata,
            fonts_used=raw_presentation.fonts_used
        )
