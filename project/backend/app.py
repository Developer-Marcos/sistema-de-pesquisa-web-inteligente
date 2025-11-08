from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from processar_dados import processar_dados

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Entrada(BaseModel):
    pergunta: str  

@app.post("/api/processar")
async def processar_pergunta(dados: Entrada):
    try:
        resultado = await processar_dados(dados.pergunta)
        return {"pesquisa": resultado}
    except Exception as e:
        return {"error": f"Erro no processamento: {str(e)}"}
