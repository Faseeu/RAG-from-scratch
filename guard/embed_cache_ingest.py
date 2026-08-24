# embed_cache_ingest.py
import json
import os

from dotenv import load_dotenv

from embedding.batch_embed import _batch_embed
from settings import settings

load_dotenv()  # reads .env file and loads all variables

API_KEY = os.getenv("JINA_API_KEY")

file = settings.embed_cache_store


def load(filename=file):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def store(cache, filename=file):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cache, f)


# def embedder(texts: list[str], task: str = "retrieval.passage"):

#     result = requests.post(
#         url="https://api.jina.ai/v1/embeddings",
#         headers={"Authorization": f"Bearer {API_KEY}"},
#         json={
#             "model": "jina-embeddings-v4",
#             "task": task,
#             "input": texts,
#             "dimensions": 512,
#         },
#     ).json()

#     # print(result)
#     if result["data"][0] is not list:
#         embeddings = result["data"][0]
#     embeddings = [item["embedding"] for item in result["data"]]

#     return embeddings


def ingest_cache():
    data: list[dict] = load()
    queries: list[str] = [piece["query"] for piece in data]
    all_embeddings: list[list[float]] = []
    queries_with_vectors: list[dict] = []

    # for i in range(0, len(queries), batch_size):
    #     batch: list[str] = queries[i : i + batch_size]
    #     batch_embeddings = embed(batch, "retrieval.passage")
    #     all_embeddings.extend(batch_embeddings)

    all_embeddings = _batch_embed(queries)

    for entry, vector in zip(data, all_embeddings):
        queries_with_vectors.append(
            {"query": entry["query"], "embedding": vector, "answer": entry["answer"]}
        )
    # print(len(queries_with_vectors[0]["embedding"]))

    store(queries_with_vectors)


if __name__ == "__main__":
    ingest_cache()
