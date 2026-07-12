from sentence_transformers import CrossEncoder


model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


# scores = model.predict(pairs)  # returns a list of floats, one score per pair


def rerank(query: str, chunks: list[str], top_k: int = 3) -> list[str]:
    
    pairs = []
    for chunk in chunks:
        pairs.append([query, chunk])
    scores = model.predict(pairs)

    print(scores)