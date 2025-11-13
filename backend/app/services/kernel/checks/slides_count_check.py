from app.services.kernel.base_checks import PresentationCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Presentation
from typing import Dict, Any


class SlidesCountCheck(PresentationCheck):
    """Проверка количества слайдов в презентации"""
    
    def validate(self, presentation: Presentation) -> ValidationResult:
        slides_count = len(presentation.slides)
        min_slides = self.params.get('min')
        max_slides = self.params.get('max')
        
        if min_slides is not None and slides_count < min_slides:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайдов {slides_count}, минимум требуется {min_slides}"
            )
        
        if max_slides is not None and slides_count > max_slides:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайдов {slides_count}, максимум допустимо {max_slides}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Количество слайдов {slides_count} в допустимых пределах"
        )
