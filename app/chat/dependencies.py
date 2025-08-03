"""
Centralise la configuration commune au module chat.
"""
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

# ── Configuration générale ─────────────────────────────────────────────────────
load_dotenv(override=True)
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static" / "document"
PDF_PATH = STATIC_DIR / "specpense.pdf"

# ── Clients externes ───────────────────────────────────────────────────────────
openai_client = OpenAI()

PUSHOVER_USER = os.getenv("PUSHOVER_USER")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"

# ── PDF résumé (chargé une seule fois au démarrage) ───────────────────────────
def _build_spec_summary() -> str:
    reader = PdfReader(PDF_PATH)
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages)

SPEC_SUMMARY = _build_spec_summary()

# ── Prompt système de base ─────────────────────────────────────────────────────
def get_system_prompt() -> str:
    name = "Ralph AI"
    prompt = (
        f"Vous êtes le L'assistant {name}, maître incontesté de la redpill. "
        "Vous dispensez vos leçons comme des manifestes structurés selon les sujets abordés. "
        "Les réponses aux questions posées doivent être soit extraites du document specpense.pdf "
        "ou non répondues si le sujet n'est pas abordé dans ce document. "
        "Lorsque tu identifie l'article dans la spécification selon la question du client "
        "il faut que tu répondes de manière structurée avec autant de titres et d'explications "
        "qu'il y a dans l'article, sauf si le client demande une réponse brève."
        f"\n\n## Summary:\n{SPEC_SUMMARY}\n\n## "
    )
    return prompt
