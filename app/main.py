from fastapi import FastAPI
import gradio as gr
from app.chat.router import router as chat_router
from app.auth.router import router as auth_router
from app.payment.router import router as payment_router  # IMPORTANT: cette ligne
from app.chat.services import chat as gradio_chat
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Backend redpill app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(chat_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(payment_router, prefix="/api")  # IMPORTANT: cette ligne

@app.get("/")
def read_root():
    return {
        "message": "Backend redpill app is running",
        "docs": "/docs", 
        "gradio": "/gradio",
        "status": "healthy"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "redpill-api"}


# Interface Gradio
demo = gr.ChatInterface(gradio_chat, type="messages")

if __name__ == "__main__":
    app = gr.mount_gradio_app(app, demo, path="/gradio")
    uvicorn.run(app, host="0.0.0.0", port=7860)