from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
from .services import chat

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str  # "user" ou "assistant"
    content: str

class ChatRequest(BaseModel):
    #message: str = Field(..., description="Message de l'utilisateur")
    #history: List[Dict[str, str]] = Field(default_factory=list)
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    assistant: str

def limit_conversation_history(history: List[ChatMessage], max_messages: int = 10) -> List[ChatMessage]:
    """
    Limite l'historique à max_messages pour éviter de dépasser la limite de tokens.
    Garde les derniers messages pour conserver le contexte récent.
    """
    if len(history) <= max_messages:
        return history
    
    # Prendre les derniers max_messages messages
    return history[-max_messages:]

@router.delete("/clear")
async def clear_conversation():
    """
    Endpoint pour vider l'historique de la conversation.
    """
    return {"message": "Conversation cleared", "status": "success"}

@router.delete("/clear/{session_id}")
async def clear_specific_session(session_id: str):
    """
    Endpoint pour vider une session spécifique.
    """
    return {"message": f"Session {session_id} cleared", "status": "success"}

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint pour envoyer un message au chatbot.
    :param request: Message utilisateur + historique
    :return: Réponse de l'assistant
    """
    try:
        # Limiter l'historique avant de traiter
        limited_history = limit_conversation_history(request.history, max_messages=10)
        
        # Convertir les ChatMessage en dict pour la fonction chat()
        history_dict = [{"role": msg.role, "content": msg.content} for msg in limited_history]
        
        # Appeler la fonction chat de services.py
        response = chat(request.message, history_dict)
        return ChatResponse(assistant=response)
        
    except Exception as e:
        print(f"Erreur dans chat_endpoint: {e}")
        # En cas d'erreur, retourner un message d'erreur mais ne pas planter
        return ChatResponse(assistant="Désolé, je ne parviens pas à répondre pour l'instant.")