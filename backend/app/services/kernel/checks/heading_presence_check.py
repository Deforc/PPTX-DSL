from app.services.kernel.base_checks import SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Slide
from typing import Dict, Any, Union, List


class HeadingPresenceCheck(SlideCheck):
    """Проверка наличия заголовка на слайде"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        required = self.params.get('required', True)
        
        if not required:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: заголовок не требуется"
            )
        
        has_heading = self._detect_heading(slide)
        
        if not has_heading:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: отсутствует заголовок"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: заголовок присутствует"
        )
    
    def _detect_heading(self, slide: Slide) -> bool:
        """Определяет наличие заголовка на основе размера шрифта и позиции"""
        if not slide.blocks:
            return False
        
        first_block = slide.blocks[0]
        if not first_block.runs:
            return False
        
        avg_font_size = sum(run.font_size for run in first_block.runs if run.font_size) / len(first_block.runs)
        
        other_blocks_sizes = []
        for block in slide.blocks[1:]:
            for run in block.runs:
                if run.font_size:
                    other_blocks_sizes.append(run.font_size)
        
        if not other_blocks_sizes:
            return True
        
        avg_other_size = sum(other_blocks_sizes) / len(other_blocks_sizes)
        
        return avg_font_size > avg_other_size * 1.2

