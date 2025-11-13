from app.services.kernel.base_checks import PresentationCheck, SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Presentation, Slide
from typing import List, Optional, Union

class SlideNumbersPresentationCheck(PresentationCheck):
    """Проверка наличия и корректности номеров слайдов в презентации"""
    
    def validate(self, presentation: Presentation) -> ValidationResult:
        """Проверяет общее наличие и корректность номеров слайдов в презентации"""
        slides_with_numbers = []
        slides_without_numbers = []
        
        for slide in presentation.slides:
            if slide.detected_page_number:
                slides_with_numbers.append(slide.page_number)
            else:
                slides_without_numbers.append(slide.page_number)
        
        total_slides = len(presentation.slides)
        slides_with_numbers_count = len(slides_with_numbers)
        
        min_coverage = self.params.get('min_coverage', default = 1)
        actual_coverage = slides_with_numbers_count / total_slides if total_slides > 0 else 0
        
        if actual_coverage < min_coverage:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=(
                    f"Низкое покрытие номеров страниц: {actual_coverage:.1%} "
                    f"({slides_with_numbers_count}/{total_slides} слайдов). "
                    f"Требуется минимум {min_coverage:.0%}"
                )
            )
        
        sequence_issues = self._check_number_sequence(slides_with_numbers, presentation.slides)
        
        if sequence_issues:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=sequence_issues
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=(
                f"Покрытие номеров страниц: {actual_coverage:.1%} "
                f"({slides_with_numbers_count}/{total_slides} слайдов). "
                "Последовательность корректна"
            )
        )
    
    def _check_number_sequence(self, numbered_slide_indices: List[int], all_slides: List[Slide]) -> Optional[str]:
        """Проверяет корректность последовательности номеров слайдов"""
        if len(numbered_slide_indices) < 2:
            return None  
        actual_numbers = []
        for slide_num in numbered_slide_indices:
            slide = next((s for s in all_slides if s.page_number == slide_num), None)
            if slide and slide.detected_page_number:
                parsed_number = self._parse_page_number(slide.detected_page_number)
                if parsed_number is not None:
                    actual_numbers.append((slide_num, parsed_number))
        
        if len(actual_numbers) < 2:
            return None
        issues = []
        arabic_numbers = [(slide_num, num) for slide_num, num in actual_numbers if isinstance(num, int)]
        if len(arabic_numbers) >= 2:
            arabic_issue = self._check_arabic_sequence(arabic_numbers)
            if arabic_issue:
                issues.append(arabic_issue)
        
        roman_numbers = [(slide_num, num) for slide_num, num in actual_numbers if isinstance(num, str)]
        if len(roman_numbers) >= 2:
            roman_issue = self._check_roman_sequence(roman_numbers)
            if roman_issue:
                issues.append(roman_issue)
        
        return "; ".join(issues) if issues else None
    
    def _check_arabic_sequence(self, numbers: List[tuple]) -> Optional[str]:
        """Проверяет последовательность арабских цифр"""
        slide_nums = [item[0] for item in numbers]
        page_nums = [item[1] for item in numbers]
        
        if not all(page_nums[i] < page_nums[i+1] for i in range(len(page_nums)-1)):
            return "Номера страниц не образуют возрастающую последовательность"
        
        max_gap = self.params.get('max_gap', 5)
        for i in range(len(page_nums)-1):
            gap = page_nums[i+1] - page_nums[i]
            if gap > max_gap:
                return f"Большой разрыв в нумерации: между {page_nums[i]} и {page_nums[i+1]}"
        
        return None
     
    def _parse_page_number(self, page_number_text: str) -> Optional[Union[int, str]]:
        """Парсит текст номера страницы в число или римскую цифру"""
        import re
        
        text = page_number_text.strip()
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        fraction_match = re.match(r'^\s*(\d+)\s*[/\\\-]\s*\d+\s*$', text)
        if fraction_match:
            return int(fraction_match.group(1))
        
        of_match = re.match(r'^\s*(\d+)\s+из\s+\d+\s*$', text, re.IGNORECASE)
        if of_match:
            return int(of_match.group(1))
        
        return None
    
    

class SlideNumbersSlideCheck(SlideCheck):
    """Проверка наличия номера на конкретном слайде"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        """Проверяет наличие и корректность номера на конкретном слайде"""
        required = self.params.get('required', True)
        
        if not required:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: номер страницы не требуется"
            )
        
        if not slide.detected_page_number:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: отсутствует номер страницы"
            )
        
        parsed_number = self._parse_page_number(slide.detected_page_number)
        
        if parsed_number is None:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: некорректный формат номера '{slide.detected_page_number}'"
            )
        
        position_ok = self._check_position(slide)
        if not position_ok:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: номер в нестандартной позиции"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: номер '{slide.detected_page_number}' корректен"
        )
    
    def _parse_page_number(self, page_number_text: str) -> Optional[Union[int, str]]:
        """Парсит текст номера страницы"""
        import re
        
        text = page_number_text.strip()
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        fraction_match = re.match(r'^\s*(\d+)\s*[/\\\-]\s*\d+\s*$', text)
        if fraction_match:
            return int(fraction_match.group(1))
        
        of_match = re.match(r'^\s*(\d+)\s+из\s+\d+\s*$', text, re.IGNORECASE)
        if of_match:
            return int(of_match.group(1))
        
        return None
    
    def _check_position(self, slide: Slide) -> bool:
        """Проверяет, что номер находится в стандартной позиции"""
        if not slide.page_number_position:
            return False
        
        standard_positions = {
            'bottom_right', 'bottom_center', 'bottom_left',
            'top_right', 'top_center', 'top_left', 'corner'
        }
        
        return slide.page_number_position.value in standard_positions