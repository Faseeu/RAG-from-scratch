from core.storage import load
from core.embedding import embed
from core.cosine_similarity import cosine_similarity


def retriever(query, top_k: int = 15):
    chunks = load()

    query_embed = embed([query], "retrieval.query")[0]
    sim: dict[int, float] = {}
    for i, chunk in enumerate(chunks):
        chunk_embed = chunk["embedding"]
        score = cosine_similarity(query_embed, chunk_embed)
        sim[i] = score

    ranked = sorted(sim.items(), key=lambda x: x[1], reverse=True)
    top_chunks = [chunks[i]["chunk"] for i, score in ranked[:top_k]]

    return top_chunks
