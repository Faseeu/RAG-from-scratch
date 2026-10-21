# def split_into_chunks(text: str, size: int = 200, overlap: int = 20) -> list[str]:
#     chunks: list[str] = []
#     words: list[str] = text.split(" ")
#     break_points = [
#         r"\n\n",
#         r"\n#",
#         r"CHAPTER",
#         r"(\n\s*)([A-Z][A-Z\s]*)(\n\s*)",
#         r"\n\s*",
#     ]
#     step: int = size - overlap

#     i = 0

#     while i < len(words):
#         # start: int = max(0, i - overlap)
#         # end: int = start + size
#         start: int = i
#         end: int = i + size

#         chunk_words: list[str] = words[start:end]
#         chunk_text: str = " ".join(chunk_words)

#         chunks.append(chunk_text)

#         i += step
#     return chunks
from dataclasses import dataclass


@dataclass
class ChunkPayload:
    page_text: str
    page_no: int
    book_title: str
    source: str
    token_count: int
    confidence: float
    chunk_index: int


import re

from chonkie import TokenChunker

from settings import settings

chunker = TokenChunker(
    tokenizer="gpt2",
    chunk_size=settings.chunk_size,  # tokens
    chunk_overlap=settings.chunk_overlap,  # Keeps overlap to keep the context connected
)


def token_chunk(
    parsed_book,
):

    chunked = []
    chunk_index = 0
    for page in parsed_book:
        text = page.page_text
        clean = re.sub(r"\s+", " ", text).strip()
        chunks = chunker(clean)
        for i, c in enumerate(chunks):
            # chunk_payload = page.copy()

            chunk_payload = ChunkPayload(
                page_text=c.text,
                page_no=page.page_no,
                book_title=page.book_title,
                source=page.source,
                token_count=c.token_count,
                confidence=page.confidence,
                chunk_index=chunk_index,
            )
            chunk_index += 1
            # chunk_payload = {
            #     "page_text": c.text,
            #     "page_no": page["page_no"],
            #     "book_title": page["book_title"],
            #     "source": page["source"],
            #     "token_count": c.token_count,
            #     "confidence": page["confidence"],
            #     "chunk_index": i,
            # }

            chunked.append(chunk_payload)
    # print(chunked)
    print(len(chunked))
    return chunked
