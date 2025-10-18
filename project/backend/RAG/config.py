import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY is None:
      print("POR FAVOR, INSIRA A CHAVE DE API DO GOOGLE NO ARQUIVO '.env'")