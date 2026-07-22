from core.storage import load
import string

# import BM25
from rank_bm25 import BM25Okapi
# from pprint import pprint


class BM25:
    def __init__(self, filename="data/RAG.json"):
        data = load(filename)
        self.corpus = [vector["chunk"] for vector in data]
        self.tk_corpus = self.tokenize(self.corpus)
        self.bm25 = BM25Okapi(self.tk_corpus)

    def bm25_search(
        self, query="meaning of goldilocks\n><?!", top_k: int = 15, filename="RAG.json"
    ):
        # Gives the dict of the VecterDB(here it is 'RAG.json')

        # corpus = [vector["chunk"] for vector in data]
        # print(corpus)
        # corpus = remove_puncutation(corpus)
        # print(corpus)
        # print(len(corpus))

        # print(tk)
        # print(len(tk_corpus))

        tk_query = self.tokenize([query])[0]
        # print(tk_query)
        scores = self.score(tk_query)
        # bm25 = BM25Okapi(tk_corpus)
        # scores = bm25.get_scores(tk_query)

        # print(len(scores))
        # print(scores[1])

        score_list = [
            {"score": score, "chunk": chunk}
            for score, chunk in zip(scores, self.corpus)
        ]
        # print(score_list)
        scores_sort = sorted(score_list, key=lambda x: x["score"], reverse=True)
        # pprint(scores_sort[:3])
        top_scores = [score["chunk"] for score in scores_sort[:top_k]]
        # print(top_scores)
        return top_scores

    def score(self, tk_query):
        # Very Very sloww
        scores = self.bm25.get_scores(tk_query)
        return scores

    def tokenize(self, textlist: list[str]):
        tokenized = [
            text.lower().split() for text in textlist
        ]  # Decapitalizes the text
        # print(tokenized)
        tokenized = [
            self.remove_puncutation(text) for text in tokenized
        ]  # Removes all punctuation

        tokenized = [
            [x for x in sublist if x != ""] for sublist in tokenized
        ]  # Rempoves empty strings
        # pprint(tokenized)
        return tokenized

    def remove_puncutation(self, text):
        results = text
        # print(results)

        for char in string.punctuation:
            results = [txt.replace(char, "") for txt in results]

        return results


# bm25_search()
# pprint(bm25_search())
# print(string.punctuation + "\\n")
