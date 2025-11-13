from typing import List, Tuple, Optional
import re
from app.domain.entities import ListType, TextRun, Paragraph

class LayoutAnalyzer:
    """Сервис для группировки текста в блоки и анализа layout"""
    
    def __init__(self, word_threshold: float = 1.0, line_threshold: float = 1.5):
        self.word_threshold = word_threshold
        self.line_threshold = line_threshold
    
    def build_paragraphs(self, text_runs: List[TextRun], page_width: float, page_height: float) -> List[Paragraph]:
        """Группирует TextRun в ParagraphBlock"""
        if not text_runs:
            return []
        
        lines = self._group_to_lines(text_runs)
        
        paragraphs = self._group_to_paragraphs(lines)
        
        paragraphs = self._detect_lists(paragraphs)
        
        return paragraphs
    
    def _group_to_lines(self, runs: List[TextRun]) -> List[List[TextRun]]:
        """Группирует TextRun в строки по вертикальной близости"""
        if not runs:
            return []
        
        lines = []
        current_line = [runs[0]]
        
        for run in runs[1:]:
            prev_run = current_line[-1]
            
            prev_y = (prev_run.bbox[1] + prev_run.bbox[3]) / 2
            curr_y = (run.bbox[1] + run.bbox[3]) / 2
            y_diff = abs(curr_y - prev_y)
            
            if y_diff <= self.line_threshold:
                current_line.append(run)
            else:
                current_line_sorted = sorted(current_line, key=lambda r: r.bbox[0])
                lines.append(current_line_sorted)
                current_line = [run]
        
        if current_line:
            current_line_sorted = sorted(current_line, key=lambda r: r.bbox[0])
            lines.append(current_line_sorted)
        
        return lines
    
    def _group_to_paragraphs(self, lines: List[List[TextRun]]) -> List[Paragraph]:
        """Группирует строки в абзацы"""
        if not lines:
            return []
        
        paragraphs = []
        current_paragraph_lines = [lines[0]]
        
        for i in range(1, len(lines)):
            prev_line = lines[i-1]
            curr_line = lines[i]
            
            prev_bottom = min(run.bbox[3] for run in prev_line)
            curr_top = min(run.bbox[1] for run in curr_line)
            vertical_gap = curr_top - prev_bottom
            
            prev_left = min(run.bbox[0] for run in prev_line)
            curr_left = min(run.bbox[0] for run in curr_line)
            indent_diff = abs(curr_left - prev_left)
            
            if vertical_gap > 10 or indent_diff > 20:
                paragraph = self._create_paragraph(current_paragraph_lines)
                paragraphs.append(paragraph)
                current_paragraph_lines = [curr_line]
            else:
                current_paragraph_lines.append(curr_line)
        
        if current_paragraph_lines:
            paragraph = self._create_paragraph(current_paragraph_lines)
            paragraphs.append(paragraph)
        
        return paragraphs
    
    def _create_paragraph(self, lines: List[List[TextRun]]) -> Paragraph:
        """Создает ParagraphBlock из линий"""
        all_runs = [run for line in lines for run in line]
        
        x0 = min(run.bbox[0] for run in all_runs)
        y0 = min(run.bbox[1] for run in all_runs)
        x1 = max(run.bbox[2] for run in all_runs)
        y1 = max(run.bbox[3] for run in all_runs)
        
        full_text = ''.join(run.text for run in all_runs)
        
        return Paragraph(
            text=full_text,
            runs=all_runs,
            bbox=(x0, y0, x1, y1)
        )
    
    def _detect_lists(self, paragraphs: List[Paragraph]) -> List[Paragraph]:
        """Определяет списки в параграфах"""
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
        """Определяет тип списка"""
        stripped = text.lstrip()
        if not stripped:
            return ListType.NONE, "", text
        
        bullet_symbols = ['•', '·', '∙', '◦', '-', '—', '*', '+', '‣']
        if any(stripped.startswith(sym) for sym in bullet_symbols):
            prefix = stripped[0]
            clean_text = stripped[1:].strip()
            return ListType.BULLET, prefix, clean_text
        
        numbered_patterns = [
            r'^\d+\.',      # 1.
            r'^\d+\)',      # 1)
            r'^\(\d+\)',    # (1)
        ]
        
        for pattern in numbered_patterns:
            match = re.search(pattern, stripped)
            if match:
                prefix = match.group(0)
                clean_text = stripped[len(prefix):].strip()
                return ListType.NUMBERED, prefix, clean_text
        
        return ListType.NONE, "", text.strip()
    
    def _detect_indentation_level(self, x_coord: float) -> int:
        """Определяет уровень вложенности по X-координате"""
        if x_coord >= 100:
            return 2
        elif x_coord >= 50:
            return 1
        else:
            return 0
    
    def _extract_list_number(self, prefix: str, list_type: ListType) -> Optional[int]:
        """Извлекает номер из префикса списка"""
        if list_type != ListType.NUMBERED:
            return None
        
        try:
            numbers = re.findall(r'\d+', prefix)
            if numbers:
                return int(numbers[0])
        except (ValueError, IndexError):
            pass
        
        return None