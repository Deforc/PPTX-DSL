from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.pdf.file_service import  FileService

router = APIRouter(prefix="/validate", tags=["validation"])
file_service = FileService()

@router.post("")
async def validate_presentation(
    pdf_file: UploadFile = File(..., description="PDF-файл презентации"),
    yaml_file: UploadFile = File(..., description="YAML-файл с правилами DSL")
) -> JSONResponse:
    """
    Валидация PDF презентации по правилам из YAML файла
    """
    if not pdf_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Файл презентации должен быть в формате PDF")
    
    if not yaml_file.filename.lower().endswith((".yaml", ".yml")):
        raise HTTPException(status_code=400, detail="Файл правил должен быть в формате YAML (.yaml или .yml)")

    try:
        result = file_service.process_uploaded_files(pdf_file, yaml_file)
        validation_result = result["validation_result"]
        
        return JSONResponse({
            "status": "completed",
            "pdf_filename": result["pdf_filename"],
            "yaml_filename": result["yaml_filename"],
            "logs": validation_result["logs"],
            "summary": validation_result["summary"],
            "detailed_analysis": validation_result["detailed_analysis"]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при обработке файлов: {str(e)}"
        )