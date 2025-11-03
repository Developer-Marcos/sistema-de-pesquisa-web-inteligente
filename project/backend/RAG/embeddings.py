from config import LLM
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, CommaSeparatedListOutputParser, JsonOutputParser
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

        Foque em qualidade e clareza semântica.""")

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
    prompt_sistema = SystemMessagePromptTemplate.from_template("""
            Você é um Analista de Dados e Pesquisa de Alta Performance.
            Sua tarefa é ler e sintetizar EXCLUSIVAMENTE o CONTEXTO fornecido para gerar uma análise objetiva e precisa que responda à pergunta do usuário.
            Você DEVE aderir estritamente ao SCHEMA JSON fornecido.
            Não inclua texto introdutório, conclusivo ou Markdown na saída.""")
    
    prompt_tarefa = HumanMessagePromptTemplate.from_template("""
            CONTEXTO RECUPERADO:
            {contexto_recuperado}

            Pergunta do Usuário:
            {pergunta}

            Schema para preenchimento:
            {schema_gerado}
            """)
                
    prompt_final = ChatPromptTemplate.from_messages([prompt_sistema, prompt_tarefa])
    
    chain_resposta = prompt_final | LLM | parser

    pesquisa = await chain_resposta.ainvoke({
        "contexto_recuperado": contexto,
        "pergunta": pergunta,
        "schema_gerado": schema_gerado
    })

    return pesquisa

