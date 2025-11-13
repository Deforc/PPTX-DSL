from abc import ABC, abstractmethod
from typing import Dict, Any, Union, List, Set
from app.domain.entities import Presentation, Slide
from app.services.kernel.validation_result import ValidationResult

class PresentationCheck(ABC):
    def __init__(self, rule_name: str, params: Dict[str, Any], severity: str):
        self.rule_name = rule_name
        self.params = params
        self.severity = severity
    
    @abstractmethod
    def validate(self, presentation: Presentation) -> ValidationResult:
        pass

class SlideCheck(ABC):
    def __init__(self, rule_name: str, params: Dict[str, Any], severity: str, scope: Union[str, List[int]]):
        self.rule_name = rule_name
        self.params = params
        self.severity = severity
        self.scope: Union[str, Set[int]] = scope if scope == 'all' else set(scope)
    
    def applies_to_slide(self, slide_number: int) -> bool:
        return self.scope == 'all' or slide_number in self.scope
    
    @abstractmethod
    def validate(self, slide: Slide) -> ValidationResult:
        pass
