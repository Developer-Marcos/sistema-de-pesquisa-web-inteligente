from embeddings import chunking, query_enhancement, criar_embedder, batch_processing, criar_db, reranking, gerar_resposta
from metaparser import criar_metaparser
from extrair_dados_web import buscar_urls, extrair_conteudo
from fila_global import progresso, resultado_final
from langchain_core.output_parsers import JsonOutputParser
from config import TAVILY_API_KEY, LLM
from time import time
import asyncio
import json


async def enviar_progresso(percentual, etapa):
    await progresso.put(json.dumps({
        "percentual": float(percentual),
        "etapa": etapa,
        "done": False
    }))


async def processar_dados(dados: str) -> dict:
    specs = dict()
    embedder_modelo = criar_embedder()

    inicio = time()
    specs["modelo_llm"] = getattr(LLM, "model", "desconhecido")
    specs["modelo_embedding"] = (embedder_modelo if isinstance(embedder_modelo, str) else "SentenceTransformer")

    # Etapa 0
    await enviar_progresso(1, "Iniciando pipeline de análise")

    # 1 - Pergunta + Metaparser paralelo
    await enviar_progresso(10, "Entendendo intenção e estrutura da pergunta")
    pergunta = dados
    metaparser_task = asyncio.create_task(criar_metaparser(pergunta=pergunta))
    specs["pergunta"] = dados
    
    print("1 - Definiu a pergunta e o metaparser")
    
    # 2 - Query enhancement
    await enviar_progresso(25, "Refinando pergunta para máxima precisão")
    perguntas_aprimoradas = query_enhancement(pergunta)
    perguntas_embeddings = [embedder_modelo.embed_query(q) for q in perguntas_aprimoradas]

    print("2 - Query enhancement finalizado com sucesso")

    # 3 - Busca URLs e extrai conteúdo
    await enviar_progresso(30, "Buscando fontes relevantes online")
    urls = buscar_urls(pergunta=pergunta, api_key=TAVILY_API_KEY)
    
    await enviar_progresso(40, "Extraindo conteúdo das fontes")
    conteudo_das_urls = await extrair_conteudo(urls)
    conteudo_valido = [item for item in conteudo_das_urls if item["conteudo_textual"].strip()]
    specs["num_urls_processadas"] = len(conteudo_valido)

    print("3 - Buscou as URLs relevantes")
    
    # 4 - Chunking incremental
    await enviar_progresso(55, "Separando os dados para processamento")
    chunks_completos = []
    quantidade_conteudo = min(20, len(conteudo_valido))

    if quantidade_conteudo == 0:
        raise RuntimeError("Nenhum conteúdo relevante encontrado para chunking.")

    for idx, item in enumerate(conteudo_valido[:quantidade_conteudo]):
        chunks = chunking(texto=item["conteudo_textual"], url=item["url"], titulo=item["title"])
        chunks_completos.extend(chunks)

        progresso_parcial = 40 + ((idx + 1) / quantidade_conteudo) * 15
        await enviar_progresso(progresso_parcial, f"Organizando conteúdo ({idx+1}/{quantidade_conteudo})")

    specs["num_chunks"] = len(chunks_completos)
    print("4 - Chunking com overlap executado")
    
    # 5 - Embeddings + DB
    await enviar_progresso(62, "Convertendo conhecimento em vetores semânticos")
    embeddings, metadados = await batch_processing(chunks_completos, embedder_modelo)
    
    print("5.1 - Embeddings criados")

    await enviar_progresso(70, "Construindo memória semântica")
    db_vetorial = criar_db(
        embeddings=embeddings,
        metadados=metadados,
        chunks=chunks_completos,
        embedder_modelo=embedder_modelo
    )

    specs["db_vetorial_tipo"] = type(db_vetorial).__name__
    specs["db_vetorial_num_vectors"] = len(db_vetorial.index_to_docstore_id)
    specs["db_vetorial_dimensao"] = db_vetorial.index.d

    print("5.2 - Banco vetorial criado")
    

    # 6 - Semantic search incremental
    await enviar_progresso(80, "Localizando as principais informações")
    resultados_semanticos = []
    total_queries = len(perguntas_embeddings)

    for idx, p_embedding in enumerate(perguntas_embeddings):
        top_chunks = db_vetorial.similarity_search_by_vector(p_embedding, k=10)
        resultados_semanticos.extend(top_chunks)

        progresso_parcial = 70 + ((idx + 1) / total_queries) * 10
        await enviar_progresso(progresso_parcial, f"Buscando respostas ({idx+1}/{total_queries})")

    print("6 - Semantic search")
    

    # 7 - Reranking
    await enviar_progresso(90, "Selecionando dados para resposta final")
    contexto_queries = " | ".join(perguntas_aprimoradas)
    resultados_ordenados = reranking(pergunta=contexto_queries, resultados_semanticos=resultados_semanticos)

    specs["num_resultados_semanticos"] = len(resultados_ordenados)

    print("7 - Reranking")
    
    # 8 - Resposta final
    metaparser = await metaparser_task
    parser = JsonOutputParser(pydantic_object=metaparser)

    resposta_final = await gerar_resposta(
        contexto="\n\n".join([
            f"<fonte>{c.metadata.get('url')}</fonte>\n"
            f"<titulo>{c.metadata.get('title')}</titulo>\n"
            f"<trecho>\n{c.page_content}\n</trecho>"
            for c in resultados_ordenados
        ]),
        pergunta=pergunta,
        schema_gerado=metaparser,
        parser=parser
    )

    specs["tempo_total_segundos"] = round(time() - inicio, 2)
    resposta_final["especificacoes"] = specs

    print("8 - Resposta final gerada")
    await enviar_progresso(97, "Resposta final pronta")

    await resultado_final.put(resposta_final)

    await progresso.put(json.dumps({
        "percentual": 100,
        "etapa": "Concluído",
        "done": True,
        "resultado": resposta_final
    }))

    return resposta_final
