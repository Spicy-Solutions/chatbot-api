from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    username: str
    income: float
    expenses: float
    conversation_id : str