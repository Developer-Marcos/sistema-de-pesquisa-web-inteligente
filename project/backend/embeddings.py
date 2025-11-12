from config import LLM
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from embedder_wrapper import EmbedderWrapper
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, CommaSeparatedListOutputParser, JsonOutputParser
from parsers import QueryAprimorada
import asyncio
from typing import List, Dict, Tuple

def criar_embedder():
    modelo_local = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", trust_remote_code=True)
    return EmbedderWrapper(modelo_local)

def chunking(texto: str, url: str, titulo: str, max_chars: int = 500, overlap: int = 200) -> list[dict]:
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

        inicio += max_chars - overlap
        chunk_id += 1

    return chunks

def query_enhancement(pergunta: str):
    prompt_query =("""
            Você é um sistema especializado em reformular consultas para mecanismos de busca e recuperação de informações (RAG).

            Tarefa:
            Dado uma pergunta, gere 4 versões diferentes da consulta para maximizar precisão e cobertura semântica.

            Pergunta: {pergunta}

            Regras:
            - Mantenha fidelidade à intenção original
            - Não invente fatos
            - Não responda a pergunta, apenas reformule
            - A saída deve ser exclusivamente um JSON válido
            - Não inclua texto fora do JSON
            - Não inclua rótulos externos como "QueryAprimorada"
            - Preencha APENAS estes campos:

            Campos:
            - query_corrigida: versão clara e gramaticalmente correta
            - query_intencao_resumida: frase curta com objetivo da busca
            - query_tecnica: versão formal e acadêmica
            - query_simplificada: linguagem simples
            - tokens_semanticos: lista com palavras chave sem stopwords

            IMPORTANTE:
            Retorne somente o JSON com os campos acima, sem explicações, sem Markdown, sem rótulos externos.
    """)

    prompt = PromptTemplate(
        template=prompt_query,
        input_variables=["pergunta"]
    )

    parser = PydanticOutputParser(pydantic_object=QueryAprimorada)

    chain = prompt | LLM | parser

    resultado = chain.invoke({"pergunta": pergunta})

    return [
        resultado.query_corrigida,
        resultado.query_tecnica,
        resultado.query_simplificada,
        " ".join(resultado.tokens_semanticos) if isinstance(resultado.tokens_semanticos, list) else resultado.tokens_semanticos
    ]

async def batch_processing(chunks: List[Dict], modelo_embedder, tamanho_batch: int = 50) -> Tuple[List[List[float]], List[Dict]]:
    resultados_embeddings = []
    resultados_metadados = []

    async def processar_batch(batch: List[Dict]):
        texto_batch = [c.get("page_content", "") for c in batch]
        metadados_batch = [c.get("metadata", {}) for c in batch]

    
        batch_embeddings = await asyncio.to_thread(modelo_embedder.embed_documents, texto_batch)
        return batch_embeddings, metadados_batch

    
    tasks = []
    for i in range(0, len(chunks), tamanho_batch):
        batch = chunks[i:i + tamanho_batch]
        tasks.append(processar_batch(batch))

    resultados = await asyncio.gather(*tasks)

    for batch_embeddings, metadados_batch in resultados:
        resultados_embeddings.extend(batch_embeddings)
        resultados_metadados.extend(metadados_batch)

    return resultados_embeddings, resultados_metadados


def criar_db(embeddings, metadados, chunks, embedder_modelo):
    text_embeddings = [(c["page_content"], emb) for c, emb in zip(chunks, embeddings)]

    db_vetorial = FAISS.from_embeddings(
        text_embeddings=text_embeddings,
        embedding=embedder_modelo,
        metadatas=metadados
    )

    return db_vetorial


def reranking(pergunta: str, resultados_semanticos: list, top_k: int = 5):
    docs_texto = ""
    for idx, doc in enumerate(resultados_semanticos):
        docs_texto += f"\n[Documento {idx}]\n{doc.page_content}\n"

    prompt_template = PromptTemplate(
    template="""
            Você é um reranker para um sistema de busca RAG.

            Pergunta do usuário:
            {pergunta}

            Documentos recuperados:
            {docs_texto}

            Tarefa:
            Classifique os documentos por relevância para responder à pergunta.

            Regras:
            - Retorne apenas uma lista de índices em ordem de relevância
            - Somente números separados por vírgula
            - Não escreva explicações

            Exemplo de resposta: 3, 0, 2, 1

            Resposta:
            """,
    input_variables=["pergunta", "docs_texto"])
    
    parser = CommaSeparatedListOutputParser()
    chain_rerank = prompt_template | LLM | parser
    ranked_indices = chain_rerank.invoke({"pergunta": pergunta,  "docs_texto": docs_texto})

    reranked_docs = [resultados_semanticos[int(i)] for i in ranked_indices[:top_k]]

    return reranked_docs


async def gerar_resposta(contexto, pergunta, schema_gerado, parser: JsonOutputParser):
    prompt_sistema = SystemMessagePromptTemplate.from_template(f"""
Você é um Analista de Dados e Pesquisa de Alta Performance.
Sua tarefa é ler e sintetizar o CONTEXTO fornecido para gerar uma análise objetiva e precisa, em formato JSON de acordo com o schema fornecido.

Regras:

1. Use o CONTEXTO como referência confiável para preencher os campos em 'campos_dinamicos' mas SEM USAR MARKDOWN.
2. Se algum detalhe não estiver no CONTEXTO, complemente com informações confiáveis e relevantes, usando suas próprias palavras.
3. Cada campo deve ser conciso, informativo e explicativo, como se estivesse ensinando o assunto a alguém que quer compreender o tema.
4. Não altere 'titulo_da_analise' nem 'resumo_executivo'.
5. Preencha 'fontes_citadas' usando apenas URLs presentes no CONTEXTO; se não houver, use ["não identificado"].
6. Retorne APENAS o JSON final do schema fornecido.
7. Não inclua texto introdutório, conclusivo, explicações sobre ausência de dados ou Markdown fora do JSON.
""")

    prompt_tarefa = HumanMessagePromptTemplate.from_template("""
    CONTEXTO RECUPERADO:
    {contexto_recuperado}

    Pergunta do Usuário:
    {pergunta}

    Schema para preenchimento:
    {schema_gerado}
    """)

    prompt_final = ChatPromptTemplate.from_messages([prompt_sistema, prompt_tarefa])

    chain_final = prompt_final | LLM | parser

    resultado_raw = await chain_final.ainvoke({
        "contexto_recuperado": contexto,
        "pergunta": pergunta,
        "schema_gerado": schema_gerado
    })

    if not isinstance(resultado_raw, dict):
        resultado = parser.parse(resultado_raw)
    else:
        resultado = resultado_raw

    return resultado


