from embeddings import chunking, query_enhancement, criar_embedder, batch_processing, criar_db, reranking, gerar_resposta
from metaparser import criar_metaparser
from extrair_dados_web import buscar_urls, extrair_conteudo
from fila_global import progresso, resultado_final
from langchain_core.output_parsers import JsonOutputParser
from config import TAVILY_API_KEY, LLM
from time import time
import unicodedata
import asyncio
import json

try:
    from cache_redis import (
        gerar_chave_cache_por_topicos, 
        obter_cache_pickle, 
        salvar_cache_pickle
    )
    print("Módulo de Cache (Redis) importado com sucesso.")
except ImportError:
    print("AVISO: Módulo de cache não encontrado. Executando sem cache.")
    def gerar_chave_cache_por_topicos(_): return None
    def obter_cache_pickle(_): return None
    def salvar_cache_pickle(*_): pass


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

def normalizar(texto):
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()

async def processar_dados(dados: str, cancelar) -> dict:
    specs = dict()
    embedder_modelo = criar_embedder()
    inicio = time()
    loop = asyncio.get_running_loop() 

    specs["modelo_llm"] = getattr(LLM, "model", "desconhecido")
    specs["modelo_embedding"] = (embedder_modelo if isinstance(embedder_modelo, str) else "SentenceTransformer")

    chunks_completos = []
    embeddings = None
    metadados = None
    db_vetorial = None

    try:
        # Etapa 0
        await progresso_passos(1, "Iniciando pipeline de análise", cancelar)

        # 1 - Pergunta + Metaparser paralelo
        pergunta = dados  
        metaparser_task = asyncio.create_task(criar_metaparser(pergunta=pergunta))
        specs["pergunta"] = dados
        await progresso_passos(10, "Entendendo intenção e estrutura da pergunta", cancelar)
        print("1 - Definiu a pergunta e o metaparser")

        # 2 - Query enhancement
        perguntas_aprimoradas = await loop.run_in_executor(None, query_enhancement, pergunta)
        print(f"DEBUG: TÓPICOS GERADOS: {perguntas_aprimoradas[-1]}")
        perguntas_embeddings = [embedder_modelo.embed_query(q) for q in perguntas_aprimoradas]
        await progresso_passos(25, "Refinando pergunta para máxima precisão", cancelar)
        print("2 - Query enhancement finalizado com sucesso")
        
        # 3 - Gerar a chave de cache com a função do cache.py
        string_tokens_bruta = perguntas_aprimoradas[-1]
        lista_tokens = string_tokens_bruta.split()
        lista_limpa = [normalizar(t) for t in lista_tokens if len(t) > 2]
        tokens_finais = sorted(lista_limpa[:3])
        cache_key = gerar_chave_cache_por_topicos(tokens_finais)
        
        cached_data = None
        if cache_key:
            print(f"Chave de cache gerada (baseada nos tópicos): {cache_key}")
            cached_data = await loop.run_in_executor(None, obter_cache_pickle, cache_key)
        else:
            print("Não foi possível gerar chave de cache (sem tópicos?). Pulando cache.")

        if cached_data:
            print(f"Cache HIT para a chave: {cache_key}")
            chunks_completos, embeddings, metadados, cached_specs = cached_data
            
            specs.update(cached_specs)
            await progresso_passos(40, "Dados relevantes encontrados em cache", cancelar)
            await progresso_passos(62, "Convertendo conhecimento (cache) em vetores", cancelar)
            print("Cache HIT: Pulando Etapas 4, 5, 6.1 e 6.2")

        else:
            if cache_key:
                print(f"Cache MISS para a chave: {cache_key}")
            
            # 4 - Busca URLs e extrai conteúdo
            urls = await loop.run_in_executor(None, buscar_urls, pergunta, TAVILY_API_KEY)
            await progresso_passos(30, "Buscando fontes relevantes online", cancelar)

            conteudo_das_urls = await extrair_conteudo(urls)  
            conteudo_valido = [item for item in conteudo_das_urls if item["conteudo_textual"].strip()]
            specs["num_urls_processadas"] = len(conteudo_valido)
            await progresso_passos(40, "Extraindo conteúdo das fontes", cancelar)
            print("4 - Buscou as URLs relevantes")

            # 5 - Chunking incremental
            quantidade_conteudo = min(20, len(conteudo_valido))
            if quantidade_conteudo == 0:
                raise RuntimeError("Nenhum conteúdo relevante encontrado para chunking.")

            for idx, item in enumerate(conteudo_valido[:quantidade_conteudo]):
                chunks = await loop.run_in_executor(None, chunking, item["conteudo_textual"], item["url"], item["title"])
                chunks_completos.extend(chunks)
                progresso_parcial = 40 + ((idx + 1) / quantidade_conteudo) * 15
                await progresso_passos(progresso_parcial, f"Organizando conteúdo ({idx+1}/{quantidade_conteudo})", cancelar)

            specs["num_chunks"] = len(chunks_completos)
            print("5 - Chunking com overlap executado")

            # 6.1 - Embeddings
            embeddings, metadados = await batch_processing(chunks_completos, embedder_modelo)
            await progresso_passos(62, "Convertendo conhecimento em vetores semânticos", cancelar)
            print("6.1 - Embeddings criados")
            
            if cache_key:
                specs_to_cache = {
                    "num_urls_processadas": specs.get("num_urls_processadas", 0),
                    "num_chunks": specs.get("num_chunks", 0)
                }
                
                dados_para_cache = (chunks_completos, embeddings, metadados, specs_to_cache)
                EXPIRA_SEGUNDOS = 60 * 60 * 6 
                
                salvou_com_sucesso = await loop.run_in_executor(
                    None, 
                    salvar_cache_pickle, 
                    cache_key, 
                    dados_para_cache, 
                    EXPIRA_SEGUNDOS
                )
                
                if salvou_com_sucesso:
                    print(f"SUCESSO: Dados gravados no Redis com a chave: {cache_key}")
                else:
                    print(f"ERRO FATAL: A função salvar_cache_pickle retornou False!")
            
            # 6.2 - Salva os dados do Cache
            if cache_key:
                specs_to_cache = {
                    "num_urls_processadas": specs.get("num_urls_processadas", 0),
                    "num_chunks": specs.get("num_chunks", 0)
                }
                dados_para_cache = (chunks_completos, embeddings, metadados, specs_to_cache)
                
                EXPIRA_SEGUNDOS = 60 * 60 * 6 
                
                await loop.run_in_executor(
                    None, 
                    salvar_cache_pickle, 
                    cache_key, 
                    dados_para_cache, 
                    EXPIRA_SEGUNDOS
                )
                print(f"6.2 - Cache MISS: Dados salvos em cache com a chave: {cache_key}")

        # 6.3 - Criação do DB
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
        print("6.3 - Banco vetorial criado")

        # 7 - Semantic search incremental
        resultados_semanticos = []
        total_queries = len(perguntas_embeddings)
        for idx, p_embedding in enumerate(perguntas_embeddings):
            top_chunks = db_vetorial.similarity_search_by_vector(p_embedding, k=10)
            resultados_semanticos.extend(top_chunks)
            progresso_parcial = 70 + ((idx + 1) / total_queries) * 10
            await progresso_passos(progresso_parcial, f"Buscando respostas ({idx+1}/{total_queries})", cancelar)
        print("7 - Semantic search")

        # 8 - Reranking (síncrono -> executor)
        contexto_queries = " | ".join(perguntas_aprimoradas)
        resultados_ordenados = await loop.run_in_executor(None, reranking, contexto_queries, resultados_semanticos)
        await progresso_passos(90, "Selecionando dados para resposta final", cancelar)
        specs["num_resultados_semanticos"] = len(resultados_ordenados)
        print("8 - Reranking")

        # 9 - Resposta final (async)
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
        print("9 - Resposta final gerada")

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
    
    except Exception as e:
        print(f"ERRO INESPERADO NO PIPELINE: {e}")
        await progresso.put(json.dumps({
            "percentual": 0,
            "etapa": f"Erro interno: {e}",
            "done": True,
            "resultado": None
        }))
        return {"erro": str(e), "resultado": None}




