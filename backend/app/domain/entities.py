from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from pathlib import Path

class ListType(Enum):
    NONE = "none"
    BULLET = "bullet"
    NUMBERED = "numbered"
    ALPHA = "alpha"
    ROMAN = "roman"

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
class TextRun:
    text: str
    font_family: Optional[str] = None
    font_size: Optional[float] = None
    is_bold: bool = False
    is_italic: bool = False
    bbox: Optional[Tuple[float, float, float, float]] = None

@dataclass  
class Paragraph:
    text: str
    runs: List[TextRun]
    list_type: ListType = ListType.NONE
    level: int = 0
    list_number: Optional[int] = None
    list_prefix: str = ""
    bbox: Optional[Tuple[float, float, float, float]] = None

@dataclass
class Slide:
    page_number: int
    width: float
    height: float
    blocks: List[Paragraph] = field(default_factory=list)
    raw_chars: List[Dict] = field(default_factory=list)
    detected_page_number: Optional[str] = None
    page_number_position: PageNumberPosition = PageNumberPosition.NONE
    page_number_bbox: Optional[Tuple[float, float, float, float]] = None

@dataclass
class Presentation:
    file_path: Path
    slides: List[Slide]
    metadata: Dict[str, Any] = field(default_factory=dict)
    fonts_used: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)

    def get_slide_by_number(self, number: int) -> Optional[Slide]:
        for slide in self.slides:
            if slide.page_number == number:
                return slide
        return None

    def get_all_text(self) -> str:
        all_text = []
        for slide in self.slides:
            for block in slide.blocks:  
                all_text.append(block.text)
        return "\n".join(all_text)

    def get_all_lists(self) -> List[Paragraph]:
        all_lists = []
        for slide in self.slides:
            for block in slide.blocks:  
                if block.list_type != ListType.NONE:
                    all_lists.append(block)
        return all_lists
