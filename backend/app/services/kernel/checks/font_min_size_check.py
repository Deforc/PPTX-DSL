from app.services.kernel.base_checks import PresentationCheck, SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Presentation, Slide
from typing import Dict, Any, List


class FontMinSizePresentationCheck(PresentationCheck):
    """Проверка минимального размера шрифта в презентации"""
    
    def validate(self, presentation: Presentation) -> ValidationResult:
        min_size = self.params.get('min')
        unit = self.params.get('unit', 'pt')  # pt или px
        
        if min_size is None:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message="Минимальный размер шрифта не указан"
            )
        
        # Собираем все размеры шрифтов
        small_fonts = []
        for slide in presentation.slides:
            for block in slide.blocks:
                for run in block.runs:
                    if run.font_size and run.font_size < min_size:
                        small_fonts.append((slide.page_number, run.font_size))
        
        if small_fonts:
            min_found = min(size for _, size in small_fonts)
            slides_affected = len(set(slide_num for slide_num, _ in small_fonts))
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Найдены шрифты меньше {min_size}{unit}: минимальный {min_found}{unit} на {slides_affected} слайдах"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Все шрифты не меньше {min_size}{unit}"
        )


class FontMinSizeSlideCheck(SlideCheck):
    """Проверка минимального размера шрифта на слайде"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        min_size = self.params.get('min')
        unit = self.params.get('unit', 'pt')  # pt или px
        
        if min_size is None:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: минимальный размер шрифта не указан"
            )
        
        # Собираем маленькие шрифты
        small_fonts = []
        for block in slide.blocks:
            for run in block.runs:
                if run.font_size and run.font_size < min_size:
                    small_fonts.append(run.font_size)
        
        if small_fonts:
            min_found = min(small_fonts)
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: найдены шрифты меньше {min_size}{unit}, минимальный {min_found}{unit}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: все шрифты не меньше {min_size}{unit}"
        )

