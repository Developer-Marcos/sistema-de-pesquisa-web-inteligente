from langchain.embeddings.base import Embeddings

class EmbedderWrapper(Embeddings):
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        if hasattr(self.model, "embed_documents"):
            return self.model.embed_documents(texts)
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        if hasattr(self.model, "embed_query"):
            return self.model.embed_query(text)
        return self.model.encode([text], convert_to_numpy=True)[0].tolist()
