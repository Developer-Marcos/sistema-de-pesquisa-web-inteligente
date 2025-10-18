from embeddings import transformar_em_embedding
from metaparser import criar_metaparser

pergunta = "Como funciona o mercado cripto?" # pergunta
# pergunta_embedding = transformar_em_embedding(pergunta) # Pergunta vira embeddings

print(criar_metaparser(pergunta))

