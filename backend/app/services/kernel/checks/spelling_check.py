import requests
from typing import Dict, Any, List
from app.services.kernel.base_checks import SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Slide

class SpellingCheck(SlideCheck):
    
    YANDEX_SPELLER_API = "https://speller.yandex.net/services/spellservice.json/checkText"
    
    def validate(self, slide: Slide) -> ValidationResult:
        enabled = self.params.get('enabled', True)
        
        if not enabled:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: проверка орфографии отключена"
            )
        
        slide_text = ' '.join(block.text for block in slide.blocks)
        
        if not slide_text.strip():
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: нет текста для проверки"
            )
        
        try:
            errors = self._check_spelling(slide_text)
            
            if errors:
                error_count = len(errors)
                preview_errors = errors[:3]
                
                error_examples = []
                for err in preview_errors:
                    word = err.get('word', '')
                    suggestions = err.get('s', [])
                    if suggestions:
                        suggestion_str = f" (возможно: {', '.join(suggestions[:2])})"
                    else:
                        suggestion_str = ""
                    error_examples.append(f"'{word}'{suggestion_str}")
                
                examples_str = ', '.join(error_examples)
                more_str = f" и еще {error_count - 3}" if error_count > 3 else ""
                
                return ValidationResult(
                    status=ValidationStatus.FAILED,
                    severity=Severity[self.severity.upper()],
                    rule_name=self.rule_name,
                    message=f"Слайд {slide.page_number}: найдено {error_count} орфографических ошибок: {examples_str}{more_str}"
                )
            
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: орфографических ошибок не найдено"
            )
            
        except Exception as e:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: не удалось проверить орфографию ({str(e)})"
            )
    
    def _check_spelling(self, text: str) -> List[Dict[str, Any]]:
        try:
            params = {
                'text': text,
                'options': 0
            }
            
            response = requests.get(
                self.YANDEX_SPELLER_API,
                params=params,
                timeout=5
            )
            
            response.raise_for_status()
            
            errors = response.json()
            
            return errors if isinstance(errors, list) else []
            
        except requests.exceptions.Timeout:
            raise Exception("Превышено время ожидания ответа от API")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка запроса к API: {str(e)}")
        except ValueError as e:
            raise Exception(f"Ошибка парсинга ответа API: {str(e)}")
