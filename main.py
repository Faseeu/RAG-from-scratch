from core.contextualize_query import contextualize_query

# from core.retriever import retriever
from guard.preprocessor import preprocessor
from llm.decomposer import query_decomposer

# from core.ingest import ingest
from llm.groqclient import GroqClient
from llm.query_rewriter import query_rewriter
from memory import resume_or_create_session
from prompt_builder import prompt_builder
from qdrantDB.db_ingest import Ingest
from qdrantDB.retrieve import get_corpus_from_qdrant, retrieve
from search.bm25_search import BM25
from search.reranker import rerank
from search.rrf_merge import rrf_merge
from verify.answerschema import AnswerStructure
from verify.quote_score import quote_score

# from pprint import pprint


# TODO: V4 and V5
def main():
    # print("Hello from rag-from-scratch!")
    # text = load_textfile("./basic_ai.txt")

    # tex = split_into_chunks(text)

    # print(tex)
    # ingest()
    
    filename = "data/Daniel Kahneman-Thinking, Fast and Slow .pdf"
    Ingest(mode="pdf", filename=filename)
    turn = 0
    client = GroqClient(model="openai/gpt-oss-120b", output_schema=AnswerStructure)
    corpus = get_corpus_from_qdrant()
    bm25 = BM25(corpus=corpus)
    # convo_name = input("What do you want to name this conversation? :\n")
    # ConMemory = ConversationMemory(session_id="1", session_name=convo_name)
    ConMemory = resume_or_create_session()
    while True:
        turn += 1
        memory = ConMemory.load()
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
        preprocessed = preprocessor(user_query, memory)
        if preprocessed is not None:
            print(f"Response from 4 layers:\n{preprocessed}")
        else:
            # memory = ConMemory.load()
            context_query = contextualize_query(user_query, memory)

            decomposed_query = query_decomposer(context_query)  # Had user query before
            full_query_chunks = []
            print(f"RAW QUERY:\n{user_query}")
            print(f"CONTEXTUALIZED QUERY:\n{context_query}")
            print(f"DECOMPOSED QUERIES:\n{decomposed_query}")
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
                    chunk = retrieve(vector_query)
                    # print(type(chunk))
                    vector_chunks.append(chunk)
                    print(len(vector_chunks))
                for bm25_query in bm25_query_list:
                    chunk = bm25.bm25_search(bm25_query)
                    # print(type(chunk))
                    keyword_chunks.append(chunk)
                    print(len(keyword_chunks))

                # print(vector_chunks)
                # print(keyword_chunks)
                all_chunks = vector_chunks + keyword_chunks
                top_chunks = rrf_merge(all_chunks)
                print(f"LENGTH OF TOP CHUNKS: {len(top_chunks)}")
                # print(f"Top Chunks(RRF): {top_chunks}")

                top_chunks = rerank(query, top_chunks)
                # print(vector_chunks)
                # print(keyword_chunks)
                # print(f"Top Chunks(ReRanked): {top_chunks}")
                print(f"LENGTH OF TOP CHUNKS(ReRanked): {len(top_chunks)}")

                full_query_chunks.extend(top_chunks)
            # if turn != 1:
            # memory = conMemory("load")
            memory = ConMemory.load()
            # else:
            #     memory = {}
            prompt = prompt_builder(
                context_query, full_query_chunks, memory
            )  # Had user_query
            # print(prompt)
            resp = client.generate(prompt)
            validated = AnswerStructure.model_validate_json(resp)
            citations_list = []
            citation_verified = []
            for citation in validated.citations:
                # validated_citation = Citation.model_validate(citation)
                citation_dict = {
                    "chunk_id": citation.chunk_id,
                    "quote": citation.quote,
                }
                quote_check = quote_score(
                    citation.quote, full_query_chunks[citation.chunk_id]
                )
                citation_verified.append(quote_check)

                citations_list.append(citation_dict)
            response = f"Sources:{citations_list} \nAnswer:{validated.answer}"
            print(user_query)
            mem = {"question": context_query, "answer": response}  # Had user_query
            # conMemory("store", mem)

            ConMemory.store(mem)
            # pprint("Vector Query", vector_query)
            # pprint("BM25 Query", bm25_query)
            print(f"Response:\n{response}")
            for citations_dict, score in zip(citations_list, citation_verified):
                if score is None:
                    print(f"⚠️ The Checked failed for chunk {citation_dict['chunk_id']}")
                    continue
                print(f"✅ Chunk ID: {citation_dict['chunk_id']} \nScore: {score:.2f}")


if __name__ == "__main__":
    main()
