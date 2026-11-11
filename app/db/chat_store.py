import uuid
from datetime import datetime

from app.core.config import DEFAULT_TITLE
from app.db.session import get_db


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def list_conversations() -> list[dict]:
    with get_db() as c:
        rows = c.execute(
            "SELECT id, title, updated_at FROM conversations ORDER BY updated_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def create_conversation() -> dict:
    cid, ts = uuid.uuid4().hex, _now()
    with get_db() as c:
        c.execute(
            "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?,?,?,?)",
            (cid, DEFAULT_TITLE, ts, ts),
        )
    return {"id": cid, "title": DEFAULT_TITLE}


def get_conversation(cid: str) -> dict | None:
    with get_db() as c:
        row = c.execute(
            "SELECT id, title FROM conversations WHERE id = ?", (cid,)
        ).fetchone()
    return dict(row) if row else None


def conversation_exists(cid: str) -> bool:
    with get_db() as c:
        return c.execute(
            "SELECT 1 FROM conversations WHERE id = ?", (cid,)
        ).fetchone() is not None


def get_messages(cid: str) -> list[dict]:
    with get_db() as c:
        rows = c.execute(
            "SELECT role, content, model FROM messages WHERE conv_id = ? ORDER BY id",
            (cid,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_history(cid: str) -> list[dict]:
    """Riwayat dalam format yang dipahami LLM (role + content)."""
    return [{"role": m["role"], "content": m["content"]} for m in get_messages(cid)]


def delete_conversation(cid: str) -> None:
    with get_db() as c:
        c.execute("DELETE FROM conversations WHERE id = ?", (cid,))


def save_turn(cid: str, user_text: str, answer: str, model: str) -> None:
    """Simpan pasangan pesan user + jawaban AI setelah streaming selesai."""
    ts = _now()
    with get_db() as c:
        is_first = c.execute(
            "SELECT COUNT(*) FROM messages WHERE conv_id = ?", (cid,)
        ).fetchone()[0] == 0

        c.execute(
            "INSERT INTO messages (conv_id, role, content, model, created_at) VALUES (?,?,?,?,?)",
            (cid, "user", user_text, None, ts),
        )
        c.execute(
            "INSERT INTO messages (conv_id, role, content, model, created_at) VALUES (?,?,?,?,?)",
            (cid, "assistant", answer, model, ts),
        )

        if is_first:  # judul diambil dari pesan pertama
            title = " ".join(user_text.split())[:40] or DEFAULT_TITLE
            c.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title, ts, cid),
            )
        else:
            c.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?", (ts, cid)
            )