from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import chat, conversations, model_info, models, pages, uploads
from app.core.config import STATIC_DIR
from app.core.logging_config import setup_logging
from app.db.session import init_db

setup_logging()  # harus dipanggil sebelum logger dipakai


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # buat tabel jika belum ada, dijalankan sekali saat server start
    yield


app = FastAPI(title="Multi-Model Chat AI", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

for module in (pages, models, model_info, conversations, chat, uploads):
    app.include_router(module.router)