from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import chat, conversations, models, pages
from app.core.config import STATIC_DIR
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # buat tabel jika belum ada, dijalankan sekali saat server start
    yield


app = FastAPI(title="Multi-Model Chat AI", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

for module in (pages, models, conversations, chat):
    app.include_router(module.router)