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

client = genai.Client(api_key=os.getenv("GEMINI_APIKEY"))

@app.get("/")
def root():
    return {"message": "Chatbot API is running! Visit /docs for API documentation."}

@app.get("/models") # Get the list of models that I can only use
def models():
    models = client.models.list()
    return {"message": models }

@app.post("/chat")
async def chat(req: ChatRequest):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents= [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"You are an expert partner in finance and decision making. The manager you are going to help is called {req.username} and the hotel has {req.income} soles of weekly income and {req.expenses} soles of weekly expenses. Be kind, honest and professional in your responses. Always respond in Spanish."
                    }
                ]
            },
            {
                "role": "user",
                "parts": [
                    {
                        "text": req.message
                    }
                ]
            }
        ]
    )

    return {
        "message": response.text
    }
