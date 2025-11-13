import redis
import json
import pickle
import os
import hashlib

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_cliente = None


def gerar_chave_cache_por_topicos(topicos: list[str]) -> str:
    if not topicos:
        return None

    topicos_normalizados = sorted([t.lower().strip() for t in topicos])
    topicos_str_key = "|".join(topicos_normalizados)
    hash_chave = hashlib.md5(topicos_str_key.encode('utf-8')).hexdigest()
    
    return f"pipeline_data:{hash_chave}"

def conectar_redis():
    global redis_cliente
    try:
        redis_cliente = redis.StrictRedis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=False
        )
        redis_cliente.ping()
        print("Conectado ao Redis com sucesso.")
    except Exception as e:
        redis_cliente = None
        print(f"Redis não disponível, cache desativado. Motivo: {e}")

conectar_redis()

def salvar_cache_pickle(chave: str, valor, expira_segundos: int = None):
    if not redis_cliente:
        return False
    try:
        valor_serializado = pickle.dumps(valor)
        redis_cliente.set(chave, valor_serializado, ex=expira_segundos)
        return True
    except Exception as e:
        print(f"Erro ao salvar cache pickle: {e}")
        return False

def obter_cache_pickle(chave: str):
    if not redis_cliente:
        return None
    try:
        valor_serializado = redis_cliente.get(chave)
        if valor_serializado:
            return pickle.loads(valor_serializado)
        return None
    except Exception as e:
        print(f"Erro ao obter cache pickle: {e}")
        return None

def salvar_cache_json(chave: str, valor: dict, expira_segundos: int = None):
    if not redis_cliente:
        return False
    try:
        redis_cliente.set(chave, json.dumps(valor), ex=expira_segundos)
        return True
    except Exception as e:
        print(f"Erro ao salvar cache JSON: {e}")
        return False

def obter_cache_json(chave: str):
    if not redis_cliente:
        return None
    try:
        valor = redis_cliente.get(chave)
        return json.loads(valor.decode('utf-8')) if valor else None
    except Exception as e:
        print(f"Erro ao obter cache JSON: {e}")
        return None

def deletar_cache(chave: str):
    if not redis_cliente:
        return False
    try:
        redis_cliente.delete(chave)
        return True
    except Exception as e:
        print(f"Erro ao deletar cache: {e}")
        return False

def limpar_todo_cache():
    if not redis_cliente:
        return False
    try:
        redis_cliente.flushdb()
        print("Cache limpo com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao limpar cache: {e}")
        return False