import requests
import numpy as np


def embed(texts: list[str], task: str) -> list[list[float]]:

    result = requests.post(
        url="https://api.jina.ai/v1/embeddings",
        headers={"Authorization": "Bearer YOUR_KEY"},
        json={
            "model": "jina-embeddings-v4",
            "task": task,
            "input": texts,
            "dimensions": 512,
        },
    ).json()

    return 
