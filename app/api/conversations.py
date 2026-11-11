from fastapi import APIRouter, HTTPException

from app.db import chat_store

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("")
def list_conversations():
    return chat_store.list_conversations()


@router.post("")
def create_conversation():
    return chat_store.create_conversation()


@router.get("/{cid}")
def get_conversation(cid: str):
    conv = chat_store.get_conversation(cid)
    if conv is None:
        raise HTTPException(status_code=404, detail="Percakapan tidak ditemukan")
    return {**conv, "messages": chat_store.get_messages(cid)}


@router.delete("/{cid}")
def delete_conversation(cid: str):
    chat_store.delete_conversation(cid)
    return {"ok": True}