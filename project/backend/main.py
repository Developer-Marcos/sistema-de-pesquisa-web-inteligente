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

# Task global de processamento
process_task: asyncio.Task | None = None

@app.post("/abort")
async def abort():
    global process_task
    if process_task and not process_task.done():
        process_task.cancel()
        return {"status": "cancelamento solicitado"}
    return {"status": "nenhum processamento ativo"}

@app.get("/stream")
async def stream():
    async def event_generator():
        while True:
            try:
                msg = await asyncio.wait_for(progresso.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            yield f"data: {msg}\n\n"

            try:
                data = json.loads(msg)
                if data.get("done") is True:
                    if not resultado_final.empty():
                        resultado = await resultado_final.get()
                        final_msg = json.dumps({
                            "done": True,
                            "resultado": resultado
                        })
                        yield f"data: {final_msg}\n\n"
                    break
            except (json.JSONDecodeError, KeyError):
                continue

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/processar")
async def processar_pergunta(dados: Entrada):
    global process_task

    # Limpa filas antigas
    while not progresso.empty():
        progresso.get_nowait()
    while not resultado_final.empty():
        resultado_final.get_nowait()

    # Cria a task global de processamento
    process_task = asyncio.create_task(processar_dados(dados.pergunta, lambda: False))

    return {"status": "processamento iniciado"}
