from embeddings import chunking, query_enhancement, criar_embedder, batch_processing, criar_db, reranking, gerar_resposta
from metaparser import criar_metaparser
from extrair_dados_web import buscar_urls, extrair_conteudo
from langchain_core.output_parsers import JsonOutputParser
from config import TAVILY_API_KEY, GOOGLE_API_KEY, LLM
from time import time
import asyncio


async def processar_dados(dados: str) -> dict:
    # 0 - configs iniciais
    specs = dict()

    embedder_modelo = criar_embedder() # Embedder local

    specs["tempo_inicial"] = time()
    specs["modelo_llm"] = getattr(LLM, "model", "desconhecido")
    specs["modelo_embedding"] = (embedder_modelo if isinstance(embedder_modelo, str) else "SentenceTransformer")

    # 1 - Define a pergunta e cria o metaparser em paralelo
    pergunta = dados
    metaparser_task = asyncio.create_task(criar_metaparser(pergunta=pergunta))

    specs["pergunta"] = dados

    print("1 - Definiu a pergunta e o metaparser")

    # 2 - Usa Query enhancement para aprimorar a pergunta e depois gera os embeddings
    perguntas_aprimoradas = query_enhancement(pergunta)
    perguntas_embeddings = [embedder_modelo.embed_query(q) for q in perguntas_aprimoradas]

    print('2 - Query enhancement finalizado com sucesso')
    
    # 3 - Busca as urls e extrai o conteudo delas
    urls = buscar_urls(pergunta=pergunta, api_key=TAVILY_API_KEY)
    conteudo_das_urls = await extrair_conteudo(urls)
    conteudo_valido = [item for item in conteudo_das_urls if item["conteudo_textual"].strip()]

    specs["num_urls_processadas"] = len(conteudo_valido)

    print("3 - Buscou as URLs relevantes")

    # 4 - Cria os chunks usando overlapping
    chunks_completos = list()
    quantidade_conteudo = 20 
    for item in conteudo_valido[:quantidade_conteudo]:
        url = item["url"]
        texto = item["conteudo_textual"]
        titulo = item["title"]

        chunks = chunking(texto=texto, url=url, titulo=titulo)
        chunks_completos.extend(chunks)

    if not chunks_completos:
        raise RuntimeError("Chunking não gerou conteúdo. Verifique os textos extraídos.")
    
    specs["num_chunks"] = len(chunks_completos)
    
    print("4 - Chunking com overlap executado")

    # 5 - Cria os embeddings com Batch processing e os insere no FAISS database
    embeddings, metadados = await batch_processing(chunks_completos, embedder_modelo)
    db_vetorial = criar_db(
        embeddings=embeddings,
        metadados=metadados,
        chunks=chunks_completos,
        embedder_modelo=embedder_modelo
    )

    specs["db_vetorial_tipo"] = type(db_vetorial).__name__
    specs["db_vetorial_num_vectors"] = len(db_vetorial.index_to_docstore_id)
    specs["db_vetorial_dimensao"] = db_vetorial.index.d


    print("5 - Embeddings gerados usando o Batch processing")

    # 6 - Semantic search para cada pergunta aprimorada
    specs["top_k_usado"] = 10

    resultados_semanticos = list()
    for p_embedding in perguntas_embeddings:
        top_chunks = db_vetorial.similarity_search_by_vector(p_embedding, k=specs["top_k_usado"])
        resultados_semanticos.extend(top_chunks)
    
    print("6 - Semantic search deu certo")

    # 7 - Reranking global usando todas as queries como contexto
    contexto_queries = " | ".join(perguntas_aprimoradas)
    resultados_ordenados = reranking(
        pergunta=contexto_queries,           
        resultados_semanticos=resultados_semanticos
    )

    specs["num_resultados_semanticos"] = len(resultados_ordenados)

    print("7 - Reranking funcionou")

    # 8 - Response Generation usando o metaparser
    metaparser = await metaparser_task
    json_metaparser = JsonOutputParser(pydantic_object=metaparser)
    resposta_final = await gerar_resposta(
        contexto="\n\n".join([
            f"<fonte>{c.metadata.get('url', 'desconhecida')}</fonte>\n"
            f"<titulo>{c.metadata.get('title','sem título')}</titulo>\n"
            f"<trecho>\n{c.page_content}\n</trecho>"
            for c in resultados_ordenados    
        ]),
        pergunta=pergunta,
        schema_gerado=metaparser,
        parser=json_metaparser
    )

    resposta_final['especificacoes'] = {
        "pergunta": specs["pergunta"],
        "num_urls_processadas": specs["num_urls_processadas"],
        "tempo_de_processamento_total_segundos": round(time() - specs["tempo_inicial"]),
        "modelo_llm": specs["modelo_llm"],
        "modelo_embedding": specs["modelo_embedding"],
        "num_chunks": specs["num_chunks"],
        "top_k_usado": specs["top_k_usado"],
        "num_top_k_chunks": specs["num_resultados_semanticos"],
        "db_vetorial_tipo": specs["db_vetorial_tipo"],
        "db_vetorial_dimensao" : specs["db_vetorial_dimensao"],
        "db_vetorial_num_vectors": specs["db_vetorial_num_vectors"]
    }

    print("8 - Geracao da resposta final foi um sucesso")

    return resposta_final


    

