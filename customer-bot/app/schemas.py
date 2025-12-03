# app/schemas.py
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    user_text: str
    user_token: Optional[str] = None  # token referencing a user record

class ChatResponse(BaseModel):
    reply: str
