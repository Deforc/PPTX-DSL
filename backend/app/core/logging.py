from __future__ import annotations

import logging

_LOG_FORMAT = "%(asctime)s %(levelname)s %(process)s %(name)s %(message)s"
def setup_logging(level: int = logging.INFO) -> None:
    """Единая настройка логирования для uvicorn и приложения."""
    # Базовый конфиг
    logging.basicConfig(level=level, format=_LOG_FORMAT)

    # Приводим uvicorn-логгеры к единому формату
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(name)
        for h in logger.handlers:
            h.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
