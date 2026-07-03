from retriever import retriever
from ingest import ingest
from groqclient import GroqClient
from prompt_builder import prompt_builder


def main():
    # print("Hello from rag-from-scratch!")
    # text = load_textfile("./basic_ai.txt")

    # tex = split_into_chunks(text)

    # print(tex)
    ingest()
    query: str = input("Plz! Enter your QUERY")
    top_chunks = retriever(query)
    print(top_chunks)
    client = GroqClient(model="llama-3.3-70b-versatile")
    prompt = prompt_builder(query, top_chunks)
    print(prompt)
    print(client.generate(prompt))


if __name__ == "__main__":
    main()
