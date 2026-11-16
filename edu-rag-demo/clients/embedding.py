"""Embedding：OpenAI 兼容 text-embedding API。"""
from openai import OpenAI
from config import config

class EmbeddingClient:
    def __init__(self):
        api_key = config.OPENAI_API_KEY
        if not api_key or "请填写" in api_key or api_key.startswith("your-"):
            raise ValueError("请配置 OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url=config.OPENAI_BASE_URL)
        self.model = config.EMBEDDING_MODEL
        self.dim = config.EMBEDDING_DIM

    def embed(self, texts: list):
        texts = list(texts)
        if not texts:
            return []
        all_vectors = []
        step = 10
        for i in range(0, len(texts), step):
            batch = texts[i : i + step]
            resp = self.client.embeddings.create(
                model=self.model, input=batch, dimensions=self.dim
            )
            vectors = [item.embedding for item in sorted(resp.data, key=lambda x: x.index)]
            all_vectors.extend(vectors)
        return all_vectors