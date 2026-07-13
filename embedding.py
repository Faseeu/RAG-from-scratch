import requests

from dotenv import load_dotenv
import os

load_dotenv()  # reads .env file and loads all variables

API_KEY = os.getenv("JINA_API_KEY")


def embed(texts: list[str], task: str = "retrieval.passage") -> list[list[float]]:

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

    return embeddings


# batch_size = 128
# for i in range(len(a)):
