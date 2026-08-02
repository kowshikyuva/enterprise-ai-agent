from google.genai import Client
from app.core.config import GOOGLE_API_KEY

client = Client(api_key=GOOGLE_API_KEY)

print("Available Models:\n")

for model in client.models.list():
    print(model.name)