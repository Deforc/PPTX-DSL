import pdfplumber
from pathlib import Path
from typing import List, Dict, Any
from app.domain.ports import PdfExtractor
from app.domain.entities import Presentation, Slide
from app.domain.errors import ExtractionError

class PdfPlumberExtractor(PdfExtractor):
    """Реализация PdfExtractor через PDFPlumber"""
    
    def extract(self, file_path: Path) -> Presentation:
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"PDF файл не найден: {file_path}")
            
            slides = []
            all_fonts = {}
            
            with pdfplumber.open(file_path) as pdf:
                # Извлекаем шрифты
                all_fonts = self._extract_fonts_from_pdf(pdf)
                
                # Парсим каждую страницу
                for page_num, page in enumerate(pdf.pages):
                    slide = self._parse_page(page, page_num + 1)
                    slides.append(slide)
            
            return Presentation(
                file_path=file_path,
                slides=slides,
                metadata=getattr(pdf, 'metadata', {}),
                fonts_used=all_fonts
            )
            
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ExtractionError(f"Ошибка извлечения из PDF: {str(e)}") from e
    
    def _parse_page(self, page: pdfplumber.page.Page, page_num: int) -> Slide:
        """Парсит страницу PDF в сырую модель Slide"""
        chars = page.chars
        width = page.width
        height = page.height
        
        return Slide(
            page_number=page_num,
            width=width,
            height=height,
            blocks=[],  # Блоки будут заполнены на этапе нормализации
            raw_chars=chars
        )
    
    def _extract_fonts_from_pdf(self, pdf) -> Dict[str, Any]:
        """Извлекает информацию о шрифтах из PDF"""
        fonts_info = {}
        
        for page_num, page in enumerate(pdf.pages):
            chars = page.chars
            for char in chars:
                font_name = char.get('fontname', 'Unknown')
                size = char.get('size', 0)
                if font_name not in fonts_info:
                    fonts_info[font_name] = {
                        'size': size,
                        'pages': set(),
                        'char_count': 0
                    }
                fonts_info[font_name]['pages'].add(page_num + 1)
                fonts_info[font_name]['char_count'] += 1
        
        return fonts_info