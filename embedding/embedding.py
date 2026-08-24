import os

import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from settings import settings

load_dotenv()  # reads .env file and loads all variables

API_KEY = os.getenv("JINA_API_KEY")
model = SentenceTransformer(settings.embedding_model)


def embed(
    texts: list[str], task: str = "retrieval.passage", mode=settings.embedding_mode
) -> list[list[float]]:
    if mode == "jina":
        result = requests.post(
            url="https://api.jina.ai/v1/embeddings",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "jina-embeddings-v4",
                "task": task,
                "input": texts,
                "dimensions": 512,
            },
        ).json()
        # print(result)

        # if result["data"][0] is not list:
        #     embeddings = result["data"][0]
        if "data" not in result:
            raise RuntimeError(f"Jina error: {result}")

        embeddings = [item["embedding"] for item in result["data"]]

        return embeddings
    elif mode == "local":
        prompt_name = "query" if task == "retrieval.query" else None

        embeddings = model.encode(texts, prompt_name=prompt_name).tolist()

        return embeddings


# batch_size = 128
# for i in range(len(a)):
# batch = ["What is the meaning of everything","WHat is","yooo", "what the heck"]
# batch_embeddings = embed(batch, mode="local")
# print(batch_embeddings[0])
