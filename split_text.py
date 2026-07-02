def split_into_chunks(text: str, size: int = 200, overlap: int = 20) -> list[str]:
    chunks: list[str] = []
    words: list[str] = text.split()

    step = size - overlap

    i = 0

    while i < len(words):
        start = max(0, i - overlap)
        end = start + size

        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append(chunk_text)

        i += step
    return chunks
