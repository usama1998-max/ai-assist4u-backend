from pydantic import BaseModel


class ChatHistoryRequest(BaseModel):
    prompt: str
    tab_id: int
