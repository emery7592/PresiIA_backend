"""
Logique métier avec RAG : construction du prompt intelligent, appel OpenAI, gestion des tool-calls.
"""
import json
import requests
from typing import List, Dict, Any
from .dependencies import (
    openai_client,
    get_system_prompt,  # Maintenant prend user_query en paramètre
    PUSHOVER_USER,
    PUSHOVER_TOKEN,
    PUSHOVER_URL,
)

# ── Notifications Pushover ─────────────────────────────────────────────────────
def push(message: str) -> None:
    print(f"Push: {message}")
    payload = {"user": PUSHOVER_USER, "token": PUSHOVER_TOKEN, "message": message}
    requests.post(PUSHOVER_URL, data=payload, timeout=5)

# ── Tools pour l'agent OpenAI ──────────────────────────────────────────────────
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
            "name": {"type": "string", "description": "The user's name, if provided"},
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

# ── Gestion des tool-calls (garde ton underscore !) ────────────────────────────
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

# ── Gestion des tool-calls (garde ton underscore !) ────────────────────────────
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

# ── Fonction principale du chat avec RAG ───────────────────────────────────────
def chat(user_message: str, history: List[Dict[str, str]]) -> str:
    """
    Fonction chat avec RAG : génère un contexte intelligent pour chaque requête.
    :param user_message: dernier message utilisateur
    :param history: historique au format [{"role": "user"/"assistant", "content": "..."}]
    """
    
    # 🎯 NOUVEAUTÉ : Le prompt système est généré dynamiquement selon la question
    messages = (
        [{"role": "system", "content": get_system_prompt(user_message)}]
        + history
        + [{"role": "user", "content": user_message}]
    )
    
    # Debug: affichage de la taille totale des messages
    total_chars = sum(len(msg["content"]) for msg in messages)
    print(f"📊 Total caractères envoyés à OpenAI: {total_chars} (~{total_chars//4} tokens)")
    
    while True:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=messages, 
                tools=TOOLS
            )
            
            finish_reason = response.choices[0].finish_reason
            
            # L'agent souhaite appeler un tool
            if finish_reason == "tool_calls":
                tool_calls = response.choices[0].message.tool_calls
                results = _handle_tool_calls(tool_calls)  # Garde ton underscore !
                messages.append(response.choices[0].message)  # message "tool_calls"
                messages.extend(results)  # réponses des tools
            else:
                # Réponse finale de l'assistant
                response_content = response.choices[0].message.content
                print(f"✅ Réponse générée: {len(response_content)} caractères")
                return response_content
                
        except Exception as e:
            print(f"❌ Erreur OpenAI: {e}")
            return "Désolé, je ne parviens pas à répondre pour l'instant. Veuillez réessayer."