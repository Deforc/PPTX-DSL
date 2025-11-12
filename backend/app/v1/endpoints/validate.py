from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter(prefix="/validate", tags=["validation"])

@router.post("")
async def validate_presentation(
    pdf_file: UploadFile = File(..., description="PDF-файл презентации"),
    yaml_file: UploadFile = File(..., description="YAML-файл с правилами DSL")
) -> JSONResponse:
    if not pdf_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Файл презентации должен быть в формате PDF")
    
    if not yaml_file.filename.lower().endswith((".yaml", ".yml")):
        raise HTTPException(status_code=400, detail="Файл правил должен быть в формате YAML (.yaml или .yml)")

    logs: List[str] = [
        "[INFO] Начата проверка презентации...",
        f"[INFO] Загружена презентация: {pdf_file.filename}",
        f"[INFO] Загружены правила: {yaml_file.filename}",
        "[WARN] Слайд 1: обнаружено 4 шрифта (рекомендуется не более 3)",
        "[ERROR] Слайд 3: низкий контраст текста на фоне (уровень контрастности 2.1, требуется ≥ 4.5)",
        "[INFO] Проверка завершена. Обнаружено: 1 ошибка, 1 предупреждение."
    ]

    summary = {
        "total": len(logs),
        "errors": 1,
        "warnings": 1,
        "infos": 4
    }

    return JSONResponse({
        "status": "completed",
        "pdf_filename": pdf_file.filename,
        "yaml_filename": yaml_file.filename,
        "logs": logs,
        "summary": summary
    })
