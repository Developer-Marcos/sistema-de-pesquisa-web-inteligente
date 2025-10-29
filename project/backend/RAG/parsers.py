from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class DefinicaoAtributos(BaseModel):
    nome_tecnico: str = Field(
        ...,
        description="O nome técnico, conciso e em snake_case do campo de dado (ex: 'custo_total' ou 'passos_de_execucao')."
    )

    nome_amigavel: str = Field(
        ...,
        description="O nome que será exibido para o usuário no Front-end (ex: 'Impacto Financeiro' ou 'Onde Encontrar')."
    )

    tipo_de_dado: Literal["string", "number", "boolean", "array_de_strings"] = Field(
        "string",
        description="O tipo de dado esperado para este campo (string, number, boolean ou array_de_strings). Deve ser o tipo mais estrito possível."
    )
    
    instrucao_de_preenchimento: str = Field(
        ...,
        description="Instruções detalhadas para o LLM principal sobre o que exatamente deve ser colocado neste campo. Inclua a citação da fonte no final, por exemplo: (Fonte 1)."
    )

class SchemaDeAnaliseDinamica(BaseModel): 
    titulo_da_analise: str = Field(
        ...,
        description="Um título conciso e informativo, gerado com base na pergunta do usuário (ex: 'Análise de Viabilidade de Energia Solar')."
    )
    
    resumo_executivo: str = Field(
        ...,
        description="Um parágrafo curto (máx. 4 frases) sintetizando a resposta e a conclusão principal da análise. Inclua citações quando necessário (ex: '...é o mais seguro (Fonte 3)')."
    )
    
    campos_dinamicos: List[DefinicaoAtributos] = Field(
        ...,
        description="Uma lista de 3 a 7 objetos que definem os campos de dados mais cruciais e relevantes para responder à pergunta do usuário com uma análise inteligente."
    )
    
    fontes_citadas: List[str] = Field(
        ...,
        description="Uma lista de todas as URLs completas das páginas web que foram usadas como contexto para gerar a análise (ex: 'https://site.com/riscos'). ESTE CAMPO DEVE SER PREENCHIDO NA CHAIN 2."
    )
    
    instrucao_de_tom: Optional[str] = Field(
        None,
        description="Defina o tom de voz da análise final (ex: 'formal e acadêmico' ou 'casual e encorajador')."
    )

