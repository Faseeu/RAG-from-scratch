from rag.query.contextualize import contextualize_query
from rag.ingest.registry import collections_index

# from core.retriever import retriever
from rag.query.guard.preprocessor import preprocessor
from rag.adapters.llm.decomposer import query_decomposer

# from core.ingest import ingest
from rag.adapters.llm.groqclient import GroqClient
from rag.adapters.llm.query_rewriter import query_rewriter
from rag.memory.conversation import MemTurn, resume_or_create_session
from rag.generation.prompt import prompt_builder
from rag.retrieval.dense import get_corpus_from_qdrant, retrieve
from rag.retrieval.sparse import BM25
from rag.retrieval.fusion import rrf_merge
from rag.config import settings
from rag.verify.answerschema import AnswerStructure
from rag.verify.quote_score import quote_score

# from pprint import pprint


# TODO: V5
def main():
    # print("Hello from rag-from-scratch!")
    # text = load_textfile("./basic_ai.txt")

    # tex = split_into_chunks(text)

    # print(tex)
    # ingest()
    filename = "data/Daniel Kahneman-Thinking, Fast and Slow .pdf"
    settings.filename = filename
    collections = collections_index.list_collections()
    if not collections:
        print("No collections found. Did you run ingest()?")
        ingest_choice = input(
            "DO you want to ingest a file? \nWrite y if yes, any other key = no: "
        )
        if ingest_choice.lower().strip() == "y":
            from rag.ingest.indexer import Ingest

            Ingest()
            collections = collections_index.list_collections()
        else:
            return

    choice = input("Choose a collection name:- \nEnter the number for it:")
    c = int(choice)
    if c < 0 or c >= len(collections):
        print(f"Invalid choice. Must be 0–{len(collections) - 1}")
        return

    user_choice = collections[c]
    settings.collection_name = user_choice

    # Ingest()
    turn = 0
    client = GroqClient(
        model="openai/gpt-oss-120b", stream=True, output_schema=AnswerStructure
    )
    corpus = get_corpus_from_qdrant()
    bm25 = BM25(corpus=corpus)
    # convo_name = input("What do you want to name this conversation? :\n")
    # conversation_memory = ConversationMemory(session_id="1", session_name=convo_name)
    conversation_memory = resume_or_create_session()
    from rag.retrieval.rerank import rerank

    while True:
        turn += 1
        memory = conversation_memory.load()
        user_query: str = input("Enter your QUERY: \n")
        if (
            user_query == "q"
            or user_query == "e"
            or user_query == "quit"
            or user_query == "exit"
        ):
            break
        if (
            user_query == ""
            or user_query == " "
            or user_query is None
            or not user_query.strip()
        ):
            continue
        if not user_query.strip():
            continue
        # Here I seperated the vector and BM25 query rewriting because what
        # They require are opposites
        #
        preprocessed = preprocessor(user_query, memory)
        if preprocessed is not None:
            print(f"Response from 4 layers:\n{preprocessed}")
        else:
            # memory = conversation_memory.load()
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
                    "Optimize for vector search only. Keep it natural, have semantic phrasing (meaning-rich) in all 5 versions (including the original)",
                )
                bm25_query_list = query_rewriter(
                    query,
                    "Optimize for BM25 search only. keep it precise, keyword-dense phrasing (exact terms) in all 5 versions (including the original)",
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
                    vector_chunks.append([c.text for c in chunk])
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
            memory = conversation_memory.load()
            # else:
            #     memory = {}
            prompt = prompt_builder(
                context_query, full_query_chunks, memory
            )  # Had user_query
            # print(prompt)
            resp = client.generate(prompt)
            # GroqClient prints streamed tokens and returns the completed string.
            # Do not replay that string character-by-character here.
            validated = AnswerStructure.model_validate_json(resp)
            citations_list = []
            citation_verified = []
            for citation in validated.citations:
                # validated_citation = Citation.model_validate(citation)

                citation_dict = {
                    "chunk_id": citation.chunk_id,
                    "quote": citation.quote,
                }
                if 0 <= citation.chunk_id < len(full_query_chunks):
                    quote_check = quote_score(
                        citation.quote, full_query_chunks[citation.chunk_id]
                    )
                else:
                    quote_check = None
                citation_verified.append(quote_check)

                citations_list.append(citation_dict)
            response = f"Sources:{citations_list} \nAnswer:{validated.answer}"
            print(user_query)
            # mem = {"question": context_query, "answmer": response}  # Had user_query
            # conMemory("store", mem)
            mem = MemTurn(question=context_query, answer=response)

            conversation_memory.store(mem)
            # pprint("Vector Query", vector_query)
            # pprint("BM25 Query", bm25_query)

            print(f"Response:\n{response}")
            for citations_dict, score in zip(citations_list, citation_verified):
                if score is None:
                    print(
                        f"⚠️ The Checked failed for chunk {citations_dict['chunk_id']}"
                    )
                    continue
                print(f"✅ Chunk ID: {citations_dict['chunk_id']} \nScore: {score:.2f}")


if __name__ == "__main__":
    main()
