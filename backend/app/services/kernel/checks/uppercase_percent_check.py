from app.services.kernel.base_checks import PresentationCheck, SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Presentation, Slide
from typing import Dict, Any


class UppercasePercentPresentationCheck(PresentationCheck):
    """Проверка процента заглавных букв в презентации"""
    
    def validate(self, presentation: Presentation) -> ValidationResult:
        max_percent = self.params.get('max')
        
        if max_percent is None:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message="Максимальный процент заглавных букв не указан"
            )
        
        all_text = presentation.get_all_text()
        
        if not all_text:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message="Нет текста для проверки"
            )
        
        # Считаем только буквы
        letters = [c for c in all_text if c.isalpha()]
        if not letters:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message="Нет букв для проверки"
            )
        
        uppercase_count = sum(1 for c in letters if c.isupper())
        percent = (uppercase_count / len(letters)) * 100
        
        if percent > max_percent:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Заглавных букв {percent:.1f}%, максимум {max_percent}%"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Процент заглавных букв {percent:.1f}% в норме"
        )


class UppercasePercentSlideCheck(SlideCheck):
    """Проверка процента заглавных букв на слайде"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        max_percent = self.params.get('max')
        
        if max_percent is None:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: максимальный процент заглавных букв не указан"
            )
        
        slide_text = ' '.join(block.text for block in slide.blocks)
        
        if not slide_text:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: нет текста для проверки"
            )
        
        # Считаем только буквы
        letters = [c for c in slide_text if c.isalpha()]
        if not letters:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: нет букв для проверки"
            )
        
        uppercase_count = sum(1 for c in letters if c.isupper())
        percent = (uppercase_count / len(letters)) * 100
        
        if percent > max_percent:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: заглавных букв {percent:.1f}%, максимум {max_percent}%"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: процент заглавных букв {percent:.1f}% в норме"
        )

