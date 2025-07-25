# from dotenv import load_dotenv
# from openai import OpenAI
# import json
# import os
# import requests
# from pypdf import PdfReader
# import gradio as gr

# load_dotenv(override=True)
# openai = OpenAI()

# pushover_user = os.getenv("PUSHOVER_USER")
# pushover_token = os.getenv("PUSHOVER_TOKEN")
# pushover_url = "https://api.pushover.net/1/messages.json"

# def push(message):
#     print(f"Push: {message}")
#     payload = {"user": pushover_user, "token": pushover_token, "message": message}
#     requests.post(pushover_url, data=payload)

# def record_user_details(email, name="Name not provided", notes="not provided"):
#     push(f"Recording interest notes {notes}")
#     return {"recorded": "ok"}

# def record_unknown_question(question):
#     push(f"Recording {question} asked that I couldn't answer")
#     return {"recorded": "ok"}

# record_user_details_json = {
#     "name": "record_user_details",
#     "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "email": {
#                 "type": "string",
#                 "description": "The email address of this user"
#             },
#             "name": {
#                 "type": "string",
#                 "description": "The user's name, if they provided it"
#             }
#             ,
#             "notes": {
#                 "type": "string",
#                 "description": "Any additional information about the conversation that's worth recording to give context"
#             }
#         },
#         "required": ["email"],
#         "additionalProperties": False
#     }
# }

# record_unknown_question_json = {
#     "name": "record_unknown_question",
#     "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "question": {
#                 "type": "string",
#                 "description": "The question that couldn't be answered"
#             },
#         },
#         "required": ["question"],
#         "additionalProperties": False
#     }
# }

# tools = [{"type": "function", "function": record_user_details_json},
#         {"type": "function", "function": record_unknown_question_json}]

# tools

# def handle_tool_calls(tool_calls):
#     results = []
#     for tool_call in tool_calls:
#         tool_name = tool_call.function.name
#         arguments = json.loads(tool_call.function.arguments)
#         print(f"Tool called: {tool_name}", flush=True)

#         # THE BIG IF STATEMENT!!!

#         if tool_name == "record_user_details":
#             result = record_user_details(**arguments)
#         elif tool_name == "record_unknown_question":
#             result = record_unknown_question(**arguments)

#         results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
#     return results

# globals()["record_unknown_question"]("this is a really hard question")

# def handle_tool_calls(tool_calls):
#     results = []
#     for tool_call in tool_calls:
#         tool_name = tool_call.function.name
#         arguments = json.loads(tool_call.function.arguments)
#         print(f"Tool called: {tool_name}", flush=True)
#         tool = globals().get(tool_name)
#         result = tool(**arguments) if tool else {}
#         results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
#     return results

# reader = PdfReader("presi/specpense.pdf")
# for page in reader.pages:
#     text = page.extract_text()
#     pages = []
# for page in reader.pages:
#     pages.append(page.extract_text() or "")
#     summary = "\n".join(pages)

# name = "Varain Engolo AI"

# system_prompt = f"Vous êtes le Professeur {name}, maître incontesté de la redpill. \
# Vous dispensez vos leçons comme des manifestes structurés selon les sujets abordés, les réponses aux questions posées doivent etre soit extraite du document specpense.pdf ou non répondu si le sujet n'est pas abordé dans ce documents. \
# Lorsque tu identifie l'article dans la specification selon la question du client il faut que tu réponde de maniere structuré avec autant de grand titre et d'xplication qu'il y a dans l'article sauf si le client demande une réponse breve. "
# system_prompt += f"\n\n## Summary:\n{summary}\n\n## "

# def chat(message, history):
#     messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
#     done = False
#     while not done:

#         # This is the call to the LLM - see that we pass in the tools json

#         response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)

#         finish_reason = response.choices[0].finish_reason
        
#         # If the LLM wants to call a tool, we do that!
         
#         if finish_reason=="tool_calls":
#             message = response.choices[0].message
#             tool_calls = message.tool_calls
#             results = handle_tool_calls(tool_calls)
#             messages.append(message)
#             messages.extend(results)
#         else:
#             done = True
#     return response.choices[0].message.content

# gr.ChatInterface(chat, type="messages").launch()

"""
Point d’entrée de l’application :
  – API FastAPI (inclut /chat)
  – Interface Gradio (facultative)
"""
from fastapi import FastAPI
import gradio as gr
from app.chat.router import router as chat_router
from app.chat.services import chat as gradio_chat

app = FastAPI(title="Backend redpill app")
app.include_router(chat_router)

# --- Interface Gradio (même comportement qu’avant) ----------------------------
demo = gr.ChatInterface(gradio_chat, type="messages")

if __name__ == "__main__":   # exécution directe : python -m app.main
    demo.launch()
