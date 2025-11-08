from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from pydantic import BaseModel, Field
from typing import List, Optional

class CampoDinamico(BaseModel):
    nome: str = Field(
        ...,
        description="O nome do campo que deve aparecer na análise final (ex: 'como_funciona', 'impacto_ambiental')."
    )
    descricao: Optional[str] = Field(
        None,
        description="Breve descrição do que o campo representa ou deve conter. Serve como guia para o LLM."
    )

class SchemaDeAnaliseDinamica(BaseModel):
    titulo_da_analise: str = Field(
        ...,
        description="Um título conciso que resume toda a análise baseada na pergunta do usuário."
    )
    resumo_executivo: str = Field(
        ...,
        description="Um resumo curto (máx. 6 frases) da análise, sintetizando a resposta principal."
    )
    campos_dinamicos: List[CampoDinamico] = Field(
        ...,
        description="Lista de campos dinâmicos que descrevem os elementos mais importantes da análise. Cada campo tem 'nome' e opcionalmente 'descricao'."
    )
    fontes_citadas: List[str] = Field(
        default_factory=list,
        description="Lista de URLs ou referências utilizadas como base para gerar a análise. Deve ser vazia ao gerar o metaparser."
    )

class QueryAprimorada(BaseModel):
    query_corrigida: str = Field(
        ...,
        description="Texto original reescrito de forma clara e correta, mantendo o sentido da pergunta."
    )
    query_intencao_resumida: str = Field(
        ...,
        description="Resumo curto da intenção da pergunta, sintetizando o que o usuário quer saber."
    )
    query_tecnica: str = Field(
        ...,
        description="Versão formal e técnica da pergunta, usando linguagem acadêmica apropriada."
    )
    query_simplificada: str = Field(
        ...,
        description="Versão simples da pergunta, explicada de forma acessível para iniciantes."
    )
    tokens_semanticos: List[str] = Field(
        ...,
        description="Lista de palavras-chave e termos semânticos importantes presentes na pergunta."
    )
