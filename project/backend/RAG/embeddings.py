from config import API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings

modelo_embedding = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001" , api_key=API_KEY)

def transformar_em_embedding(pergunta):
      return modelo_embedding.embed_query(pergunta)