import warnings
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]  # folder root proyek
load_dotenv(BASE_DIR / ".env")  # harus dijalankan sebelum litellm dipakai

STATIC_DIR = BASE_DIR / "app" / "static"
DB_PATH = BASE_DIR / "data" / "chat.db"

# Nama tampilan -> string model LiteLLM.
# Nama ini juga dipakai sebagai key di MODEL_INFO dan sebagai identitas model.
MODELS = {
    "Nemotron 3.5 Super VL (free)": "openrouter/nvidia/nemotron-3.5-super-vl:free",
    "Nemotron 3 Ultra (free)": "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
    "Nemotron 3.5 Lightning (free)": "openrouter/nvidia/nemotron-3.5-lightning:free",
    "DeepSeek V4 Flash": "openrouter/deepseek/deepseek-v4-flash-0731",
    "DeepSeek V4 Pro": "openrouter/deepseek/deepseek-v4-pro-0813",
    "GPT-6.1 Terra": "openrouter/openai/gpt-6.1-terra",
    "GPT-6 Luna": "openrouter/openai/gpt-6-luna",
    "Gemini 3.8 Flash": "openrouter/google/gemini-3.8-flash",
    "Gemini 4 Argon": "openrouter/google/gemini-4-argon",
    "Claude Haiku 5.5": "openrouter/anthropic/claude-haiku-5.5",
    "Claude Sonnet 5.5": "openrouter/anthropic/claude-sonnet-5.5",
}

# Penjelasan untuk pengguna awam. Key harus sama persis dengan nama di MODELS.
# hint: teks pendek yang tampil di dropdown (usahakan di bawah 25 karakter,
#       dan dibuat berbeda untuk setiap model agar mudah dibedakan)
# desc: penjelasan lengkap yang tampil di bawah kotak input
MODEL_INFO = {
    "Nemotron 3.5 Lightning (free)": {
        "hint": "Gratis · Harian, cepat",
        "desc": "Pilihan utama untuk chat harian. Ringan dan cepat untuk tanya jawab dan tugas sederhana. Gratis, tapi ada batas pemakaian harian. Jangan dipakai untuk data rahasia.",
    },
    "Nemotron 3 Ultra (free)": {
        "hint": "Gratis · Coding & penalaran",
        "desc": "Model paling besar untuk coding dan masalah yang butuh penalaran bertahap, seperti merancang fitur atau mencari bug yang rumit. Lebih lambat dari model harian dan lebih cepat habis kuota gratisnya. Gratis, tapi ada batas pemakaian harian. Jangan dipakai untuk data rahasia.",
    },
       "Nemotron 3.5 Super VL (free)": {
        "hint": "Gratis · Analisis gambar",
        "desc": "Untuk menganalisis gambar, screenshot, dan dokumen. Kurang cocok untuk coding kompleks. Gratis, tapi ada batas pemakaian harian. Jangan dipakai untuk data rahasia.",
    },
    "Nemotron 3.5 Lightning (free)": {
        "hint": "Gratis · Cepat",
        "desc": "Model yang ringan dan cepat untuk tugas berulang atau pertanyaan sederhana. Gratis, tapi ada batas pemakaian harian. Kemampuan penalarannya lebih terbatas dibanding model Ultra. Jangan dipakai untuk data rahasia.",
    },
    "DeepSeek V4 Flash": {
        "hint": "Berbayar · Cepat",
        "desc": "Model yang cepat untuk tanya jawab dan coding ringan. Berbayar sesuai pemakaian, butuh saldo OpenRouter.",
    },
    "DeepSeek V4 Pro": {
        "hint": "Berbayar · Penalaran",
        "desc": "Versi yang lebih besar untuk coding dan masalah yang butuh penalaran. Berbayar sesuai pemakaian, butuh saldo OpenRouter.",
    },
    "GPT-6.1 Terra": {
        "hint": "Berbayar · Seimbang",
        "desc": "Pilihan seimbang untuk coding, menulis, dan chat harian. Cukup baik membaca screenshot. Berbayar sesuai pemakaian.",
    },
    "GPT-6 Luna": {
        "hint": "Berbayar · Hemat",
        "desc": "Versi cepat dan hemat untuk chat dan tugas ringan. Berbayar sesuai pemakaian, biaya per jawaban kecil.",
    },
    "Gemini 3.8 Flash": {
        "hint": "Berbayar · Cepat",
        "desc": "Model Gemini yang cepat untuk chat harian dan tugas ringan. Berbayar sesuai pemakaian, butuh saldo OpenRouter.",
    },
    "Gemini 4 Argon": {
        "hint": "Berbayar · Kualitas tinggi",
        "desc": "Model Gemini generasi terbaru. Cocok untuk tugas yang butuh kualitas lebih tinggi. Berbayar sesuai pemakaian, butuh saldo OpenRouter.",
    },
    "Claude Haiku 5.5": {
        "hint": "Berbayar · Ringan",
        "desc": "Claude yang lebih ringan dan cepat untuk pertanyaan singkat dan tugas sederhana. Berbayar sesuai pemakaian.",
    },
    "Claude Sonnet 5.5": {
        "hint": "Berbayar · Teliti",
        "desc": "Jawaban yang rapi dan teliti untuk coding dan tulisan. Berbayar sesuai pemakaian, butuh saldo OpenRouter.",
    },
}

# Peringatan jika ada model tanpa penjelasan. Model tetap berfungsi, hanya tanpa keterangan.
for _name in MODELS:
    if _name not in MODEL_INFO:
        warnings.warn(f"Model '{_name}' belum punya entri di MODEL_INFO", stacklevel=2)

SYSTEM_PROMPT = (
    "Jawab singkat, padat, langsung ke inti. Tanpa basa-basi. "
    "Topik IT/coding: code block bersih, komentar hanya bagian krusial. "
    "Permintaan panduan/tutorial: langkah detail dan jelas."
)

DEFAULT_TITLE = "Chat baru"
MAX_HISTORY = 40   # jumlah pesan terakhir yang dikirim ke model
MAX_TOKENS = 4096  # batas panjang jawaban per respons

# Logging
LOG_DIR = BASE_DIR / "logs"  # folder log harian
LOG_RETENTION_DAYS = 30      # file log lebih lama dari ini dihapus otomatis
LOG_LEVEL = "INFO"           # DEBUG, INFO, WARNING, ERROR