import json
from settings import settings

def store(chunks_with_vectors, filename="data/RAG.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(chunks_with_vectors, f)


def load(file=settings.rag_filename):
    vectorDB = {}
    with open(file, "r", encoding="utf-8") as f:
        vectorDB = json.load(f)
    return vectorDB
