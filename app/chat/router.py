from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict

from .services import chat

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str  # "user" ou "assistant"
    content: str

class ChatRequest(BaseModel):
    #message: str = Field(..., description="Message de l’utilisateur")
    #history: List[Dict[str, str]] = Field(default_factory=list)
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    assistant: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint pour envoyer un message au chatbot.
    
    :param request: Message utilisateur + historique
    :return: Réponse de l'assistant
    """
    try:
        # Convertir les ChatMessage en dict pour la fonction chat()
        history_dict = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        # Appeler la fonction chat de services.py
        response = chat(request.message, history_dict)
        
        return ChatResponse(assistant=response)
        
    except Exception as e:
        print(f"Erreur dans chat_endpoint: {e}")
        # En cas d'erreur, retourner un message d'erreur mais ne pas planter
        return ChatResponse(assistant="Désolé, je ne parviens pas à répondre pour l'instant.")