from core.retriever import retriever
from core.ingest import ingest
from llm.groqclient import GroqClient
from prompt_builder import prompt_builder
from memory import conMemory
from search.bm25_search import BM25
from search.rrf_merge import rrf_merge

from search.reranker import rerank
from llm.query_rewriter import query_rewriter
from guard.preprocessor import preprocessor
from verify.answerschema import AnswerStructure, Citation


# from pprint import pprint
from llm.decomposer import query_decomposer


def main():
    # print("Hello from rag-from-scratch!")
    # text = load_textfile("./basic_ai.txt")

    # tex = split_into_chunks(text)

    # print(tex)
    # ingest()
    turn = 0
    client = GroqClient(model="openai/gpt-oss-120b", output_schema=AnswerStructure)
    bm25 = BM25()

    while True:
        turn += 1
        user_query: str = input("Enter your QUERY: \n")
        if (
            user_query == "q"
            or user_query == "e"
            or user_query == "quit"
            or user_query == "exit"
        ):
            break
        # Here I seperated the vector and BM25 query rewriting because what
        # They require are opposites
        #
        preprocessed = preprocessor(user_query)
        if preprocessed is not None:
            print(f"Response from 4 layers:\n{preprocessed}")
        else:
            decomposed_query = query_decomposer(user_query)
            full_query_chunks = []
            for query in decomposed_query:
                # query = user_query
                vector_query_list = query_rewriter(
                    query,
                    "Optimize for vector search only. Keep it natural, have semantic phrasing (meaning-rich) in all 4 versions",
                )
                bm25_query_list = query_rewriter(
                    query,
                    "Optimize for BM25 search only. keep it precise, keyword-dense phrasing (exact terms) in all 4 versions",
                )
                print(vector_query_list)
                print(bm25_query_list)
                # print(type(vector_query_list))
                # print(repr(vector_query_list))

                # for i, item in enumerate(vector_query_list):
                #     print(i, repr(item), type(item))

                #     if i == 4:
                #         break

                # raise SystemExit
                # HYBRID SEARCH
                vector_chunks = []
                keyword_chunks = []
                for vector_query in vector_query_list:
                    chunk = retriever(vector_query)
                    # print(type(chunk))
                    vector_chunks.append(chunk)
                    print(len(vector_chunks))
                for bm25_query in bm25_query_list:
                    chunk = bm25.bm25_search(bm25_query)
                    # print(type(chunk))
                    keyword_chunks.append(chunk)
                    print(len(keyword_chunks))

                # # why is there a game of thrones refereance in the book.also how would i recover when my coding habits breakdown from trauma or soemthing like addiction
                # print(vector_chunks)
                # print(keyword_chunks)
                all_chunks = vector_chunks + keyword_chunks
                top_chunks = rrf_merge(all_chunks)
                print(f"LENGTH OF TOP CHUNKS: {len(top_chunks)}")
                # print(f"Top Chunks(RRF): {top_chunks}")

                top_chunks = rerank(query, top_chunks)
                # print(vector_chunks)
                # print(keyword_chunks)
                print(f"Top Chunks(ReRanked): {top_chunks}")
                print(f"LENGTH OF TOP CHUNKS(ReRanked): {len(top_chunks)}")

                full_query_chunks.extend(top_chunks)
            if turn != 1:
                memory = conMemory("load")
            else:
                memory = {}
            prompt = prompt_builder(user_query, full_query_chunks, memory)
            # print(prompt)
            resp = client.generate(prompt)
            validated = AnswerStructure.model_validate_json(resp)
            citations_list = []
            for citation in AnswerStructure.citations:
                validated_citation = Citation.model_validate_json(validated.citations)
                citation_dict = {
                    "chunk_id": validated_citation.chunk_id,
                    "quote": validated_citation.quote,
                }
                citations_list.extend(citation_dict)
            response = f"Sources:{citations_list} \nAnswer:{validated.answer}"
            print(user_query)
            mem = {"question": user_query, "answer": response}
            conMemory("store", mem)
            # pprint("Vector Query", vector_query)
            # pprint("BM25 Query", bm25_query)
            print(f"Response:\n{response}")


if __name__ == "__main__":
    main()
