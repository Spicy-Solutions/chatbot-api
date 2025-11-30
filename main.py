from typing import Union
from google import genai
from app.models.chat_request import ChatRequest
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

load_dotenv()

app = FastAPI()

# Configurar CORS para permitir peticiones desde el frontend
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
- Siempre menciona los ingresos y gastos de la siguiente manera: Con la informacion que tengo a la mano de tu hotel.

Ahora empieza a ayudar al gerente con sus dudas o necesidades.
"""


genai_client = genai.Client(api_key=os.getenv("GEMINI_APIKEY"))
memory = {}

@app.get("/")
def root():
    return {"message": "Chatbot API is running! Visit /docs for API documentation."}

@app.get("/models") # Get the list of models that I can only use
def models():
    models = genai_client.models.list()
    return {"message": models }

@app.post("/chat")
async def chat(req: ChatRequest):
    
    # 1. Only build the system context on a NEW Conversation
    if req.conversation_id not in memory:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(username=req.username, income=req.income, expenses=req.expenses)
        
        memory[req.conversation_id] = [
            { 
                "role": "user", 
                "parts": [
                    {
                        "text": system_prompt
                    }
                ]
            }
        ]
    
    # 2. Append the user message into conversation's history context
    memory[req.conversation_id].append({
        "role": "user",
        "parts": [{"text": req.message}]
    })
    
    # 3. Call Gemini model
    response = genai_client.models.generate_content(
        model="gemini-2.0-flash",
        contents= memory[req.conversation_id]
    )

    # 4. Store assistan message into conversation's history context
    memory[req.conversation_id].append({
        "role": "model",
        "parts": [{"text": response.text}]
    })
    
    # 5. Returns model's response
    return {
        "message": response.text
    }
