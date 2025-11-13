import re
from typing import List, Dict
from app.domain.entities import TextRun

class TextNormalizer:
    
    def normalize_symbols(self, raw_chars: List[Dict]) -> List[TextRun]:
        if not raw_chars:
            return []
        
        normalized_chars = []
        for char in raw_chars:
            normalized_char = self._normalize_char(char)
            if normalized_char:
                normalized_chars.append(normalized_char)
        
        sorted_chars = sorted(normalized_chars, 
                            key=lambda char: (char['bbox'][1], char['bbox'][0]))
        
        text_runs = []
        for char in sorted_chars:
            text_run = TextRun(
                text=char['text'],
                font_family=char['font_family'],
                font_size=char['font_size'],
                is_bold=char['is_bold'],
                is_italic=char['is_italic'],
                bbox=char['bbox']
            )
            text_runs.append(text_run)
        
        return text_runs
    
    def _normalize_char(self, char: Dict) -> Dict:
        font_name = char.get('fontname', 'Unknown')
        text = char.get('text', '')
        
        if not text.strip() and text != ' ':
            return None
        
        font_family, is_bold, is_italic = self._clean_font_name(font_name)
        
        bbox = (
            char.get('x0', 0),
            char.get('top', 0),  
            char.get('x1', 0),
            char.get('bottom', 0)
        )
        
        return {
            'text': text,
            'font_family': font_family,
            'font_size': char.get('size', 12),
            'is_bold': is_bold,
            'is_italic': is_italic,
            'bbox': bbox
        }
    
    def _clean_font_name(self, font_name: str) -> tuple:
        if '+' in font_name:
            font_name = font_name.split('+')[-1]
        
        font_family = font_name
        is_bold = False
        is_italic = False
        
        font_lower = font_name.lower()
        if 'bold' in font_lower:
            is_bold = True
            font_family = font_name.replace('Bold', '').replace('-', '').strip()
        elif 'italic' in font_lower:
            is_italic = True
            font_family = font_name.replace('Italic', '').replace('-', '').strip()
        elif 'oblique' in font_lower:
            is_italic = True
            font_family = font_name.replace('Oblique', '').replace('-', '').strip()
        
        font_family = self._split_merged_font_name(font_family)
        
        return font_family, is_bold, is_italic
    
    def _split_merged_font_name(self, font_name: str) -> str:
        if not font_name or font_name[0].islower():
            return font_name
        
        spaced = ''.join(' ' + char if char.isupper() else char 
                       for i, char in enumerate(font_name)).strip()
        return spaced
