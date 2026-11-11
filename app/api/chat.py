import sqlite3

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from app.core.config import MAX_HISTORY, MAX_TOKENS, MODELS, SYSTEM_PROMPT
from app.db import chat_store
from app.schemas.chat import ChatIn
from app.services.llm import stream_answer

router = APIRouter(prefix="/api", tags=["chat"])
TEXT_PLAIN = "text/plain; charset=utf-8"


@router.post("/chat")
async def chat(body: ChatIn):
    if body.model not in MODELS:
        raise HTTPException(status_code=400, detail=f"Model '{body.model}' tidak dikenal")

    # Akses SQLite dijalankan di threadpool agar event loop tidak terblokir
    exists = await run_in_threadpool(chat_store.conversation_exists, body.conv_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan")

    history = await run_in_threadpool(chat_store.get_history, body.conv_id)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history[-MAX_HISTORY:],
        {"role": "user", "content": body.message},
    ]

    async def stream():
        parts: list[str] = []
        try:
            async for text in stream_answer(MODELS[body.model], messages, MAX_TOKENS):
                parts.append(text)
                yield text
        except Exception as e:
            msg = str(e).lower()
            if "rate" in msg or "quota" in msg or "429" in msg:
                yield "\n[Kuota model ini sudah habis hari ini. Coba model lain di dropdown.]"
            elif "503" in msg or "unavailable" in msg or "high demand" in msg:
                yield "\n[Server model sedang sibuk. Coba lagi beberapa saat.]"
            else:
                yield "\n[Terjadi gangguan saat menghubungi model. Coba lagi.]"
                print(f"LLM error: {e}")  # detail teknis tetap tercatat di terminal
            return

        answer = "".join(parts)
        if answer:
            try:
                await run_in_threadpool(
                    chat_store.save_turn, body.conv_id, body.message, answer, body.model
                )
            except sqlite3.Error:
                pass  # misal chat sudah dihapus saat streaming berjalan

    return StreamingResponse(stream(), media_type=TEXT_PLAIN)