# Multi-Model Chat AI

Web chat lokal dengan FastAPI, bisa ganti model (Gemini, Claude, GPT, Ollama) lewat LiteLLM. Riwayat chat tersimpan di SQLite.

## Instalasi

```bash
cd multi-model-chat-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # lalu isi API key
```

## Menjalankan

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

Buka http://127.0.0.1:8000

## Catatan

- Model tanpa key bisa dipakai lewat Ollama (`ollama pull llama3`).
- Jangan commit `.env` dan `data/`.
