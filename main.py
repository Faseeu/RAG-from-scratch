from retriever import retriever
from ingest import ingest
from groqclient import GroqClient
from prompt_builder import prompt_builder
from memory import conMemory


def main():
    # print("Hello from rag-from-scratch!")
    # text = load_textfile("./basic_ai.txt")

    # tex = split_into_chunks(text)

    # print(tex)
    # ingest()
    turn = 0
    client = GroqClient(model="llama-3.3-70b-versatile")
    while True:
        turn += 1
        query: str = input("Enter your QUERY: \n")
        if query == "q" or query == "e" or query == "quit" or query == "exit":
            break

        top_chunks = retriever(query)
        print(top_chunks)

        if turn != 1:
            memory = conMemory("load")
        else:
            memory = {}
        prompt = prompt_builder(query, top_chunks, memory)
        # print(prompt)
        response = client.generate(prompt)
        mem = {"question": query, "answer": response}
        conMemory("store", mem)
        print(response)


if __name__ == "__main__":
    main()
