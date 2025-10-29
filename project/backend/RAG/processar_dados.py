#from embeddings import transformar_em_embedding
#from metaparser import criar_metaparser
from extrair_dados_web import buscar_urls, extrair_conteudo
from config import TAVILY_API_KEY
import asyncio

pergunta = "Quanto custa viajar pro japao?"
# pergunta_embedding = transformar_em_embedding(pergunta) # Pergunta vira embeddings
# print(criar_metaparser(pergunta))

urls = buscar_urls(pergunta=pergunta, api_key=TAVILY_API_KEY)
conteudo_das_urls = asyncio.run(extrair_conteudo(urls))

for item in conteudo_das_urls:
        print(f"URL: {item['url']}\nConteúdo (primeiros 100 chars):\n{item['conteudo_textual'][:100]}\n{'-'*80}")