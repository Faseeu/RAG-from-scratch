from retriever import retriever
from ingest import ingest
from groqclient import GroqClient
from prompt_builder import prompt_builder
from memory import conMemory
from bm25_search import bm25_search
from rrf_merge import rrf_merge
from reranker import rerank
from query_rewriter import query_rewriter


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
        # Here I seperated the vector and BM25 query rewriting because what
        # They require are opposites
        #
        vector_query = query_rewriter(
            query,
            "Optimize for vector search only. Keep it natural, have semantic phrasing (meaning-rich)",
        )
        bm25_query = query_rewriter(
            query,
            "Optimize for BM25 search only. keep it precise, keyword-dense phrasing (exact terms)",
        )
        print(vector_query)
        print(bm25_query)
        # HYBRID SEARCH
        vector_chunks = retriever(vector_query)
        keyword_chunks = bm25_search(bm25_query)
        top_chunks = rrf_merge(vector_chunks, keyword_chunks)
        print("Top Chunks(RRF)", top_chunks)

        top_chunks = rerank(query, top_chunks)
        print(vector_chunks)
        print(keyword_chunks)
        print("Top Chunks(ReRanked):", top_chunks)
        if turn != 1:
            memory = conMemory("load")
        else:
            memory = {}
        prompt = prompt_builder(query, top_chunks, memory)
        # print(prompt)
        response = client.generate(prompt)
        mem = {"question": query, "answer": response}
        conMemory("store", mem)
        print("Vector Query", vector_query)
        print("BM25 Query", bm25_query)
        print(f"Response:\n{response}")


if __name__ == "__main__":
    main()
