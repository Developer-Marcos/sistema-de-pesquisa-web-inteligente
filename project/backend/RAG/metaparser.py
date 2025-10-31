from config import LLM
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from parsers import SchemaDeAnaliseDinamica

llm = LLM

prompt_metaparser = """Você é um Engenheiro de Esquemas de Dados de IA. Sua única e exclusiva função é definir a estrutura de dados (schema) mais útil para a análise solicitada pelo usuário. Você deve agir como um tradutor de intenção para estrutura de dados.

Regras de Formato Rigorosas:
Você DEVE aderir estritamente à estrutura de dados definida. Não inclua NENHUM texto explicativo, introdutório, conclusivo, ou qualquer tipo de Markdown (como ```json) antes, dentro ou depois da saída. Gere APENAS o objeto JSON que preenche o esquema.

Requisitos Específicos para Preenchimento dos Atributos:
O campo 'titulo_da_analise' deve ser conciso e cobrir todo o escopo da pergunta.
O campo 'resumo_executivo' deve ser uma síntese da resposta esperada (máx. 4 frases).
Cada objeto em 'campos_dinamicos' DEVE ter um 'nome_tecnico' em snake_case e uma 'instrucao_de_preenchimento' clara para o LLM principal.
Escolha um 'tipo_de_dado' apropriado para cada atributo (string, number, boolean ou array_de_strings).
Defina o 'instrucao_de_tom' com um tom ideal para a análise deste tópico específico.
[REGRA CRÍTICA]: O campo 'fontes_citadas' DEVE ser retornado como uma lista vazia ([]).

Saída Exigida:
Gere o objeto JSON final, preenchendo todos os campos da DynamicAnalysisSchema, com base na pergunta do usuário.
"""
prompt_funcao = """Contexto da Tarefa:
Analise a pergunta do usuário e preencha o JSON da 'DynamicAnalysisSchema' com os campos de análise mais cruciais (entre 3 e 7 campos).

Pergunta do Usuário:
"{pergunta_usuario}"
"""

system_message_prompt = SystemMessagePromptTemplate.from_template(prompt_metaparser)
human_mensage_prompt = HumanMessagePromptTemplate.from_template(prompt_funcao)

prompt_final = ChatPromptTemplate.from_messages([
      system_message_prompt,
      human_mensage_prompt
])

parser = JsonOutputParser(pydantic_object=SchemaDeAnaliseDinamica)

chain_criar_metaparser = prompt_final | llm | parser

def criar_metaparser(pergunta):
      metaparser = chain_criar_metaparser.invoke({"pergunta_usuario": pergunta})
      return metaparser


