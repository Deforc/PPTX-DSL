from app.services.kernel.base_checks import SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Slide
from typing import Dict, Any

class ElementsCountCheck(SlideCheck):
    
    def validate(self, slide: Slide) -> ValidationResult:
        max_elements = self.params.get('max')
        
        if max_elements is None:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: максимальное количество элементов не указано"
            )
        
        elements_count = len(slide.blocks)
        
        if elements_count > max_elements:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: {elements_count} элементов, максимум {max_elements}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: количество элементов {elements_count} в норме"
        )
