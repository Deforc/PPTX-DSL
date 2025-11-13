from app.services.kernel.base_checks import PresentationCheck, SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Presentation, Slide, ListType
from typing import Dict, Any, Set


class ListConsistencyPresentationCheck(PresentationCheck):
    """Проверка единообразия использования списков в презентации"""
    
    def validate(self, presentation: Presentation) -> ValidationResult:
        same_type = self.params.get('same_type', True)
        
        if not same_type:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message="Проверка единообразия списков отключена"
            )
        
        # Собираем все типы списков
        list_types: Set[ListType] = set()
        for slide in presentation.slides:
            for block in slide.blocks:
                if block.list_type != ListType.NONE:
                    list_types.add(block.list_type)
        
        if len(list_types) == 0:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message="Нет списков для проверки"
            )
        
        if len(list_types) > 1:
            types_str = ', '.join(lt.value for lt in list_types)
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Используются разные типы списков: {types_str}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Все списки одного типа: {list(list_types)[0].value}"
        )


class ListConsistencySlideCheck(SlideCheck):
    """Проверка единообразия использования списков на слайде"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        same_type = self.params.get('same_type', True)
        
        if not same_type:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: проверка единообразия списков отключена"
            )
        
        # Собираем все типы списков на слайде
        list_types: Set[ListType] = set()
        for block in slide.blocks:
            if block.list_type != ListType.NONE:
                list_types.add(block.list_type)
        
        if len(list_types) == 0:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: нет списков для проверки"
            )
        
        if len(list_types) > 1:
            types_str = ', '.join(lt.value for lt in list_types)
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: используются разные типы списков: {types_str}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: все списки одного типа"
        )

