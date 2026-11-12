import sqlite3
import time

import litellm
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from starlette.concurrency import run_in_threadpool

from app.core.attachments import build_message_content
from app.core.config import MAX_HISTORY, MAX_TOKENS, MODELS
from app.core.prompts import build_system_prompt
from app.db import chat_store
from app.schemas.chat import ChatIn
from app.services.llm import stream_answer

router = APIRouter(prefix="/api", tags=["chat"])
TEXT_PLAIN = "text/plain; charset=utf-8"

# Aturan penanganan error, diurutkan dari yang paling spesifik.
# Format: (nama class di litellm, pesan untuk pengguna).
# Nama yang tidak ada di versi litellm yang terpasang akan dilewati otomatis.
ERROR_RULES = [
    ("AuthenticationError", "API key salah atau belum diisi. Cek file .env lalu restart server."),
    ("RateLimitError", "Kuota habis atau terlalu banyak request. Coba lagi nanti atau pilih model lain."),
    ("ServiceUnavailableError", "Server model sedang sibuk. Coba lagi beberapa saat."),
    ("ContextWindowExceededError", "Percakapan atau lampiran terlalu panjang untuk model ini. Kurangi isi atau mulai chat baru."),
    ("BadRequestError", "Permintaan ditolak penyedia model. Cek model yang dipilih atau ukuran lampiran."),
    ("APIError", "Gangguan dari penyedia model. Detail ada di log."),
]

# Kata kunci cadangan, untuk error yang tidak selalu punya class khusus (misalnya saldo 402)
CREDIT_KEYWORDS = ("402", "insufficient", "credit", "saldo")
CREDIT_MESSAGE = "Saldo atau kredit penyedia tidak cukup. Isi saldo atau kurangi MAX_TOKENS."
UNKNOWN_MESSAGE = "Terjadi gangguan saat menghubungi model. Coba lagi."

LOG_ERROR_MAX_CHARS = 300  # batas panjang pesan error di log (JSON dari penyedia bisa sangat panjang)


def _classify(e: Exception) -> tuple[str, bool]:
    """
    Mengembalikan (pesan_untuk_pengguna, dikenal).
    dikenal=True  : error yang sudah diketahui penyebabnya, cukup dicatat satu baris.
    dikenal=False : error tak terduga, dicatat dengan traceback lengkap.
    """
    text = str(e).lower()
    if any(k in text for k in CREDIT_KEYWORDS):
        return CREDIT_MESSAGE, True

    for class_name, message in ERROR_RULES:
        cls = getattr(litellm, class_name, None)
        if cls is not None and isinstance(e, cls):
            return message, True

    return UNKNOWN_MESSAGE, False


@router.post("/chat")
async def chat(body: ChatIn):
    if body.model not in MODELS:
        raise HTTPException(status_code=400, detail=f"Model '{body.model}' tidak dikenal")

    if not body.message.strip() and not body.attachments:
        raise HTTPException(status_code=400, detail="Pesan atau lampiran harus diisi")

    # Akses SQLite dijalankan di threadpool agar event loop tidak terblokir
    exists = await run_in_threadpool(chat_store.conversation_exists, body.conv_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan")

    history = await run_in_threadpool(chat_store.get_history, body.conv_id)

    # model_content: teks saja, atau list (teks + gambar) untuk model vision
    # saved_text   : teks saja, tanpa base64, untuk disimpan ke database
    model_content, saved_text = build_message_content(body.message, body.attachments)

    messages = [
        # Identitas diambil dari config, jadi model baru ikut otomatis tanpa ubah kode
        {"role": "system", "content": build_system_prompt(body.model, MODELS[body.model])},
        *history[-MAX_HISTORY:],
        {"role": "user", "content": model_content},
    ]

    async def stream():
        parts: list[str] = []
        started = time.perf_counter()

        # Catat metadata saja, bukan isi pesan, supaya percakapan tidak masuk log
        logger.info(
            "Chat mulai | conv={} | model={} | lampiran={}",
            body.conv_id, body.model, len(body.attachments),
        )

        try:
            async for text in stream_answer(MODELS[body.model], messages, MAX_TOKENS):
                parts.append(text)
                yield text
        except Exception as e:
            user_msg, known = _classify(e)
            if known:
                detail = str(e)[:LOG_ERROR_MAX_CHARS]
                logger.error("Model {} gagal: {}: {}", body.model, type(e).__name__, detail)
            else:
                logger.exception("Error tak terduga saat memanggil model {}", body.model)
            yield f"\n[{user_msg}]"
            return

        answer = "".join(parts)
        if answer:
            try:
                await run_in_threadpool(
                    chat_store.save_turn, body.conv_id, saved_text, answer, body.model
                )
            except sqlite3.Error:
                # Misal chat sudah dihapus saat streaming berjalan
                logger.warning("Gagal menyimpan jawaban untuk chat {}", body.conv_id)

        logger.info(
            "Chat selesai | conv={} | model={} | {} karakter | {:.1f} detik",
            body.conv_id, body.model, len(answer), time.perf_counter() - started,
        )

    return StreamingResponse(stream(), media_type=TEXT_PLAIN)