import re
from typing import List, Tuple, Dict, Any
from app.domain.entities import Slide, PageNumberPosition

class PageNumberDetector:
    """Сервис для обнаружения и проверки номеров страниц"""
    
    def __init__(self):
        self.page_number_patterns = [
            r'^\d{1,3}$',
            r'^\d{1,3}\s*[/\\\-]\s*\d{1,3}$',
            r'^\d{1,3}\s+из\s+\d{1,3}$',
        ]
        
        self.positions = {
            PageNumberPosition.BOTTOM_RIGHT: (0.7, 0.9, 0.9, 1.0),  
            PageNumberPosition.BOTTOM_CENTER: (0.4, 0.9, 0.6, 1.0), 
            PageNumberPosition.BOTTOM_LEFT: (0.0, 0.9, 0.3, 1.0),   
            PageNumberPosition.TOP_RIGHT: (0.7, 0.0, 0.9, 0.1),     
            PageNumberPosition.TOP_CENTER: (0.4, 0.0, 0.6, 0.1),    
            PageNumberPosition.TOP_LEFT: (0.0, 0.0, 0.3, 0.1),      
            PageNumberPosition.CORNER: (0.9, 0.9, 1.0, 1.0),        
        }
    
    def detect_page_numbers(self, slides: List[Slide]) -> List[Slide]:
        """Обнаруживает номера страниц на всех слайдах"""
        for slide in slides:
            self._detect_slide_page_number(slide)
        
        self._validate_page_number_sequence(slides)
        
        return slides
    
    def _detect_slide_page_number(self, slide: Slide) -> None:
        """Обнаруживает номер страницы на одном слайде"""
        if not slide.blocks:
            return
        
        page_number_candidates = []
        
        for block in slide.blocks:
            if self._is_page_number_candidate(block.text, block.bbox, slide.width, slide.height):
                confidence = self._calculate_confidence(block.text, block.bbox, slide.width, slide.height)
                page_number_candidates.append({
                    'block': block,
                    'confidence': confidence,
                    'position': self._detect_position(block.bbox, slide.width, slide.height)
                })
        
        if page_number_candidates:
            best_candidate = max(page_number_candidates, key=lambda x: x['confidence'])
            
            if best_candidate['confidence'] > 0.5:  
                slide.detected_page_number = best_candidate['block'].text
                slide.page_number_position = best_candidate['position']
                slide.page_number_bbox = best_candidate['block'].bbox
    
    def _is_page_number_candidate(self, text: str, bbox: Tuple[float, float, float, float], 
                                page_width: float, page_height: float) -> bool:
        """Проверяет, является ли блок кандидатом в номер страницы"""
        
        if not self._matches_page_number_pattern(text):
            return False
        
        
        if not self._is_in_page_number_zone(bbox, page_width, page_height):
            return False
        
        
        bbox_width = bbox[2] - bbox[0]
        bbox_height = bbox[3] - bbox[1]
        
        if bbox_width > page_width * 0.2 or bbox_height > page_height * 0.1:
            return False
        
        return True
    
    def _matches_page_number_pattern(self, text: str) -> bool:
        """Проверяет текст на соответствие паттернам номеров страниц"""
        clean_text = text.strip()
        
        for pattern in self.page_number_patterns:
            if re.match(pattern, clean_text, re.IGNORECASE):
                return True
        
        return False
 
    def _is_in_page_number_zone(self, bbox: Tuple[float, float, float, float], 
                              page_width: float, page_height: float) -> bool:
        """Проверяет, находится ли блок в зоне типичного расположения номеров страниц"""
        x_center = (bbox[0] + bbox[2]) / 2 / page_width
        y_center = (bbox[1] + bbox[3]) / 2 / page_height
        
        
        page_number_zones = [
            (0.7, 0.9, 1.0, 1.0),  # правый нижний угол
            (0.4, 0.9, 0.6, 1.0),  # центр снизу
            (0.0, 0.9, 0.3, 1.0),  # левый нижний угол
            (0.7, 0.0, 1.0, 0.1),  # правый верхний угол
            (0.4, 0.0, 0.6, 0.1),  # центр сверху
            (0.0, 0.0, 0.3, 0.1),  # левый верхний угол
        ]
        
        for zone in page_number_zones:
            if (zone[0] <= x_center <= zone[2] and 
                zone[1] <= y_center <= zone[3]):
                return True
        
        return False
    
    def _calculate_confidence(self, text: str, bbox: Tuple[float, float, float, float],
                           page_width: float, page_height: float) -> float:
        """Вычисляет уверенность, что это номер страницы (0-1)"""
        confidence = 0.0
        
        clean_text = text.strip()
        
        if re.match(r'^\d{1,3}$', clean_text):
            confidence += 0.4
        elif re.match(r'^\d{1,3}\s*[/\\\-]\s*\d{1,3}$', clean_text):
            confidence += 0.3
        else:
            confidence += 0.2
        
        position_confidence = self._calculate_position_confidence(bbox, page_width, page_height)
        confidence += position_confidence * 0.4
        
        bbox_height = bbox[3] - bbox[1]
        if bbox_height < page_height * 0.02:  
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _calculate_position_confidence(self, bbox: Tuple[float, float, float, float],
                                    page_width: float, page_height: float) -> float:
        """Вычисляет уверенность на основе позиции"""
        x_center = (bbox[0] + bbox[2]) / 2 / page_width
        y_center = (bbox[1] + bbox[3]) / 2 / page_height
        
        position_weights = [
            # (x_min, x_max, y_min, y_max, weight)
            (0.85, 1.0, 0.85, 1.0, 1.0),   # правый нижний угол - самый вероятный
            (0.4, 0.6, 0.9, 1.0, 0.8),     # центр снизу
            (0.0, 0.15, 0.85, 1.0, 0.7),   # левый нижний угол
            (0.85, 1.0, 0.0, 0.15, 0.6),   # правый верхний угол
            (0.4, 0.6, 0.0, 0.15, 0.5),    # центр сверху
            (0.0, 0.15, 0.0, 0.15, 0.4),   # левый верхний угол
        ]
        
        for x_min, x_max, y_min, y_max, weight in position_weights:
            if (x_min <= x_center <= x_max and 
                y_min <= y_center <= y_max):
                return weight
        
        return 0.1  
    
    def _detect_position(self, bbox: Tuple[float, float, float, float],
                       page_width: float, page_height: float) -> PageNumberPosition:
        """Определяет позицию номера страницы"""
        x_center = (bbox[0] + bbox[2]) / 2 / page_width
        y_center = (bbox[1] + bbox[3]) / 2 / page_height
        
        if y_center > 0.7:  
            if x_center > 0.7:
                return PageNumberPosition.BOTTOM_RIGHT
            elif x_center < 0.3:
                return PageNumberPosition.BOTTOM_LEFT
            else:
                return PageNumberPosition.BOTTOM_CENTER
        else:  
            if x_center > 0.7:
                return PageNumberPosition.TOP_RIGHT
            elif x_center < 0.3:
                return PageNumberPosition.TOP_LEFT
            else:
                return PageNumberPosition.TOP_CENTER
    
    def _validate_page_number_sequence(self, slides: List[Slide]) -> None:
        """Проверяет последовательность номеров страниц"""
        numbered_slides = [s for s in slides if s.detected_page_number]
        
        if len(numbered_slides) < 2:
            return
        
        
        try:
            arabic_numbers = []
            for slide in numbered_slides:
                numbers = re.findall(r'\d+', slide.detected_page_number)
                if numbers:
                    arabic_numbers.append(int(numbers[0]))
            
            if len(arabic_numbers) >= 2:
                expected_sequence = list(range(min(arabic_numbers), max(arabic_numbers) + 1))
                if arabic_numbers != expected_sequence:
                    print(f"Предупреждение: непоследовательная нумерация страниц: {arabic_numbers}")
        
        except (ValueError, IndexError):
            pass
    
    def get_page_number_statistics(self, slides: List[Slide]) -> Dict[str, Any]:
        """Возвращает статистику по номерам страниц"""
        numbered_slides = [s for s in slides if s.detected_page_number]
        total_slides = len(slides)
        
        position_counts = {}
        for position in PageNumberPosition:
            position_counts[position.value] = 0
        
        for slide in numbered_slides:
            position_counts[slide.page_number_position.value] += 1
        
        formats = {}
        for slide in numbered_slides:
            format_type = self._classify_page_number_format(slide.detected_page_number)
            formats[format_type] = formats.get(format_type, 0) + 1
        
        return {
            "total_slides": total_slides,
            "slides_with_page_numbers": len(numbered_slides),
            "coverage_percentage": (len(numbered_slides) / total_slides * 100) if total_slides > 0 else 0,
            "position_distribution": position_counts,
            "format_distribution": formats,
        }
    
    def _classify_page_number_format(self, page_number: str) -> str:
        """Классифицирует формат номера страницы"""
        clean_text = page_number.strip()
        
        if re.match(r'^\d+$', clean_text):
            return "simple_number"
        elif re.match(r'^\d+[/\\\-]\d+$', clean_text):
            return "fraction"
        elif re.match(r'^\d+\s+из\s+\d+$', clean_text):
            return "x_of_y"
        elif re.match(r'^[\(\[]\d+[\)\]]$', clean_text):
            return "brackets"
        elif re.match(r'^\d+\.$', clean_text):
            return "with_dot"
        else:
            return "other"