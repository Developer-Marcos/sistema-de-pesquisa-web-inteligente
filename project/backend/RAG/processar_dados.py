from embeddings import transformar_em_embedding, chunking
#from metaparser import criar_metaparser
from extrair_dados_web import buscar_urls, extrair_conteudo
from config import TAVILY_API_KEY, GOOGLE_API_KEY
import asyncio

pergunta = "Como funciona a fotossintese?"
# pergunta_embedding = transformar_em_embedding(pergunta, GOOGLE_API_KEY) # Pergunta vira embeddings
# print(criar_metaparser(pergunta))

urls = buscar_urls(pergunta=pergunta, api_key=TAVILY_API_KEY)
conteudo_das_urls = asyncio.run(extrair_conteudo(urls))

conteudo_valido = [item for item in conteudo_das_urls if item["conteudo_textual"].strip()]

chunks_completos = list()
for item in conteudo_valido[:10]:
      url = item["url"]
      texto = item["conteudo_textual"]
      titulo = item["title"]

      chunks = chunking(texto=texto, url=url, titulo=titulo)
      chunks_completos.extend(chunks)

if not chunks_completos:
    raise RuntimeError("Chunking não gerou conteúdo. Verifique os textos extraídos.")

print(f"conteudo: {chunks_completos}")

