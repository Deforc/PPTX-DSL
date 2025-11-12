from app.services.kernel.base_checks import PresentationCheck, SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Presentation, Slide
from typing import Dict, Any, Union, List


class FontCountPresentationCheck(PresentationCheck):
    """Проверка количества различных шрифтов в презентации"""
    
    def validate(self, presentation: Presentation) -> ValidationResult:
        fonts = set()
        for slide in presentation.slides:
            for block in slide.blocks:
                for run in block.runs:
                    if run.font_family:
                        fonts.add(run.font_family)
        
        font_count = len(fonts)
        max_fonts = self.params.get('max')
        
        if max_fonts is not None and font_count > max_fonts:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Используется {font_count} шрифтов, максимум допустимо {max_fonts}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Количество шрифтов {font_count} в допустимых пределах"
        )


class FontCountSlideCheck(SlideCheck):
    """Проверка количества различных шрифтов на слайде"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        fonts = set()
        for block in slide.blocks:
            for run in block.runs:
                if run.font_family:
                    fonts.add(run.font_family)
        
        font_count = len(fonts)
        max_fonts = self.params.get('max')
        
        if max_fonts is not None and font_count > max_fonts:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: используется {font_count} шрифтов, максимум {max_fonts}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: количество шрифтов {font_count} в норме"
        )

