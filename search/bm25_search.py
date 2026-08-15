import string

# import BM25
from rank_bm25 import BM25Okapi

from core.storage import load
from qdrantDB.retrieve import get_corpus_from_qdrant
from settings import settings

# from pprint import pprint


class BM25:
    def __init__(self, corpus=None, filename=settings.RAG_text_filename):
        if corpus is None:
            data = load(filename)
            self.corpus = [vector["chunk"] for vector in data]
        else:
            self.corpus = corpus
        self.tk_corpus = self.tokenize(self.corpus)
        self.bm25 = BM25Okapi(self.tk_corpus, k1=1.2, b=0.3)

    def bm25_search(self, query="Earth\n><?!", top_k: int = settings.retrieval_top_k):
        # Gives the dict of the VecterDB(here it is 'RAG.json')

        # corpus = [vector["chunk"] for vector in data]
        # print(corpus)
        # corpus = remove_puncutation(corpus)
        # print(corpus)
        # print(len(corpus))

        # print(tk)
        # print(len(tk_corpus))

        tk_query = self.tokenize([query])[0]
        if not tk_query:
            return []
        # print(tk_query)
        scores = self.score(tk_query)
        # bm25 = BM25Okapi(tk_corpus)
        # scores = bm25.get_scores(tk_query)

        # print(len(scores))
        # print(scores[1])

        score_list = [
            {"score": score, "chunk": chunk}
            for score, chunk in zip(scores, self.corpus)
            if score > 0
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
        tokenized = []
        translator = str.maketrans(string.punctuation, " " * len(string.punctuation))

        for text in textlist:
            cleaned_text = text.lower().translate(translator)
            tokens = [token for token in cleaned_text.split() if token]
            tokenized.append(tokens)
        # tokenized = [
        #     text.lower().split()
        # ]  # Decapitalizes the text
        # print(tokenized)
        # tokenized = [
        #     self.remove_puncutation(text) for text in tokenized if text
        # ]  # Removes all punctuation

        # # tokenized = [
        #     [x for x in sublist if x != ""] for sublist in tokenized
        # ]  # Rempoves empty strings
        # pprint(tokenized)
        return tokenized

    def remove_puncutation(self, chunk):
        results = chunk
        # print(results)

        for char in string.punctuation:
            results = [txt.replace(char, "") for txt in results]

        return results


# bm25_search()
# pprint(bm25_search())
# print(string.punctuation + "\\n")
if __name__ == "__main__":
    docs = get_corpus_from_qdrant("The Foundation Trilogy")
    search = BM25(corpus=docs)

    hard_queries = [
        # Test 1: Hyphenation & Special Tokens
        "Visi-Sonor performance on Neotrantor",
        # Test 2: Polysemy & False Positive Weighting
        "The Mule is a physical mutant not an animal",
        # Test 3: Concept / Vocabulary Mismatch (Notice 'Psychohistory' is missing)
        "mathematical prediction of human behavior across galaxy thousands of years",
        # Test 4: Negation Trap
        "Second Foundation is NOT located on Terminus",
        # Test 5: Roman Numerals & Over-saturating Keywords
        "Dagobert IX Emperor on Neotrantor",
    ]

    for q in hard_queries:
        print(f"\n{'=' * 60}\nQUERY: {q}\n{'=' * 60}")
        results = search.bm25_search(query=q, top_k=2)

        if not results:
            print("No results returned.")
            continue

        for i, res in enumerate(results, 1):
            # Print cleanly whether your function returns strings or dicts
            text = res.get("chunk", res) if isinstance(res, dict) else res
            # Preview first 200 chars
            clean_text = text.replace("\n", " ")
            print(f"[{i}] {clean_text[:200]}...\n")
