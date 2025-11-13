from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    status: ProcessingStatus
    message: str
    upload_time: datetime

class ProcessingResponse(BaseModel):
    file_id: str
    filename: str
    status: ProcessingStatus
    slides_count: int = 0
    processing_time: Optional[float] = None
    page_number_analysis: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime

class SlideInfo(BaseModel):
    slide_number: int
    title: str
    blocks_count: int
    has_page_number: bool
    page_number_position: Optional[str] = None
    layout: str

class PresentationDetailResponse(BaseModel):
    file_id: str
    filename: str
    slides: List[SlideInfo]
    total_slides: int
    slides_with_page_numbers: int
    page_number_coverage: float
    processing_time: float
    created_at: datetime

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    file_id: Optional[str] = None
