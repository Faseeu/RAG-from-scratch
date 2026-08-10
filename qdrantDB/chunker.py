def split_into_chunks(text: str, size: int = 200, overlap: int = 20) -> list[str]:
    chunks: list[str] = []
    words: list[str] = text.split(" ")
    break_points = [
        r"\n\n",
        r"\n#",
        r"CHAPTER",
        r"(\n\s*)([A-Z][A-Z\s]*)(\n\s*)",
        r"\n\s*",
    ]
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


import re

from chonkie import TokenChunker


def token_chunk(
    parsed_book,
):

    chunker = TokenChunker(
        tokenizer="gpt2",
        chunk_size=512,  # tokens
        chunk_overlap=70,  # Keeps overlap to keep the context connected
    )
    chunked = []
    for page in parsed_book:
        text = page["page_text"]
        clean = re.sub(r"\s+", " ", text).strip()
        chunks = chunker(clean)
        for i,c in enumerate(chunks):
            chunk_payload = page.copy()
            chunk_payload["page_text"] = c.text
            chunk_payload["token_count"] = c.token_count
            chunk_payload["chunk_index"] = i
            chunked.append(chunk_payload)
    print(chunked)
    print(len(chunked))
    return chunked
