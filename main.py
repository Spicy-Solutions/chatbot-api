from typing import Union
from google import genai
from app.models.chat_request import ChatRequest
from dotenv import load_dotenv
from fastapi import FastAPI
import os

load_dotenv()

app = FastAPI()

client = genai.Client(api_key=os.getenv("GEMINI_APIKEY"))
    
@app.get("/models") # Get the list of models that I can only use
def models():
    models = client.models.list()
    
    return {"message": models }
    

@app.post("/chat")
async def chat(req: ChatRequest):
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents= req.message
    )
    
    return {
        "message": response.text
    }
    
    
    
""" If the response were made by using OpenAI, it would be like:
    completion = client.chat.completions.create(
        model="o3",
        messages=[
            {
                "role": "system", 
                "content": f"You are an expert partner in finance and decision making. The manager you are going to help is called {req.username} and the hotel has {req.income} soles of weekly income and ${req.expenses} soles of weekly expenses. Be kind, honest and professional in your responses."
            },
            {
                "role": "user",
                "content": req.message
            }
        ]
    )
    """
    