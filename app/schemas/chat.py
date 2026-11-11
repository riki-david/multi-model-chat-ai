from pydantic import BaseModel


class ChatIn(BaseModel):
    conv_id: str
    message: str
    model: str  # nama tampilan, harus ada di MODELS