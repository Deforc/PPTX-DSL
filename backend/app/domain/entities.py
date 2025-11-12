from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning" 
    INFO = "info"
    SUCCESS = "success"

class ListType(Enum):
    NONE = "none"
    BULLET = "bullet"
    NUMBERED = "numbered"
    ALPHA = "alpha"  # a), b), c)
    ROMAN = "roman"   # i), ii), iii)

@dataclass
class TextRun:
    """Фрагмент текста с одинаковым форматированием"""
    text: str
    font_family: Optional[str]
    font_size: Optional[float]
    is_bold: bool = False
    is_italic: bool = False
    bbox: tuple[float, float, float, float] = None  # координаты блока

@dataclass  
class Paragraph:
    """Абзац текста"""
    text: str
    runs: List[TextRun]
    list_type: ListType = ListType.NONE
    level: int = 0  # уровень вложенности для списков
    list_number: Optional[int] = None  # номер для нумерованных списков
    list_prefix: str = ""  # префикс списка (•, 1., a) и т.д.)
    bbox: tuple[float, float, float, float] = None  # координаты блока


@dataclass
class Shape:
    """Фигура на слайде (текстовый блок в PDF)"""
    shape_id: str
    shape_type: str  # 'text', 'image' и т.д.
    text: str
    paragraphs: List[Paragraph]
    bbox: tuple[float, float, float, float] = None  # координаты блока

class PageNumberPosition(Enum):
    NONE = "none"
    BOTTOM_RIGHT = "bottom_right"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_LEFT = "bottom_left"
    TOP_RIGHT = "top_right"
    TOP_CENTER = "top_center"
    TOP_LEFT = "top_left"
    CORNER = "corner"

@dataclass
class Slide:
    """Слайд (страница PDF)"""
    page_number: int
    width: float
    height: float
    blocks: List[Paragraph]
    raw_chars: List[Dict] = field(default_factory=list)
    detected_page_number: Optional[str] = None  # Распознанный номер страницы
    page_number_position: PageNumberPosition = PageNumberPosition.NONE
    page_number_bbox: Optional[Tuple[float, float, float, float]] = None

@dataclass
class Presentation:
    """Презентация (PDF документ)"""
    file_path: Path
    slides: List[Slide]
    metadata: Dict[str, Any]
    fonts_used: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-init обработка для Presentation"""
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)

    def get_slide_by_number(self, number: int) -> Optional[Slide]:
        for slide in self.slides:
            if slide.page_number == number:  
                return slide
        return None
    
    def get_all_text(self) -> str:
        """Получить весь текст презентации"""
        return "\n".join(
            shape.text 
            for slide in self.slides 
            for shape in slide.shapes
        )

    def get_all_lists(self) -> List[Paragraph]:
        """Получить все списки из презентации"""
        all_lists = []
        for slide in self.slides:
            for shape in slide.shapes:
                for paragraph in shape.paragraphs:
                    if paragraph.list_type != ListType.NONE:
                        all_lists.append(paragraph)
        return all_lists