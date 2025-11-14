# sistema-de-pesquisa-web-inteligente

###### Projeto fullstack com pipeline avançado de RAG (Usando query enchantment, metaparser, chunking overlap, batch processing assíncrono, semantic search e reranking), web scraping (tavily), FAISS, embeddings, geração com LLMs e caching otimizado usando Redis, integrado a um backend FastAPI e frontend React com Server-Sent Events (SSE).

O usuário faz uma pergunta e o sistema pesquisa automaticamente na internet, acessando sites relevantes e extraindo as informações mais importantes. Enquanto isso acontece, o backend envia atualizações em tempo real para o frontend, que exibe uma tela de carregamento interativa. No final, o usuário recebe um resumo completo do que foi encontrado, junto com as fontes utilizadas e detaslhes técnicos.

<hr>

### Estrutura do projeto: 
#### FrontEnd: 
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white) ![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=for-the-badge&logo=node.js&logoColor=white)

- **React** + **Vite** para criar a interface SPA *(Single Page Aplication)* e torná-la dinâmica. <br>
- **Talwind CSS** para estilizar o conteúdo.
-  **NodeJS** para rodar o servidor FrontEnd.

#### BackEnd:
![Google Gemini](https://img.shields.io/badge/google%20gemini-8E75B2?style=for-the-badge&logo=google%20gemini&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-5C3EE8?style=for-the-badge&logo=uvicorn&logoColor=white)<br>
![Tavily](https://img.shields.io/badge/Tavily-1042FF?style=for-the-badge)
![Faiss](https://img.shields.io/badge/FAISS-005BBB?style=for-the-badge&logo=Meta&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DC382D.svg?style=for-the-badge&logo=redis&logoColor=white)
![Transformers](https://img.shields.io/badge/Transformers-FFDD00?style=for-the-badge&logo=huggingface&logoColor=black)<br>
![LangChain](https://img.shields.io/badge/-LangChain-000000?style=for-the-badge&logo=langchain&logoColor=white)

- **Google Gemini** + **LangChain** para criar e orquestrar o fluxo inteligente.
- **FastAPI** + **Uvicorn** atuam como comunicação entre o FrontEnd e BackEnd.
- **Tavily** busca e extrai o conteúdo da internet (Web Scraping)
- **FAISS** + **Transformers** servem como mecanismo de vetor-store, armazenando e buscando embeddings executando RAG.
- **Redis** É usado como banco de dados para Caching.

<hr>

### Como utilizar?
Clone o repositório:
```
git clone https://github.com/Developer-Marcos/sistema-de-pesquisa-web-inteligente.git
```

<hr>

**Ativando o FrontEnd**:
 - Navegue até a pasta *frontend*:<br>
```
cd frontend
```

 - Instale as dependências do frontend:<br>
```
npm install
```

 - Inicie o servidor FrontEnd:
```
npm run dev
```
**Cole a URL (link) do local indicado no terminal para acessar o projeto.**

<hr>

**Ativando o BackEnd:**
 - Abra outro terminal e navegue até a pasta *backend*:<br>
```
cd backend
```

 - Instale as dependências do Python: <br>
```
pip install -r requirements.txt
```

- Crie o arquivo .env **dentro da pasta backend** e **adicione a sua API KEY** do Google Gemini e Tavily:<br>    
``` python
GOOGLE_API_KEY = "sua_API_KEY_google"
TAVILY_API_KEY = "sua_API_KEY_tavily"
```

 - Inicie o servidor da API:
```
uvicorn main:app --reload
```

<hr>

###### Opcional mas recomendado

**Ativando o banco de dados Redis:**
-  Baixe o Redis DB do site oficial.
-  Após baixar rode o banco de dados. 

<hr>

**Entre na pagina web e faça a sua pergunta.** <br>
###### O processo pode demorar pela primeira vez, mas por conta do caching, tende a ir ficando mais rapido conforme o uso.

<hr>

#### Fluxo de funcionamento:
<p>O Usuário faz uma pergunta ou escolhe uma das pré definições:</p>

![TelaInicial](images/tela_inicial.png)

<hr>

<p>O sistema vai processar todo o fluxo e receber as informações via SSE:<p/>
 
![TelaCarregamento](images/tela_carregamento.png)

<p>No terminal do backend é possivel ver mais detalhes:</p>

![DetalhesProcessamento](images/fluxo.png)

<hr>

<p>No final a pesquisa é gerada no frontend:</p>

![PesquisaCompleta](images/tela_final.png)

<p>Os detalhes também podem ser vistos:</p>

![Detalhes](images/tela_info.png)

<hr>

###### Mais detalhes podem ser vistos dentro do código.
