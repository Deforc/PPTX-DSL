from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, FileResponse

from app.core.config import get_settings
from app.services.pdf.file_service import FileService
from typing import List, Optional
import os
import json
from app.domain.entities import Slide

from app.web.models.models import (
    UploadResponse,
    ProcessingResponse,
    PresentationDetailResponse,
    SlideInfo,
    ErrorResponse,
    ProcessingStatus
)


router = APIRouter()
file_service = FileService()


@router.get("/healthz", summary="Проверка на то, насколько жив сервис")
def heallthz() -> dict:
    return {"status": "ok"}


@router.get("/version", summary="Версия и окружение")
def version() -> dict:
    s = get_settings()
    return {
        "name": s.APP_NAME,
        "version": s.APP_VERSION,
        "env": s.ENV,
    }
# async def upload_pdf(
#     background_tasks: BackgroundTasks,
#     file: UploadFile = File(..., description="PDF файл для обработки")
# ):
#     """
#     Загрузка PDF файла для обработки
    
#     - **file**: PDF файл для анализа презентации
#     """
#     # Проверяем тип файла
#     if not file.filename or not file.filename.lower().endswith('.pdf'):
#         raise HTTPException(
#             status_code=400,
#             detail="Файл должен быть в формате PDF"
#         )
    
#     try:
#         # Сохраняем файл
#         file_id = file_service.save_uploaded_file(file)
        
#         # Запускаем обработку в фоне
#         background_tasks.add_task(file_service.process_file, file_id)
        
#         return UploadResponse(
#             file_id=file_id,
#             filename=file.filename,
#             status=ProcessingStatus.PENDING,
#             message="Файл успешно загружен и поставлен в очередь на обработку",
#             upload_time=file_service.processing_status[file_id]["created_at"]
#         )
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Ошибка при загрузке файла: {str(e)}"
#         )

# @router.get(
#     "/status/{file_id}",
#     response_model=ProcessingResponse,
#     responses={404: {"model": ErrorResponse}}
# )
# async def get_processing_status(file_id: str):
#     """
#     Получение статуса обработки PDF файла
    
#     - **file_id**: ID файла полученный при загрузке
#     """
#     try:
#         status = file_service.get_status(file_id)
        
#         # Подготавливаем данные для ответа
#         response_data = {
#             "file_id": file_id,
#             "filename": status["filename"],
#             "status": status["status"],
#             "created_at": status["created_at"]
#         }
        
#         if status["status"] == ProcessingStatus.COMPLETED:
#             result = status.get("result", {})
#             response_data.update({
#                 "slides_count": result.get("slides_count", 0),
#                 "processing_time": status.get("processing_time"),
#                 "page_number_analysis": result.get("page_number_analysis")
#             })
#         elif status["status"] == ProcessingStatus.FAILED:
#             response_data["error_message"] = status.get("error_message")
        
#         return ProcessingResponse(**response_data)
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Ошибка при получении статуса: {str(e)}"
#         )

# @router.get(
#     "/result/{file_id}",
#     response_model=PresentationDetailResponse,
#     responses={
#         404: {"model": ErrorResponse},
#         400: {"model": ErrorResponse}
#     }
# )
# async def get_processing_result(file_id: str):
#     """
#     Получение результатов обработки PDF файла
    
#     - **file_id**: ID файла полученный при загрузке
#     """
#     try:
#         result = file_service.get_result(file_id)
#         presentation = result["presentation"]
#         status = file_service.get_status(file_id)
        
#         # Формируем информацию о слайдах
#         slides_info = []
#         for slide in presentation.slides:
#             slides_info.append(
#                 SlideInfo(
#                     slide_number=slide.page_number,
#                     title=slide._extract_slide_title(slide),
#                     blocks_count=len(slide.blocks),
#                     has_page_number=slide.detected_page_number is not None,
#                     page_number_position=slide.page_number_position.value if slide.detected_page_number else None,
#                     layout=slide._detect_slide_layout(slide)
#                 )
#             )
        
#         # Анализ номеров страниц
#         page_number_analysis = result.get("page_number_analysis", {})
#         slides_with_page_numbers = page_number_analysis.get("slides_with_page_numbers", 0)
#         total_slides = len(presentation.slides)
        
