import uuid
import shutil
from pathlib import Path
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
import tempfile

from app.domain.entities import Presentation
from app.services.pdf.pdf_processing import PdfProcessingService

class FileService:
    def __init__(self):
        self.processing_service = PdfProcessingService()
    
    def process_uploaded_files(self, pdf_file: UploadFile, yaml_file: UploadFile) -> Dict[str, Any]:
        """Обрабатывает PDF с применением YAML правил и возвращает результат"""
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as pdf_temp:
            pdf_content = pdf_file.file.read()
            pdf_temp.write(pdf_content)
            pdf_temp_path = pdf_temp.name
        
        try:
            yaml_content = yaml_file.file.read().decode('utf-8')
            

            ## Место для парсера DSL
            presentation: Presentation = self.processing_service.process_pdf(Path(pdf_temp_path))
            
            validation_result = self._validate_presentation(presentation, None)
            
            return {
                "presentation": presentation,
                "validation_result": validation_result,
                "pdf_filename": pdf_file.filename,
                "yaml_filename": yaml_file.filename
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")
        finally:
            Path(pdf_temp_path).unlink(missing_ok=True)
    
    def _validate_presentation(self, presentation: Presentation, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Применяет правила валидации к презентации"""
        logs = []
        errors = 0
        warnings = 0
        infos = 0
        
        logs.append("[INFO] Начата проверка презентации...")
        logs.append(f"[INFO] Загружена презентация: {presentation.file_path.name}")
        logs.append(f"[INFO] Обработано слайдов: {len(presentation.slides)}")
        infos += 3
        
        fonts_analysis = self._analyze_fonts(presentation)
        logs.append(f"[INFO] Обнаружено шрифтов: {fonts_analysis['total_unique_fonts']}")
        infos += 1
        if fonts_analysis['total_unique_fonts'] > 1 :
            errors+=1
            logs.append(f"[ERROR]Шрифтов больше, чем требуется ")

        min_coverage = len(presentation.slides)
        slides_with_page_numbers = sum(1 for slide in presentation.slides if slide.detected_page_number)
        coverage = slides_with_page_numbers / len(presentation.slides) if presentation.slides else 0
        
        if coverage < min_coverage:
            logs.append(f"[WARN] Только {slides_with_page_numbers}/{len(presentation.slides)} слайдов имеют номера страниц (покрытие: {coverage:.1%})")
            warnings += 1
        else:
            logs.append(f"[INFO] Покрытие номеров страниц: {coverage:.1%} ({slides_with_page_numbers}/{len(presentation.slides)})")
            infos += 1
        
        
        layout_analysis = self._analyze_layouts(presentation)
        logs.append(f"[INFO] Распределение layout: {layout_analysis}")
        infos += 1
        
        logs.append(f"[INFO] Проверка завершена. Обнаружено: {errors} ошибок, {warnings} предупреждений.")
        infos += 1
        
        return {
            "logs": logs,
            "summary": {
                "total_logs": len(logs),
                "errors": errors,
                "warnings": warnings,
                "infos": infos
            },
            "detailed_analysis": {
                "total_slides": len(presentation.slides),
                "slides_with_page_numbers": slides_with_page_numbers,
                "page_number_coverage": coverage,
                "fonts_analysis": fonts_analysis,
                "layout_analysis": layout_analysis
            }
        }
    
    def _count_fonts_on_slide(self, slide) -> int:
        """Считает количество уникальных шрифтов на слайде"""
        fonts = set()
        for block in slide.blocks:
            for run in block.runs:
                if run.font_family:
                    fonts.add(run.font_family)
        return len(fonts)
    
    def _analyze_fonts(self, presentation: Presentation) -> Dict[str, Any]:
        """Анализирует использование шрифтов"""
        all_fonts = set()
        font_usage = {}
        
        for slide in presentation.slides:
            for block in slide.blocks:
                for run in block.runs:
                    if run.font_family:
                        all_fonts.add(run.font_family)
                        font_usage[run.font_family] = font_usage.get(run.font_family, 0) + 1
        
        return {
            "unique_fonts": list(all_fonts),
            "total_unique_fonts": len(all_fonts),
            "font_usage": font_usage
        }
    
    def _analyze_layouts(self, presentation: Presentation) -> Dict[str, int]:
        """Анализирует layout слайдов"""
        layouts = {}
        for i, slide in enumerate(presentation.slides, 1):
            layout_type = self._detect_slide_layout(slide)
            layouts[layout_type] = layouts.get(layout_type, 0) + 1
        
        return layouts
    
    def _detect_slide_layout(self, slide) -> str:
        """Определяет тип layout слайда"""
        if not slide.blocks:
            return "blank"
        
        total_text_length = sum(len(block.text) for block in slide.blocks)
        
        if len(slide.blocks) == 1 and total_text_length < 100:
            return "title"
        elif len(slide.blocks) <= 3 and total_text_length < 300:
            return "content"
        elif len(slide.blocks) <= 5:
            return "detailed"
        else:
            return "complex"