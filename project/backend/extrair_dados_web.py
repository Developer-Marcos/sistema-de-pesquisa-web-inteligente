from langchain_tavily import TavilySearch
from urllib.parse import urlparse
import httpx
import trafilatura
import asyncio
from langsmith import traceable
from typing import List, Dict, Optional

@traceable(run_type="retriever", name="Tavily buscador de sites")
def buscar_urls(pergunta: str, api_key: str, max_resultados: int = 25) -> List[str]:
      tavily_search_tool = TavilySearch(
      tavily_api_key = api_key,
      max_results = max_resultados
      )

      pesquisa_web = tavily_search_tool.run(pergunta)
      urls_filtradas = []
      for item in pesquisa_web['results']:
            url = item['url']
            parsed = urlparse(url)
            if ("youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc):
                  continue
            if url.lower().endswith((".pdf", ".mp3", ".mp4", ".avi", ".mov", ".wmv")):
                  continue
            urls_filtradas.append(url)

      return urls_filtradas


limite = asyncio.Semaphore(3)

async def baixar_conteudo(url: str) -> dict[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    async with limite:
        for tentativa in range(2):
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(15.0),
                    headers=headers,
                    follow_redirects=True
                ) as client:
                    
                    resposta = await client.get(url)

                    if not (200 <= resposta.status_code < 300):
                        print(f"Falha {resposta.status_code} em {url}")
                        continue

                    conteudo_textual = trafilatura.extract(resposta.text)
                    metadata = trafilatura.extract_metadata(resposta.text)

                    titulo = metadata.title if metadata and metadata.title else "Sem título"

                    return {
                        "url": url,
                        "conteudo_textual": conteudo_textual or "",
                        "title": titulo
                    }

            except (httpx.TimeoutException, httpx.NetworkError):
                await asyncio.sleep(1.5 ** tentativa)

            except Exception:
                break

        return {"url": url, "conteudo_textual": "", "title": "Sem título"}


@traceable(run_type="tool", name="Trafiladura extrator de conteudo dos sites buscados")
async def extrair_conteudo(urls: List[str]) -> List[Dict[str, str]]:
    tarefas = [baixar_conteudo(url) for url in urls] 
    resultados = await asyncio.gather(*tarefas)

    return resultados
