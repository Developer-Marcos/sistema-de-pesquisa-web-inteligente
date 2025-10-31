from config import LLM
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from parsers import QueryAprimorada


def criar_embedder(chave_api):
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        api_key=chave_api
    )

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
        Dado uma pergunta, você deve gerar 4 versões diferentes da consulta com o objetivo de maximizar tanto precisão quanto cobertura semântica.

        Pergunta: {pergunta}

        Regras:
        - Mantenha fidelidade à intenção original
        - Não invente fatos
        - Nunca devolva respostas, apenas reformulações
        - Saída obrigatória no formato JSON do modelo QueryAprimorada

        Campos:
        - query_corrigida: versão clara e gramaticalmente correta
        - query_intencao_resumida: frase curta explicando o objetivo da busca
        - query_tecnica: versão formal e acadêmica
        - query_simplificada: linguagem simples
        - tokens_semanticos: lista de palavras chave sem stopwords

        Foque em qualidade e clareza semântica.
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

    
def batch_processing(chunks: list, modelo_embedder, tamanho_batch: int = 50) -> tuple[list, list]:
    resultados_embeddings = []
    resultados_metadados = []

    for i in range(0, len(chunks), tamanho_batch):
        batch = chunks[i:i + tamanho_batch]

        texto_batch = [c["page_content"] for c in batch]
        metadados_batch = [c["metadata"] for c in batch]

        batch_embeddings = modelo_embedder.embed_documents(texto_batch)

        resultados_embeddings.extend(batch_embeddings)
        resultados_metadados.extend(metadados_batch)

    return resultados_embeddings, resultados_metadados


from langchain_community.vectorstores import FAISS

from langchain_community.vectorstores import FAISS

from langchain_community.vectorstores import FAISS

def criar_db(embeddings_externos, metadados, chunks, embedder_object):
    text_embeddings = [(c["page_content"], emb) for c, emb in zip(chunks, embeddings_externos)]
    
    db_vetorial = FAISS.from_embeddings(
        text_embeddings=text_embeddings,
        embedding=embedder_object,
        metadatas=metadados
    )
    return db_vetorial

