from contextlib import asynccontextmanager
from typing import Union
from google import genai
from app.models.chat_request import ChatRequest
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

load_dotenv()

SYSTEM_PROMPT_TEMPLATE = """
Eres un experto socio en finanzas y toma de decisiones.
Tu rol es ayudar al gerente {username} del hotel.
Datos del hotel:
- Ingresos semanales: {income} soles
- Gastos semanales: {expenses} soles

Tu estilo:
- Sé amable, honesto y profesional.
- No inventes información que no tengas.
- Explica de forma clara y en términos simples.
- Responde SIEMPRE en español.
- Siempre menciona los ingresos y gastos de la siguiente manera:
  Con la informacion que tengo a la mano de tu hotel.

Ahora empieza a ayudar al gerente con sus dudas o necesidades.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):

    api_key = os.getenv("GEMINI_APIKEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_APIKEY in .env")

    try:
        app.state.genai_client = genai.Client(api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Gemini client: {e}")

    app.state.memory = {}

    print("Startup completed")
    yield
    print("Shutdown completed")

app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://sweet-manager-web-application.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
def root():
    return {"message": "Chatbot API is running! Visit /docs for API documentation."}

@app.get("/models")
def models():
    try:
        models = app.state.genai_client.models.list()
        return {"models": [m.name for m in models]}
    except Exception as e:
        raise HTTPException(500, f"Failed to list models: {e}")

@app.post("/chat")
async def chat(req: ChatRequest):
    memory = app.state.memory
    client = app.state.genai_client

    # 1. New conversation
    if req.conversation_id not in memory:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            username=req.username,
            income=req.income,
            expenses=req.expenses,
        )
        memory[req.conversation_id] = [
            {"role": "user", "parts": [{"text": system_prompt}]}
        ]

    # 2. Add user message
    memory[req.conversation_id].append(
        {"role": "user", "parts": [{"text": req.message}]}
    )

    # 3. Call Gemini with error handling
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=memory[req.conversation_id],
        )
    except Exception as e:
        raise HTTPException(500, f"Gemini model error: {e}")

    # 4. Store assistant response
    memory[req.conversation_id].append(
        {"role": "model", "parts": [{"text": response.text}]}
    )

    return {"message": response.text}
