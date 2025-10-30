from config import GOOGLE_API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings



def transformar_em_embedding(pergunta, chave_api):
      modelo_embedding = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001" , api_key=chave_api)
      return modelo_embedding.embed_query(pergunta)

def chunking(texto: str, url: str, titulo: str, max_chars: int = 800) -> list[dict]:
    chunks = []
    inicio = 0
    chunk_id = 0

    while inicio < len(texto):
        fim = inicio + max_chars
        parte = texto[inicio:fim].strip()

        if parte:
            chunks.append({
                "page_content": parte,
                "metadata": {
                    "source": url,
                    "url": url,
                    "title": titulo,
                    "chunk_id": chunk_id,
                    "total_length": len(texto)
                }
            })

        inicio = fim
        chunk_id += 1

    return chunks

