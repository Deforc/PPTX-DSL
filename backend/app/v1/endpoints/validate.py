from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/validate", tags=["validation"])
file_service = FileService()

@router.post("")
async def validate_presentation(
    pdf_file: UploadFile = File(..., description="PDF-файл презентации"),
    yaml_file: UploadFile = File(..., description="YAML-файл с правилами DSL")
) -> JSONResponse:
    if not pdf_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Файл презентации должен быть в формате PDF")
    
    if not yaml_file.filename.lower().endswith((".yaml", ".yml")):
        raise HTTPException(status_code=400, detail="Файл правил должен быть в формате YAML (.yaml или .yml)")

    result = file_service.process_uploaded_files(pdf_file, yaml_file)
    
    return JSONResponse({
        "status": "success" if result["success"] else "failed",
        "files": result["files"],
        "validation": result["validation"],
        "presentation": result["presentation"],
        "detailed_results": result["detailed_results"]
    })
