from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from processar_dados import processar_dados
from fila_global import progresso, resultado_final
import asyncio
import json

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

@app.get("/stream")
async def stream():
    async def event_generator():
        while True:
            msg = await progresso.get()     # recebe progresso (JSON string)
            yield f"data: {msg}\n\n"

            data = json.loads(msg)

            # Se chegou no final da pipeline
            if data.get("done") is True:
                resultado = await resultado_final.get()

                final_msg = json.dumps({
                    "done": True,
                    "resultado": resultado
                })

                yield f"data: {final_msg}\n\n"
                break
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/processar")
async def processar_pergunta(dados: Entrada):
    while not progresso.empty():
        progresso.get_nowait()
    while not resultado_final.empty():
        resultado_final.get_nowait()
 
    asyncio.create_task(processar_dados(dados.pergunta))

    return {"status": "processamento iniciado"}
