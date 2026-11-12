from fastapi import APIRouter

from app.core.config import MODEL_INFO, MODELS

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/model-info")
def model_info():
    """Daftar model beserta penjelasannya. Model tanpa info tetap dikembalikan."""
    return [
        {"name": name, "hint": "", "desc": "", **MODEL_INFO.get(name, {})}
        for name in MODELS
    ]