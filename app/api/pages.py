from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.core.config import STATIC_DIR

router = APIRouter(tags=["pages"])


@router.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")