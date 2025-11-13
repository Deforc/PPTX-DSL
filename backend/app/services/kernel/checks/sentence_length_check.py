import re
from app.services.kernel.base_checks import SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Slide
from typing import Dict, Any, List

class SentenceLengthCheck(SlideCheck):
    
    def validate(self, slide: Slide) -> ValidationResult:
        max_length = self.params.get('max')
        unit = self.params.get('unit', 'words')
        
        slide_text = ' '.join(block.text for block in slide.blocks)
        
        sentences = re.split(r'[.!?]+', slide_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: нет текста для проверки"
            )
        
        long_sentences = []
        
        for sentence in sentences:
            if unit == 'words':
                length = len(sentence.split())
                unit_name = "слов"
            else:
                length = len(sentence)
                unit_name = "символов"
            
            if max_length is not None and length > max_length:
                preview = sentence[:50] + "..." if len(sentence) > 50 else sentence
                long_sentences.append((length, preview))
        
        if long_sentences:
            first_long = long_sentences[0]
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: найдено {len(long_sentences)} длинных предложений. "
                        f"Пример: {first_long[1]} ({first_long[0]} {unit_name}, макс. {max_length})"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: все предложения в пределах нормы"
        )
