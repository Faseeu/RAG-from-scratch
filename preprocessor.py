import json
import string
from rapidfuzz import process, fuzz
from cosine_similarity import cosine_similarity
from embed_cache_ingest import load, embedder, ingest_cache


filename = "basic_greets.json"
with open(filename, "r") as f:
    hashmap = json.load(f)
faq_enteries = load()


def preprocessor(query: str):
    query = remove_puncutation(query)
    simple = exact_match(query)
    if simple is not None:
        return simple
    fuzzy = fuzzysearch(query)
    if fuzzy is not None:
        return fuzzy


def exact_match(query: str):

    if query in hashmap:
        return hashmap[query]
    return None


def fuzzysearch(query: str, threshold=60):

    result = process.extractOne(query, hashmap.keys(), scorer=fuzz.ratio)
    # sliced = [best for best, score, index in result if int(score) > threshold]
    # print(f"RESULTS FROM FUZZY SEARCH: {result}\n Sliced: {sliced}")
    # for best in sliced[0]
    # greeting = hashmap[sliced[0]]
    # return greeting
    return result[0] if result[1] > threshold else None


def vector_search(query: str, threshold=0.65, filename="faq_enteries.json"):
    query_embed = embedder([query], "retrieval.query")[0]

    similarity_scores: dict[int, float] = {}
    # data_embed = [comp["embedding"] for comp in data]

    print(query_embed)
    # print(data_embed)
    for i, faq_entry in enumerate(faq_enteries):
        data_embed = faq_entry["embedding"]
        print(type(data_embed))
        score = cosine_similarity(query_embed, data_embed)
        similarity_scores[i] = score

    ranked = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
    # print(ranked)
    best_index, best_score = ranked[0]
    if best_score > threshold:
        return faq_enteries[best_index]["answer"]
    return None


def remove_puncutation(text):
    results = text.lower().strip()
    # print(results)
    #  METHOD 3
    translation_table = str.maketrans("", "", string.punctuation)
    results = text.translate(translation_table)
    # METHOD 2 AND 3
    # for char in string.punctuation: # COMMON LINE
    #     # print("CHAR FROM PUNTUATION", char)
    #     # for txt in results:
    #     #     print("TXT FROM RESULTS", txt)
    #     #     results = txt.replace(char, "")
    #     #     final += results

    #     #     print(final)
    # METHOD 3
    #     results = "".join(txt.replace(char, "") for txt in results)

    # print(results)

    return results.strip()


# print(preprocessor("yeah makes sense"))
query = "???"
query_search = vector_search(query)

# queries = [query["query"] for query in data]
print(query_search)


# print(queries)
