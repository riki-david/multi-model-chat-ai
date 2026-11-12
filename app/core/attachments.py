from pydantic import BaseModel

MAX_TOTAL_CHARS = 60_000  # batas total teks lampiran per pesan
MAX_IMAGES = 5            # batas jumlah gambar per pesan


class Attachment(BaseModel):
    name: str
    kind: str                     # "text" atau "image"
    content: str | None = None    # isi teks, untuk kind "text"
    mime: str | None = None       # untuk kind "image"
    data: str | None = None       # base64, untuk kind "image"


def build_message_content(
    message: str, attachments: list[Attachment]
) -> tuple[str | list, str]:
    """
    Mengembalikan (content_untuk_model, teks_untuk_db).

    - content_untuk_model: str jika tanpa gambar, list jika ada gambar
      (format OpenAI, didukung LiteLLM).
    - teks_untuk_db: teks saja, tanpa base64, agar database tidak membengkak.
    """
    texts: list[str] = []
    images: list[dict] = []
    used = 0

    for att in attachments:
        if att.kind == "image" and att.data and att.mime:
            if len(images) < MAX_IMAGES:
                images.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{att.mime};base64,{att.data}"},
                })
            continue

        if att.kind == "text" and att.content:
            room = MAX_TOTAL_CHARS - used
            if room <= 0:
                continue
            text = att.content[:room]
            used += len(text)
            safe_name = att.name.replace('"', "'")
            texts.append(f'<file name="{safe_name}">\n{text}\n</file>')

    context = "\n\n".join(texts)
    if message:
        prompt = f"{context}\n\n{message}" if context else message
    else:
        prompt = context

    if not images:
        return prompt, prompt

    model_content = [{"type": "text", "text": prompt or "Jelaskan gambar ini."}, *images]
    return model_content, prompt