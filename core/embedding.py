import os

import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
load_dotenv()  # reads .env file and loads all variables

API_KEY = os.getenv("JINA_API_KEY")


def embed(
    texts: list[str], task: str = "retrieval.passage", mode="jina"
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

        if result["data"][0] is not list:
            embeddings = result["data"][0]
        embeddings = [item["embedding"] for item in result["data"]]
        import time

        time.sleep(10)
        return embeddings
    elif mode == "local":
        embeddings = model.encode(texts)

        return [embeddings]


# batch_size = 128
# for i in range(len(a)):
# batch = ["What is the meaning of everything","WHat is","yooo", "what the heck"]
# batch_embeddings = embed(batch, mode="local")
# print(batch_embeddings[0])
