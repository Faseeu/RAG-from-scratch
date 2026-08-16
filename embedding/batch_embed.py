from embedding.embedding import embed
from settings import settings


def _batch_embed(
    chunks: list[str],
    mode: str = settings.embedding_mode,
    batch_size: int = settings.batch_size,
):
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch: list[str] = chunks[i : i + batch_size]
        # batch_embeddings = embed(batch, "retrieval.passage")
        batch_embeddings = embed(batch, mode=mode)
        all_embeddings.extend(batch_embeddings)
    return all_embeddings
