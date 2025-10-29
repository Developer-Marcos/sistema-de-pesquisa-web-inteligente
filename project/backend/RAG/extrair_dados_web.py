from langchain_tavily import TavilySearch
from urllib.parse import urlparse
import httpx
import trafilatura
import asyncio

from typing import List, Dict, Optional

def buscar_urls(pergunta: str, api_key: str, max_resultados: int = 5) -> List[str]:
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
async def baixar_conteudo(url: str) -> Dict[str, str]:
    """
    Baixa o conteúdo textual de uma URL, com User-Agent e controle de paralelismo.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    async with limite:
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
                resposta = await client.get(url)
                # Se bloqueado, retorna string vazia
                if resposta.status_code != 200:
                    print(f"Não foi possível acessar {url}: {resposta.status_code}")
                    return {"url": url, "conteudo_textual": ""}
                
                conteudo_textual = trafilatura.extract(resposta.text)
                if not conteudo_textual:
                    conteudo_textual = ""
                
                return {"url": url, "conteudo_textual": conteudo_textual}
        except Exception as e:
            print(f"Erro ao processar {url}: {e}")
            return {"url": url, "conteudo_textual": ""}

async def extrair_conteudo(urls: List[str]) -> List[Dict[str, str]]:
      extracao = [baixar_conteudo(url) for url in urls]
      resultados = await asyncio.gather(*extracao)

      return resultados