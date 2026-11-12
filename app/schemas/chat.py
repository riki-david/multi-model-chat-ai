from pydantic import BaseModel, Field

from app.core.attachments import Attachment


class ChatIn(BaseModel):
    conv_id: str
    message: str = ""
    model: str
    attachments: list[Attachment] = Field(default_factory=list)