import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
      print("POR FAVOR, INSIRA A CHAVE DE API DO GOOGLE_API_KEY NO ARQUIVO '.env'")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if TAVILY_API_KEY is None:
      print("POR FAVOR, INSIRA A CHAVE DE API DO TAVILY_API_KEY NO ARQUIVO '.env'")

LLM = ChatGoogleGenerativeAI(
      model="gemini-2.5-flash",
      api_key=GOOGLE_API_KEY
)