from pydantic import BaseModel


class SimpleAIResponse(BaseModel):
    message: str
