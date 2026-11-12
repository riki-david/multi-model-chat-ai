import logging

import litellm
from loguru import logger

from app.core.config import LOG_DIR, LOG_LEVEL, LOG_RETENTION_DAYS

LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | {level: <7} | {name}:{function}:{line} - {message}"
)


class InterceptHandler(logging.Handler):
    """Mengalihkan log dari logging bawaan Python (uvicorn, litellm, dll.) ke loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Timpa nama, fungsi, dan baris dengan milik record asli
        def _use_original_source(r):
            r["name"] = record.name
            r["function"] = record.funcName
            r["line"] = record.lineno

        (
            logger.patch(_use_original_source)
            .opt(exception=record.exc_info)
            .log(level, record.getMessage())
        )


def setup_logging() -> None:
    """Pasang log ke console dan file harian. Aman dipanggil lebih dari sekali."""
    if getattr(setup_logging, "_done", False):
        return
    setup_logging._done = True

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Matikan info debug LiteLLM ("LiteLLM completion() model=...")
    litellm.suppress_debug_info = True
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)

    logger.remove()

    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        enqueue=True,
    )

    logger.add(
        LOG_DIR / "app-{time:YYYY-MM-DD}.log",
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        rotation="00:00",
        retention=f"{LOG_RETENTION_DAYS} days",
        encoding="utf-8",
        enqueue=True,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "litellm", "LiteLLM"):
        lib_logger = logging.getLogger(name)
        lib_logger.handlers = [InterceptHandler()]
        lib_logger.propagate = False

    # Set ulang level LiteLLM setelah loop di atas, karena loop tidak mengubahnya
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)

     # Matikan log request GET dari browser (refresh halaman)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)