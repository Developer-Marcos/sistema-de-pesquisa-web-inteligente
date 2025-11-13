from embeddings import chunking, query_enhancement, criar_embedder, batch_processing, criar_db, reranking, gerar_resposta
from metaparser import criar_metaparser
from extrair_dados_web import buscar_urls, extrair_conteudo
from fila_global import progresso, resultado_final
from langchain_core.output_parsers import JsonOutputParser
from config import TAVILY_API_KEY, LLM
from time import time
import asyncio
import json


async def verificar_cancelamento(cancelar):
    if cancelar():
        await progresso.put({
            "percentual": 0,
            "etapa": "Processamento cancelado pelo usuário",
            "done": True,
            "resultado": None
        })
        raise asyncio.CancelledError("Processamento cancelado pelo usuário")

async def enviar_progresso(percentual, etapa):
    await progresso.put(json.dumps({
        "percentual": float(percentual),
        "etapa": etapa,
        "done": False
    }))

async def progresso_passos(percentual: float, etapa: str, cancelar):
    await enviar_progresso(percentual, etapa)
    await verificar_cancelamento(cancelar)

async def processar_dados(dados: str, cancelar) -> dict:
    specs = dict()
    embedder_modelo = criar_embedder()
    inicio = time()
    loop = asyncio.get_running_loop()  

    specs["modelo_llm"] = getattr(LLM, "model", "desconhecido")
    specs["modelo_embedding"] = (embedder_modelo if isinstance(embedder_modelo, str) else "SentenceTransformer")

    try:
        # Etapa 0
        await progresso_passos(1, "Iniciando pipeline de análise", cancelar)

        # 1 - Pergunta + Metaparser paralelo
        pergunta = dados
        metaparser_task = asyncio.create_task(criar_metaparser(pergunta=pergunta))
        specs["pergunta"] = dados
        await progresso_passos(10, "Entendendo intenção e estrutura da pergunta", cancelar)
        print("1 - Definiu a pergunta e o metaparser")

        # 2 - Query enhancement (síncrono, mas executado em executor)
        perguntas_aprimoradas = await loop.run_in_executor(None, query_enhancement, pergunta)
        perguntas_embeddings = [embedder_modelo.embed_query(q) for q in perguntas_aprimoradas]
        await progresso_passos(25, "Refinando pergunta para máxima precisão", cancelar)
        print("2 - Query enhancement finalizado com sucesso")

        # 3 - Busca URLs e extrai conteúdo (síncrono -> executor)
        urls = await loop.run_in_executor(None, buscar_urls, pergunta, TAVILY_API_KEY)
        await progresso_passos(30, "Buscando fontes relevantes online", cancelar)

        conteudo_das_urls = await extrair_conteudo(urls)  # se async, mantemos assim
        conteudo_valido = [item for item in conteudo_das_urls if item["conteudo_textual"].strip()]
        specs["num_urls_processadas"] = len(conteudo_valido)
        await progresso_passos(40, "Extraindo conteúdo das fontes", cancelar)
        print("3 - Buscou as URLs relevantes")

        # 4 - Chunking incremental (síncrono -> executor)
        chunks_completos = []
        quantidade_conteudo = min(20, len(conteudo_valido))
        if quantidade_conteudo == 0:
            raise RuntimeError("Nenhum conteúdo relevante encontrado para chunking.")

        for idx, item in enumerate(conteudo_valido[:quantidade_conteudo]):
            chunks = await loop.run_in_executor(None, chunking, item["conteudo_textual"], item["url"], item["title"])
            chunks_completos.extend(chunks)
            progresso_parcial = 40 + ((idx + 1) / quantidade_conteudo) * 15
            await progresso_passos(progresso_parcial, f"Organizando conteúdo ({idx+1}/{quantidade_conteudo})", cancelar)

        specs["num_chunks"] = len(chunks_completos)
        print("4 - Chunking com overlap executado")

        # 5 - Embeddings + DB (batch_processing já é async)
        embeddings, metadados = await batch_processing(chunks_completos, embedder_modelo)
        await progresso_passos(62, "Convertendo conhecimento em vetores semânticos", cancelar)
        print("5.1 - Embeddings criados")

        db_vetorial = criar_db(
            embeddings=embeddings,
            metadados=metadados,
            chunks=chunks_completos,
            embedder_modelo=embedder_modelo
        )
        specs["db_vetorial_tipo"] = type(db_vetorial).__name__
        specs["db_vetorial_num_vectors"] = len(db_vetorial.index_to_docstore_id)
        specs["db_vetorial_dimensao"] = db_vetorial.index.d
        await progresso_passos(70, "Construindo memória semântica", cancelar)
        print("5.2 - Banco vetorial criado")

        # 6 - Semantic search incremental
        resultados_semanticos = []
        total_queries = len(perguntas_embeddings)
        for idx, p_embedding in enumerate(perguntas_embeddings):
            top_chunks = db_vetorial.similarity_search_by_vector(p_embedding, k=10)
            resultados_semanticos.extend(top_chunks)
            progresso_parcial = 70 + ((idx + 1) / total_queries) * 10
            await progresso_passos(progresso_parcial, f"Buscando respostas ({idx+1}/{total_queries})", cancelar)
        print("6 - Semantic search")

        # 7 - Reranking (síncrono -> executor)
        contexto_queries = " | ".join(perguntas_aprimoradas)
        resultados_ordenados = await loop.run_in_executor(None, reranking, contexto_queries, resultados_semanticos)
        await progresso_passos(90, "Selecionando dados para resposta final", cancelar)
        specs["num_resultados_semanticos"] = len(resultados_ordenados)
        print("7 - Reranking")

        # 8 - Resposta final (async)
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
        await progresso_passos(97, "Resposta final pronta", cancelar)
        print("8 - Resposta final gerada")

        await resultado_final.put(resposta_final)
        await progresso.put(json.dumps({
            "percentual": 100,
            "etapa": "Concluído",
            "done": True,
            "resultado": resposta_final
        }))

        return resposta_final

    except asyncio.CancelledError:
        while not progresso.empty():
            progresso.get_nowait()
        await progresso.put(json.dumps({
            "percentual": 0,
            "etapa": "Processamento cancelado pelo usuário",
            "done": True,
            "resultado": None
        }))
        print("Processamento cancelado pelo usuário")
        return {"cancelado": True, "resultado": None}




