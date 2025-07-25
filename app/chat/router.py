from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict

from .services import chat

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str = Field(..., description="Message de l’utilisateur")
    history: List[Dict[str, str]] = Field(default_factory=list)

@router.post("/")
async def chat_endpoint(payload: ChatRequest):
    """
    Appel simple : renvoie la réponse de l’assistant
    """
    answer = chat(payload.message, payload.history)
    return {"assistant": answer}