#         return PresentationDetailResponse(
#             file_id=file_id,
#             filename=status["filename"],
#             slides=slides_info,
#             total_slides=total_slides,
#             slides_with_page_numbers=slides_with_page_numbers,
#             page_number_coverage=(
#                 (slides_with_page_numbers / total_slides * 100) 
#                 if total_slides > 0 else 0
#             ),
#             processing_time=result["processing_time"],
#             created_at=status["created_at"]
#         )
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Ошибка при получении результатов: {str(e)}"
#         )

# @router.get(
#     "/result/{file_id}/detailed",
#     responses={
#         404: {"model": ErrorResponse},
#         400: {"model": ErrorResponse}
#     }
# )
# async def get_detailed_result(file_id: str):
#     """
#     Получение детальных результатов обработки (полные данные)
    
#     - **file_id**: ID файла полученный при загрузке
#     """
#     try:
#         result = file_service.get_result(file_id)
        
#         # Конвертируем презентацию в словарь для JSON
#         presentation_dict = self._presentation_to_dict(result["presentation"])
        
#         return {
#             "file_id": file_id,
#             "processing_time": result["processing_time"],
#             "page_number_analysis": result["page_number_analysis"],
#             "presentation": presentation_dict
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Ошибка при получении детальных результатов: {str(e)}"
#         )

# @router.get("/files", response_model=List[ProcessingResponse])
# async def list_uploaded_files(
#     status: Optional[ProcessingStatus] = Query(None, description="Фильтр по статусу")
# ):
#     """
#     Получение списка всех загруженных файлов
    
#     - **status**: Опциональный фильтр по статусу обработки
#     """
#     try:
#         files_list = []
        
#         for file_id, status_data in file_service.processing_status.items():
#             if status and status_data["status"] != status:
#                 continue
                
#             files_list.append(
#                 ProcessingResponse(
#                     file_id=file_id,
#                     filename=status_data["filename"],
#                     status=status_data["status"],
#                     created_at=status_data["created_at"]
#                 )
#             )
        
#         return files_list
    
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Ошибка при получении списка файлов: {str(e)}"
#         )

# @router.delete("/{file_id}",
#     responses={
#         404: {"model": ErrorResponse},
#         200: {"model": {"message": str}}
#     }
# )
# async def delete_file(file_id: str):
#     """
#     Удаление файла и его данных
    
#     - **file_id**: ID файла для удаления
#     """
#     try:
#         if file_id not in file_service.processing_status:
#             raise HTTPException(status_code=404, detail="Файл не найден")
        
#         status = file_service.processing_status[file_id]
#         if status["file_path"].exists():
#             status["file_path"].unlink()
        
#         # Удаляем из статусов
#         del file_service.processing_status[file_id]
        
#         return {"message": f"Файл {file_id} успешно удален"}
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Ошибка при удалении файла: {str(e)}"
#         )

# # Вспомогательные методы
# def _extract_slide_title(self, slide: Slide) -> str:
#     """Извлекает заголовок слайда"""
#     if not slide.blocks:
#         return "Без заголовка"
    
#     # Берем первый блок как заголовок (упрощенная логика)
#     first_block = slide.blocks[0]
#     if first_block.text and len(first_block.text) < 100:  # Заголовки обычно короткие
#         return first_block.text[:50] + "..." if len(first_block.text) > 50 else first_block.text
    
#     return "Без заголовка"

# def _detect_slide_layout(slide: Slide) -> str:
#     """Определяет layout слайда"""
#     if not slide.blocks:
#         return "blank"
    
#     # Упрощенная логика определения layout
#     blocks_count = len(slide.blocks)
#     if blocks_count == 1 and len(slide.blocks[0].text) < 100:
#         return "title"
#     elif blocks_count <= 3:
#         return "content"
#     else:
#         return "detailed"

# def _presentation_to_dict(presentation):
#     """Конвертирует презентацию в словарь для JSON"""
#     # Это упрощенная реализация, можно добавить более детальную конвертацию
#     return {
#         "file_path": str(presentation.file_path),
#         "slides_count": len(presentation.slides),
#         "metadata": presentation.metadata,
#         "fonts_used": presentation.fonts_used
#     }
