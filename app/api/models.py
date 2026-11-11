from fastapi import APIRouter

from app.core.config import MODELS

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models")
def list_models() -> list[str]:
    return list(MODELS.keys())