from app.services.kernel.base_checks import PresentationCheck, SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Presentation, Slide
from typing import Dict, Any, Union, List


class FontSizesCountPresentationCheck(PresentationCheck):
    """Проверка количества различных размеров шрифтов в презентации"""
    
    def validate(self, presentation: Presentation) -> ValidationResult:
        font_sizes = set()
        for slide in presentation.slides:
            for block in slide.blocks:
                for run in block.runs:
                    if run.font_size:
                        font_sizes.add(run.font_size)
        
        sizes_count = len(font_sizes)
        max_sizes = self.params.get('max')
        
        if max_sizes is not None and sizes_count > max_sizes:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Используется {sizes_count} размеров шрифтов, максимум допустимо {max_sizes}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Количество размеров шрифтов {sizes_count} в допустимых пределах"
        )


class FontSizesCountSlideCheck(SlideCheck):
    """Проверка количества различных размеров шрифтов на слайде"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        font_sizes = set()
        for block in slide.blocks:
            for run in block.runs:
                if run.font_size:
                    font_sizes.add(run.font_size)
        
        sizes_count = len(font_sizes)
        max_sizes = self.params.get('max')
        
        if max_sizes is not None and sizes_count > max_sizes:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: используется {sizes_count} размеров шрифтов, максимум {max_sizes}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: количество размеров шрифтов {sizes_count} в норме"
        )

