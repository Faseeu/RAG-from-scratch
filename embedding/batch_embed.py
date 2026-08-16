from embedding.embedding import embed
from settings import settings


def _batch_embed(self, chunks, mode=settings.embedding_mode):
    all_embeddings = []
    for i in range(0, len(chunks), self.batch_size):
        batch: list[str] = chunks[i : i + self.batch_size]
        # batch_embeddings = embed(batch, "retrieval.passage")
        batch_embeddings = embed(batch, mode=mode)
        all_embeddings.extend(batch_embeddings)
    return all_embeddings
