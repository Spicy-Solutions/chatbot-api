from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    username: str
    income: float
    expenses: float
    conversation_id: Optional[str] = None