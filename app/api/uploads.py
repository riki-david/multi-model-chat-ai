import asyncio
import base64
import io
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

router = APIRouter(prefix="/api", tags=["uploads"])

MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
MAX_TEXT_CHARS = 200_000      # batas teks hasil ekstraksi per file
MAX_XLSX_ROWS = 500           # batas baris per sheet

IMAGE_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


# ---------- Ekstraksi teks (fungsi sinkron, dijalankan di thread) ----------

def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    if reader.is_encrypted:
        reader.decrypt("")  # coba password kosong
    pages = []
    for i, page in enumerate(reader.pages, 1):
        pages.append(f"[Halaman {i}]\n{page.extract_text() or '(tanpa teks)'}")
    return "\n\n".join(pages)


def _extract_docx(data: bytes) -> str:
    from docx import Document

    doc = Document(io.BytesIO(data))
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text.strip() for cell in row.cells))
    return "\n".join(parts)


def _extract_xlsx(data: bytes) -> str:
    from openpyxl import load_workbook

    wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        out.append(f"[Sheet: {ws.title}]")
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i >= MAX_XLSX_ROWS:
                out.append(f"... (dipotong setelah {MAX_XLSX_ROWS} baris)")
                break
            if any(v is not None for v in row):
                out.append("\t".join("" if v is None else str(v) for v in row))
    wb.close()
    return "\n".join(out)


def _extract_pptx(data: bytes) -> str:
    from pptx import Presentation

    prs = Presentation(io.BytesIO(data))
    out = []
    for i, slide in enumerate(prs.slides, 1):
        out.append(f"[Slide {i}]")
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                out.append(shape.text_frame.text)
    return "\n".join(out)


EXTRACTORS = {
    ".pdf": _extract_pdf,
    ".docx": _extract_docx,
    ".xlsx": _extract_xlsx,
    ".pptx": _extract_pptx,
}


# ---------- Endpoint ----------

@router.post("/upload")
async def upload_file(file: UploadFile):
    name = file.filename or "file"
    ext = Path(name).suffix.lower()

    # Baca maksimal MAX_BYTES+1 agar file besar tidak memenuhi RAM
    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File terlalu besar (maksimal 10 MB)")
    if not data:
        raise HTTPException(400, "File kosong")

    # Gambar: dikirim sebagai base64, model harus mendukung vision
    if ext in IMAGE_MIME:
        return {
            "name": name,
            "kind": "image",
            "mime": IMAGE_MIME[ext],
            "data": base64.b64encode(data).decode("ascii"),
        }

    try:
        if ext in EXTRACTORS:
            # Parser dokumen berat, jalankan di thread agar server tidak macet
            text = await asyncio.to_thread(EXTRACTORS[ext], data)
        else:
            # Format lain dianggap teks jika bukan biner (cek byte NUL)
            if b"\x00" in data[:8192]:
                raise HTTPException(
                    400, f"Format '{ext or '-'}' berupa file biner dan belum didukung"
                )
            text = data.decode("utf-8-sig", errors="replace")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(422, f"Gagal membaca {name}: {exc}")

    if len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS] + "\n... (dipotong, file terlalu panjang)"

    return {"name": name, "kind": "text", "content": text}