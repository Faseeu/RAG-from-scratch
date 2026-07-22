from dotenv import load_dotenv
import os
from sentence_transformers import CrossEncoder

# Load variables from .env
load_dotenv()

# Retrieve the token
token = os.getenv("HF_TOKEN")


model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", token=token)


# scores = model.predict(pairs)  # returns a list of floats, one score per pair


def rerank(
    query: str, chunks: list[str], top_k: int = 3, threshold: int = -5
) -> list[str]:

    pairs = []
    for chunk in chunks:
        pairs.append([query, chunk])
    scores = model.predict(pairs)
    # print(pairs)

    # top_scores = [{i, score} for i, score in enumerate(scores)]
    scores_dict = [
        {"score": score, "chunk": chunk} for score, chunk in zip(scores, chunks) if score > threshold
    ]
    top_sorted = sorted(scores_dict, key=lambda x: x["score"], reverse=True)
    
    print(f"SCORES FROM RERANKER: {top_sorted}")
    top_scores = [chunk["chunk"] for chunk in top_sorted[:top_k]]
    # print(top_scorq
    # es)
    

    return top_scores
