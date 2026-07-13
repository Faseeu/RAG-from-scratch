from storage import load
import string

# import BM25
from rank_bm25 import BM25Okapi
from pprint import pprint


def bm25_search(
    query="meaning of goldilocks\n><?!", top_k: int = 15, filename="RAG.json"
):
    data = load(filename)  # Gives the dict of the VecterDB(here it is 'RAG.json')

    corpus = [vector["chunk"] for vector in data]
    # print(corpus)
    # corpus = remove_puncutation(corpus)
    # print(corpus)
    # print(len(corpus))
    tk_corpus = tokenize(corpus)
    # print(tk)
    # print(len(tk_corpus))

    tk_query = tokenize([query])[0]
    # print(tk_query)
    scores = score(tk_corpus, tk_query)
    # bm25 = BM25Okapi(tk_corpus)
    # scores = bm25.get_scores(tk_query)

    # print(len(scores))
    # print(scores[1])

    score_list = [
        {"score": score, "chunk": chunk} for score, chunk in zip(scores, corpus)
    ]
    # print(score_list)
    scores_sort = sorted(score_list, key=lambda x: x["score"], reverse=True)
    # pprint(scores_sort[:3])
    top_scores = [score["chunk"] for score in scores_sort[:top_k]]
    # print(top_scores)
    return top_scores


def score(tk_corpus, tk_query):
    bm25 = BM25Okapi(tk_corpus)
    scores = bm25.get_scores(tk_query)
    return scores


def tokenize(textlist: list[str]):
    tokenized = [text.lower().split() for text in textlist]
    # print(tokenized)
    tokenized = [remove_puncutation(text) for text in tokenized]

    tokenized = [[x for x in sublist if x != ""] for sublist in tokenized]
    # pprint(tokenized)
    return tokenized


def remove_puncutation(text):
    results = text
    # print(results)

    for char in string.punctuation:
        results = [txt.replace(char, "") for txt in results]

    return results


# bm25_search()
# pprint(bm25_search())
# print(string.punctuation + "\\n")
