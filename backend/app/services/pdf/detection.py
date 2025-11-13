from app.domain.entities import Paragraph, ListType
from typing import List, Tuple, Optional
import re

class ListDetection:

    def _detect_lists(self, paragraphs: List[Paragraph]) -> List[Paragraph]:
        for paragraph in paragraphs:
            list_type, list_prefix, clean_text = self._detect_list_type(paragraph.text)
            
            if list_type != ListType.NONE:
                paragraph.list_type = list_type
                paragraph.list_prefix = list_prefix
                paragraph.text = clean_text
                paragraph.level = self._detect_indentation_level(paragraph.bbox[0])
                paragraph.list_number = self._extract_list_number(list_prefix, list_type)
        
        return paragraphs
    
    def _detect_list_type(self, text: str) -> Tuple[ListType, str, str]:
        stripped = text.lstrip()
        if not stripped:
            return ListType.NONE, "", text
        
        bullet_symbols = ['•', '·', '∙', '◦', '-', '—', '*', '+', '‣']
        if any(stripped.startswith(sym) for sym in bullet_symbols):
            prefix = stripped[0]
            clean_text = stripped[1:].strip()
            return ListType.BULLET, prefix, clean_text
        
        numbered_patterns = [
            r'^\d+\.',
            r'^\d+\)',
            r'^\(\d+\)',
        ]
        
        for pattern in numbered_patterns:
            match = re.search(pattern, stripped)
            if match:
                prefix = match.group(0)
                clean_text = stripped[len(prefix):].strip()
                return ListType.NUMBERED, prefix, clean_text
        
        return ListType.NONE, "", text.strip()
    
    def _detect_indentation_level(self, x_coord: float) -> int:
        if x_coord >= 100:
            return 2
        elif x_coord >= 50:
            return 1
        else:
            return 0
    
    def _extract_list_number(self, prefix: str, list_type: ListType) -> Optional[int]:
        if list_type != ListType.NUMBERED:
            return None
        
        try:
            numbers = re.findall(r'\d+', prefix)
            if numbers:
                return int(numbers[0])
        except (ValueError, IndexError):
            pass
        
        return None
