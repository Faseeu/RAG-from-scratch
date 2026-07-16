# def rrf_merge(
#     vector_results: list[str], bm25_results: list[str], k: int = 60, top_k: int = 10
# ) -> list[str]:

#     rrf = {}
#     for i, v in enumerate(vector_results):
#         score = 1 / (k + (i + 1))
#         rrf[v] = score

#     for i, b in enumerate(bm25_results):
#         score = 1 / (k + (i + 1))
#         if b in rrf:
#             old_score = rrf[b]
#             score = old_score + score

#         rrf[b] = score

#     rrf_sort = sorted(rrf.items(), key=lambda x: x[1], reverse=True)
#     top_results = [chunk for chunk, score in rrf_sort[:top_k]]

#     return top_results


def rrf_merge(chunk_lists: list[list[str]], k: int = 60, top_k: int = 10) -> list[str]:

    rrf = {}
    # for i, v in enumerate(vector_results):
    #     score = 1 / (k + (i + 1))
    #     rrf[v] = score
    for search in chunk_lists:
        for i, b in enumerate(search):
            score = _rank(k, i)
            if b in rrf:
                old_score = rrf[b]
                score = old_score + score
            # print(f"SCORES FROM RRF MERGE: {score}")
            rrf[b] = score

    rrf_sort = sorted(rrf.items(), key=lambda x: x[1], reverse=True)
    top_results = [chunk for chunk, score in rrf_sort[:top_k]]

    return top_results


def _rank(k: int, i: int) -> int:
    score = 1 / (k + (i + 1))
    return score
