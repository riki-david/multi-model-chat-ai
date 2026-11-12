from fastapi import APIRouter, Query
from starlette.concurrency import run_in_threadpool

from app.db import chat_store

router = APIRouter(prefix="/api", tags=["search"])

MAX_RESULTS = 30      # jumlah chat maksimal yang dikembalikan
SNIPPET_RADIUS = 60   # jumlah karakter di kiri dan kanan kata yang ditemukan


def _snippet(text: str, ql: str) -> str:
    """Potongan teks di sekitar kata yang dicari (ql sudah dalam huruf kecil)."""
    i = text.lower().find(ql)
    start = max(0, i - SNIPPET_RADIUS)
    end = min(len(text), i + len(ql) + SNIPPET_RADIUS)
    s = " ".join(text[start:end].split())  # rapikan spasi dan baris baru
    return ("…" if start > 0 else "") + s + ("…" if end < len(text) else "")


def _search(q: str) -> list[dict]:
    ql = q.lower()
    results: list[dict] = []

    for conv in chat_store.list_conversations():
        cid = conv["id"]
        title = conv.get("title") or ""

        snippet = None
        if ql in title.lower():
            snippet = ""  # cocok di judul, tidak perlu potongan isi
        else:
            # Cari di isi pesan, berhenti di pesan pertama yang cocok
            for m in chat_store.get_messages(cid):
                content = m.get("content") or ""
                if ql in content.lower():
                    snippet = _snippet(content, ql)
                    break

        if snippet is not None:
            results.append({"id": cid, "title": title, "snippet": snippet})
            if len(results) >= MAX_RESULTS:
                break

    return results


@router.get("/search")
async def search(q: str = Query(default="", max_length=100)):
    q = q.strip()
    if len(q) < 2:
        return []
    # Akses SQLite dijalankan di threadpool agar event loop tidak terblokir
    return await run_in_threadpool(_search, q)