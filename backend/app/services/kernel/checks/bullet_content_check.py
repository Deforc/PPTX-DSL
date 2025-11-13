from typing import List, Dict, Any
from app.services.kernel.base_checks import PresentationCheck, SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Presentation, Slide, Paragraph

class BulletConsistencyCheck(SlideCheck):
    
    def validate(self, slide: Slide) -> ValidationResult:
        check_parallelism = self.params.get('check_parallelism', True)
        check_punctuation = self.params.get('check_punctuation', True)
        
        bullet_paragraphs = [block for block in slide.blocks if block.list_type.value != 'none']
        
        if not bullet_paragraphs:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: маркированные списки отсутствуют"
            )
        
        issues = []
        
        if check_parallelism:
            parallelism_issues = self._check_parallelism(bullet_paragraphs)
            issues.extend(parallelism_issues)
        
        if check_punctuation:
            punctuation_issues = self._check_punctuation(bullet_paragraphs)
            issues.extend(punctuation_issues)
        
        if issues:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: {'; '.join(issues[:3])}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: маркированные списки согласованы"
        )
    
    def _check_parallelism(self, bullet_paragraphs: List[Paragraph]) -> List[str]:
      
        issues = []
        first_words = []
        
        for paragraph in bullet_paragraphs:
            first_word = paragraph.text.split()[0] if paragraph.text.split() else ""
            first_words.append(first_word.lower())
        
        unique_first_words = set(first_words)
        if len(unique_first_words) > 1:
            issues.append("пункты списка начинаются с разных слов")
        
        return issues
    
    def _check_punctuation(self, bullet_paragraphs: List[Paragraph]) -> List[str]:
        issues = []
        endings = []
        
        for paragraph in bullet_paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue
            
            last_char = text[-1]
            endings.append(last_char)
        if "." in endings:
            issues.append("списки не должны оканчиваться точкой")
        if "," in endings:
            issues.append("списки не должны оканчиваться запятой")
        if ";" in endings:
            issues.append("списки не должны оканчиваться точкой с запятой")
        return issues
