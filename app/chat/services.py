"""
Logique métier : construction du prompt, appel OpenAI, gestion des tool-calls.
"""
import json
import requests
from typing import List, Dict, Any

from .dependencies import (
    openai_client,
    get_system_prompt,
    PUSHOVER_USER,
    PUSHOVER_TOKEN,
    PUSHOVER_URL,
)

# ── Notifications Pushover ─────────────────────────────────────────────────────
def push(message: str) -> None:
    print(f"Push: {message}")
    payload = {"user": PUSHOVER_USER, "token": PUSHOVER_TOKEN, "message": message}
    requests.post(PUSHOVER_URL, data=payload, timeout=5)

# ── Tools pour l’agent OpenAI ──────────────────────────────────────────────────
def record_user_details(email: str, name: str = "Name not provided", notes: str = "not provided"):
    push(f"Recording interest notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question: str):
    push(f"Recording {question} asked that I couldn't answer")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name":  {"type": "string", "description": "The user's name, if provided"},
            "notes": {"type": "string", "description": "Contextual notes"},
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered",
    "parameters": {
        "type": "object",
        "properties": {"question": {"type": "string", "description": "Unanswered question"}},
        "required": ["question"],
        "additionalProperties": False,
    },
}

TOOLS = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]

# ── Gestion des tool-calls ─────────────────────────────────────────────────────
def _handle_tool_calls(tool_calls: List[Any]) -> List[Dict[str, Any]]:
    results = []
    for call in tool_calls:
        tool_name = call.function.name
        arguments = json.loads(call.function.arguments)

        fn = {
            "record_user_details": record_user_details,
            "record_unknown_question": record_unknown_question,
        }.get(tool_name)

        result = fn(**arguments) if fn else {}
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": call.id}
        )
    return results

# ── Fonction principale du chat ────────────────────────────────────────────────
def chat(user_message: str, history: List[Dict[str, str]]) -> str:
    """
    Fonction réutilisable par Gradio ou par une route FastAPI.
    :param user_message: dernier message utilisateur
    :param history: historique au format [{"role": "user"/"assistant", "content": "..."}]
                    (Gradio fournit déjà ce format)
    """
    messages = (
        [{"role": "system", "content": get_system_prompt()}]
        + history
        + [{"role": "user", "content": user_message}]
    )

    while True:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=TOOLS
        )
        finish_reason = response.choices[0].finish_reason

        # L’agent souhaite appeler un tool
        if finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            results = _handle_tool_calls(tool_calls)
            messages.append(response.choices[0].message)  # message "tool_calls"
            messages.extend(results)                      # réponses des tools
        else:
            # Réponse finale de l'assistant
            return response.choices[0].message.content
