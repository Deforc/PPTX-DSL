from app.services.kernel.base_checks import SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Slide, ListType
from typing import Dict, Any


class ListNestingCheck(SlideCheck):
    """Проверка уровня вложенности списков на слайде"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        max_level = self.params.get('max_level')
        
        # Находим максимальный уровень вложенности среди списков
        list_items = [block for block in slide.blocks if block.list_type != ListType.NONE]
        
        if not list_items:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: нет списков для проверки"
            )
        
        max_found_level = max(block.level for block in list_items)
        
        if max_level is not None and max_found_level > max_level:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: уровень вложенности {max_found_level}, максимум {max_level}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: уровень вложенности {max_found_level} в норме"
        )

