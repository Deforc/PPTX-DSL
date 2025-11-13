import os
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pdf.pdf_processing import PdfProcessingService
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.v1.routers import router

def create_app() -> FastAPI:
    s = get_settings()
    setup_logging()

    app = FastAPI(
        title=s.APP_NAME,
        version=s.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    upload_dir: Path = s.upload_path
    os.makedirs(upload_dir, exist_ok=True)

    app.include_router(router, prefix=s.API_V1_PREFIX)
    return app

app = create_app()
