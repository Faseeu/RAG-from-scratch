import json


def store(chunks_with_vectors, filename="RAG.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(chunks_with_vectors, f)


def load(file="RAG.json"):
    vectorDB = {}
    with open(file, "r", encoding="utf-8") as f:
        vectorDB = json.load(f)
    return vectorDB
