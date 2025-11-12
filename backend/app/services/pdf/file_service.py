import uuid
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import UploadFile, HTTPException
import os

from app.domain.entities import Presentation
from app.services.pdf.pdf_processing import PdfProcessingService

class FileService:
    """Сервис для управления загруженными файлами"""
    
    def __init__(self, upload_dir: str = "uploads", processed_dir: str = "processed"):
        self.upload_dir = Path(upload_dir)
        self.processed_dir = Path(processed_dir)
        self.processing_service = PdfProcessingService()
        
        self.upload_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        self.processing_status: Dict[str, Dict[str, Any]] = {}
    
    def save_uploaded_file(self, file: UploadFile) -> str:
        """Сохраняет загруженный файл и возвращает file_id"""
        file_id = str(uuid.uuid4())
        
        original_filename = file.filename or "unknown.pdf"
        safe_filename = self._create_safe_filename(original_filename, file_id)
        file_path = self.upload_dir / safe_filename
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            self.processing_status[file_id] = {
                "file_id": file_id,
                "filename": original_filename,
                "file_path": file_path,
                "status": "pending",
                "created_at": datetime.now(),
                "error_message": None,
                "result": None
            }
            
            return file_id
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка сохранения файла: {str(e)}"
            )
    
    def process_file(self, file_id: str) -> Dict[str, Any]:
        """Обрабатывает PDF файл"""
        if file_id not in self.processing_status:
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        status = self.processing_status[file_id]
        status["status"] = "processing"
        
        try:
            start_time = datetime.now()
            presentation: Presentation = self.processing_service.process_pdf(status["file_path"])
            processing_time = (datetime.now() - start_time).total_seconds()
            
            page_number_analysis = self.processing_service.get_page_number_analysis(presentation)
            
            result = {
                "presentation": presentation,
                "processing_time": processing_time,
                "page_number_analysis": page_number_analysis,
                "slides_count": len(presentation.slides)
            }
            
            status.update({
                "status": "completed",
                "result": result,
                "processing_time": processing_time,
                "completed_at": datetime.now()
            })
            
            return result
            
        except Exception as e:
            status.update({
                "status": "failed",
                "error_message": str(e),
                "completed_at": datetime.now()
            })
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка обработки PDF: {str(e)}"
            )
    
    def get_status(self, file_id: str) -> Dict[str, Any]:
        """Возвращает статус обработки файла"""
        if file_id not in self.processing_status:
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        return self.processing_status[file_id]
    
    def get_result(self, file_id: str) -> Dict[str, Any]:
        """Возвращает результат обработки"""
        status = self.get_status(file_id)
        if status["status"] != "completed":
            raise HTTPException(
                status_code=400, 
                detail="Обработка еще не завершена"
            )
        
        return status["result"]
    
    def _create_safe_filename(self, original_filename: str, file_id: str) -> str:
        """Создает безопасное имя файла"""
        extension = Path(original_filename).suffix.lower()
        if extension not in ['.pdf']:
            extension = '.pdf'
        
        safe_name = original_filename.replace(' ', '_').replace('/', '_')
        return f"{file_id}_{safe_name}"
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Очищает старые файлы"""
        current_time = datetime.now()
        
        for file_id, status in list(self.processing_status.items()):
            file_age = (current_time - status["created_at"]).total_seconds() / 3600
            
            if file_age > max_age_hours:
                if status["file_path"].exists():
                    status["file_path"].unlink()
                del self.processing_status[file_id]