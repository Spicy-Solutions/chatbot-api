import requests
import json

url = "http://localhost:8000/chat"
data = {
    "message": "Dame un consejo breve sobre finanzas",
    "username": "Nelson",
    "income": 5000,
    "expenses": 3000
}

try:
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("\nRespuesta del chatbot:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
