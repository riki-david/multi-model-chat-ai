from app.core.config import SYSTEM_PROMPT

# Berlaku untuk semua model, supaya klaim identitas dari riwayat lama tidak ikut terbawa
STALE_IDENTITY_NOTE = (
    "Riwayat percakapan bisa berisi jawaban dari model lain. "
    "Jika ada pesan sebelumnya yang menyebut nama model berbeda, "
    "anggap itu bukan identitas kamu saat ini."
)


def build_system_prompt(display_name: str, model_id: str) -> str:
    """
    Menyusun system prompt dengan identitas model yang dipakai pada request ini.

    display_name : nama di dropdown, misalnya "Claude Sonnet"
    model_id     : string LiteLLM, misalnya "anthropic/claude-sonnet-4-5"
    """
    identity = (
        f"Identitas kamu pada permintaan ini: model '{display_name}' (ID: {model_id}). "
        "Jika ditanya model apa yang sedang kamu pakai, jawab sesuai identitas ini."
    )
    return "\n\n".join([SYSTEM_PROMPT, identity, STALE_IDENTITY_NOTE])