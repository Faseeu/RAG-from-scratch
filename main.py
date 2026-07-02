from cosine_similarity import cosine_similarity
from embedding import embed
from text_chunker import split_into_chunks
from loader import load_textfile
import re


def main():
    print("Hello from rag-from-scratch!")
    text = load_textfile("./basic_ai.txt")
    cleaned = re.sub(r"\s+", " ", text).strip()
    tex = split_into_chunks(cleaned)
    print(tex)


if __name__ == "__main__":
    main()
