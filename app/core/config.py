from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]  # folder root proyek
load_dotenv(BASE_DIR / ".env")  # harus dijalankan sebelum litellm dipakai

STATIC_DIR = BASE_DIR / "app" / "static"
DB_PATH = BASE_DIR / "data" / "chat.db"

# Nama tampilan -> string model LiteLLM
MODELS = {
    "Gemini Flash": "gemini/gemini-3.5-flash",
    "Claude Sonnet": "anthropic/claude-sonnet-4-5",
    "GPT-4o": "gpt-4o",
    "Llama 3 (lokal)": "ollama/llama3",
}

SYSTEM_PROMPT = (
    "Jawab singkat, padat, langsung ke inti. Tanpa basa-basi. "
    "Topik IT/coding: code block bersih, komentar hanya bagian krusial. "
    "Permintaan panduan/tutorial: langkah detail dan jelas."
)

DEFAULT_TITLE = "Chat baru"
MAX_HISTORY = 40   # jumlah pesan terakhir yang dikirim ke model
MAX_TOKENS = 2048  # batas panjang jawaban per respons