from fastapi import FastAPI
import gradio as gr
from app.chat.router import router as chat_router
from app.chat.services import chat as gradio_chat
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Backend redpill app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev seulement
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure le router chat avec les routes API
app.include_router(chat_router)

# --- Interface Gradio (même comportement qu'avant) ----------------------------
demo = gr.ChatInterface(gradio_chat, type="messages")

if __name__ == "__main__":
    # Pour que FastAPI et Gradio tournent sur le même port
    # On monte Gradio sur FastAPI
    app = gr.mount_gradio_app(app, demo, path="/gradio")
    
    # Lancer le serveur sur le port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)