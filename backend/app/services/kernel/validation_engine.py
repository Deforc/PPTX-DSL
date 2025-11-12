from typing import List
from app.domain.entities import Presentation
from app.services.kernel.base_checks import PresentationCheck, SlideCheck
from app.services.kernel.validation_result import ValidationResult


class ValidationEngine:
    def __init__(self, presentation_checks: List[PresentationCheck] = None, 
                 slide_checks: List[SlideCheck] = None):
        self.presentation_checks = presentation_checks or []
        self.slide_checks = slide_checks or []
    
    def validate(self, presentation: Presentation) -> List[ValidationResult]:
        results = []
        
        # Presentation-level checks
        for check in self.presentation_checks:
            result = check.validate(presentation)
            results.append(result)
        
        # Slide-level checks
        for slide in presentation.slides:
            for check in self.slide_checks:
                if check.applies_to_slide(slide.page_number):
                    result = check.validate(slide)
                    results.append(result)
        
        return results

