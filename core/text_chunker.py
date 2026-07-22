def split_into_chunks(text: str, size: int = 200, overlap: int = 20) -> list[str]:
    chunks: list[str] = []
    words: list[str] = text.split(" ")

    step: int = size - overlap

    i = 0

    while i < len(words):
        # start: int = max(0, i - overlap)
        # end: int = start + size
        start: int = i
        end: int = i + size

        chunk_words: list[str] = words[start:end]
        chunk_text: str = " ".join(chunk_words)

        chunks.append(chunk_text)

        i += step
    return chunks
