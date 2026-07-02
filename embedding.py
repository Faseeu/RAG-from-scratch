import requests


def embed(texts: list[str], task: str) -> list[list[float]]:

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

    embeddings = [item["embedding"] for item in result["data"]]

    return embeddings


# batch_size = 128
# for i in range(len(a)):
