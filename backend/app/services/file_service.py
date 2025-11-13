import tempfile
from pathlib import Path
from typing import Dict, Any, List
from fastapi import UploadFile, HTTPException

from app.domain.entities import Presentation
from app.services.pdf.pdf_processing import PdfProcessingService
from app.services.dsl import load_validation_engine_from_string, DSLParseError
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity

class FileService:
    
    def __init__(self):
        self.pdf_processor = PdfProcessingService()
    
    def process_uploaded_files(self, pdf_file: UploadFile, yaml_file: UploadFile) -> Dict[str, Any]:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as pdf_temp:
            pdf_content = pdf_file.file.read()
            pdf_temp.write(pdf_content)
            pdf_temp_path = pdf_temp.name
        
        try:
            yaml_content = yaml_file.file.read().decode('utf-8')
            validation_engine = self._load_validation_rules(yaml_content)
            
            presentation = self.pdf_processor.process_pdf(Path(pdf_temp_path))
            
            validation_results = validation_engine.validate(presentation)
            
            result = self._format_results(
                presentation=presentation,
                validation_results=validation_results,
                pdf_filename=pdf_file.filename,
                yaml_filename=yaml_file.filename
            )
            
            return result
            
        except DSLParseError as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Ошибка парсинга правил валидации: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка обработки файлов: {str(e)}"
            )
        finally:
            Path(pdf_temp_path).unlink(missing_ok=True)
    
    def _load_validation_rules(self, yaml_content: str):
        return load_validation_engine_from_string(yaml_content)
    
    def _format_results(
        self,
        presentation: Presentation,
        validation_results: List[ValidationResult],
        pdf_filename: str,
        yaml_filename: str
    ) -> Dict[str, Any]:
        
        logs = []
        errors = 0
        warnings = 0
        infos = 0
        
        logs.append(f"[INFO] Начата проверка презентации '{pdf_filename}'")
        logs.append(f"[INFO] Применены правила из '{yaml_filename}'")
        logs.append(f"[INFO] Обработано слайдов: {len(presentation.slides)}")
        logs.append(f"[INFO] Применено проверок: {len(validation_results)}")
        infos += 4
        
        for result in validation_results:
            if result.status == ValidationStatus.PASSED:
                prefix = "[SUCCESS]"
            else:
                prefix = f"[{result.severity.value.upper()}]"
            
            log_message = f"{prefix} {result.rule_name}: {result.message}"
            logs.append(log_message)
            
            if result.status == ValidationStatus.FAILED:
                if result.severity == Severity.ERROR:
                    errors += 1
                elif result.severity == Severity.WARNING:
                    warnings += 1
                elif result.severity == Severity.INFO:
                    infos += 1
            
        passed_checks = sum(1 for r in validation_results if r.status == ValidationStatus.PASSED)
        failed_checks = sum(1 for r in validation_results if r.status == ValidationStatus.FAILED)
        
        logs.append(f"[INFO] Проверка завершена. Пройдено: {passed_checks}, провалено: {failed_checks}")
        logs.append(f"[INFO] Обнаружено: {errors} ошибок, {warnings} предупреждений, {infos} информационных сообщений")
        infos += 2
        
        presentation_analysis = self._analyze_presentation(presentation)
        
        return {
            "success": failed_checks == 0,
            "files": {
                "pdf_filename": pdf_filename,
                "yaml_filename": yaml_filename
            },
            "validation": {
                "total_checks": len(validation_results),
                "passed": passed_checks,
                "failed": failed_checks,
                "logs": logs,
                "summary": {
                    "errors": errors,
                    "warnings": warnings,
                    "infos": infos,
                    "total_logs": len(logs)
                }
            },
            "presentation": {
                "total_slides": len(presentation.slides),
                "analysis": presentation_analysis
            },
            "detailed_results": [
                {
                    "rule_name": result.rule_name,
                    "status": result.status.value,
                    "severity": result.severity.value,
                    "message": result.message
                }
                for result in validation_results
            ]
        }
    
    def _analyze_presentation(self, presentation: Presentation) -> Dict[str, Any]:
        
        all_fonts = set()
        font_usage = {}
        
        for slide in presentation.slides:
            for block in slide.blocks:
                for run in block.runs:
                    if run.font_family:
                        all_fonts.add(run.font_family)
                        font_usage[run.font_family] = font_usage.get(run.font_family, 0) + 1
        
        slides_with_page_numbers = sum(
            1 for slide in presentation.slides 
            if slide.detected_page_number is not None
        )
        page_number_coverage = (
            slides_with_page_numbers / len(presentation.slides) 
            if presentation.slides else 0
        )
        
        all_font_sizes = set()
        for slide in presentation.slides:
            for block in slide.blocks:
                for run in block.runs:
                    if run.font_size:
                        all_font_sizes.add(run.font_size)
        
        total_text_length = sum(
            sum(len(block.text) for block in slide.blocks)
            for slide in presentation.slides
        )
        avg_text_per_slide = (
            total_text_length / len(presentation.slides)
            if presentation.slides else 0
        )
        
        return {
            "fonts": {
                "unique_fonts": sorted(list(all_fonts)),
                "total_unique": len(all_fonts),
                "usage": font_usage
            },
            "font_sizes": {
                "unique_sizes": sorted(list(all_font_sizes)),
                "total_unique": len(all_font_sizes)
            },
            "page_numbers": {
                "slides_with_numbers": slides_with_page_numbers,
                "coverage": round(page_number_coverage * 100, 1),
                "coverage_percent": f"{page_number_coverage:.1%}"
            },
            "text": {
                "total_characters": total_text_length,
                "avg_per_slide": round(avg_text_per_slide, 1)
            }
        }
