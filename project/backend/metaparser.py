from config import LLM
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from parsers import SchemaDeAnaliseDinamica

llm = LLM

prompt_metaparser = """Você é um Engenheiro de Estrutura de Análise. Com base na pergunta do usuário, gere **um JSON detalhado com os campos mais relevantes para responder à pergunta**.

Regras:
- Apenas JSON válido do modelo MetaparserDinamico.
- Todos os campos obrigatórios do schema devem ser preenchidos: 'titulo_da_analise', 'resumo_executivo', 'campos_dinamicos'.
- 'campos_dinamicos' deve conter de 3 a 7 campos relevantes, cada um com 'nome' e opcionalmente 'descricao'.
- Transforme o nome de cada campo em um título legível para humanos: substitua '_' por espaços, capitalize corretamente e preserve abreviações ou nomes próprios.
- 'fontes_citadas' deve ser sempre [].
- Não inclua explicações, texto extra ou Markdown.
- Cada campo deve fazer sentido para a pergunta específica.

Exemplo de saída esperada:
{{
  "titulo_da_analise": "Análise detalhada da Fotossíntese",
  "resumo_executivo": "A fotossíntese é o processo pelo qual as plantas convertem luz solar em energia química, essencial para a vida na Terra.",
  "campos_dinamicos": [
    {{"nome": "Processo Biológico", "descricao": "Explicação passo a passo do processo da fotossíntese."}},
    {{"nome": "Importância Ambiental", "descricao": "Impacto da fotossíntese no ecossistema."}},
    {{"nome": "Principais Componentes", "descricao": "Elementos essenciais envolvidos na fotossíntese."}},
    {{"nome": "Curiosidades", "descricao": "Informações interessantes e menos conhecidas sobre o tema."}}
  ],
  "fontes_citadas": []
}}
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

async def criar_metaparser(pergunta):
      metaparser = await chain_criar_metaparser.ainvoke({"pergunta_usuario": pergunta})
      return metaparser


