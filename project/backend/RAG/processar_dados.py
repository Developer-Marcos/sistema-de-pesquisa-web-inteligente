from embeddings import chunking, query_enhancement, criar_embedder, batch_processing, criar_db
#from metaparser import criar_metaparser
from extrair_dados_web import buscar_urls, extrair_conteudo
from config import TAVILY_API_KEY, GOOGLE_API_KEY
import asyncio

embedder_modelo = criar_embedder(chave_api=GOOGLE_API_KEY)

# 1 - Define a pergunta e cria o metaparser
pergunta = "Como funciona a fotossintese?"
# print(criar_metaparser(pergunta))

# 2 - Busca as urls e extrai o conteudo delas
urls = buscar_urls(pergunta=pergunta, api_key=TAVILY_API_KEY)
conteudo_das_urls = asyncio.run(extrair_conteudo(urls))
conteudo_valido = [item for item in conteudo_das_urls if item["conteudo_textual"].strip()]

# 3 - Cria os chunks usando overlapping
chunks_completos = list()
for item in conteudo_valido[:5]:
      url = item["url"]
      texto = item["conteudo_textual"]
      titulo = item["title"]

      chunks = chunking(texto=texto, url=url, titulo=titulo)
      chunks_completos.extend(chunks)

if not chunks_completos:
    raise RuntimeError("Chunking não gerou conteúdo. Verifique os textos extraídos.")

# 4 - Cria os embeddings com Batch processing e os insere no FAISS database
embeddings, metadados = batch_processing(chunks_completos, embedder_modelo)
db_vetorial = criar_db(
    embeddings_externos=embeddings,
    metadados=metadados,
    chunks=chunks_completos,
    embedder_object=embedder_modelo
)

# 5 - Usa Query enhancement para aprimorar a pergunta

#perguntas_aprimoradas = query_enhancement(pergunta)

#resultados_semanticos = list()
#for p in perguntas_aprimoradas:
     #p_embedding = embedder_modelo.embed_documents(p)


