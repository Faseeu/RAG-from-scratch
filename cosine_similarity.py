from math import sqrt


def cosine_similarity(query_embed, chunk_embed):

    A = query_embed
    B = chunk_embed

    dot_product = sum(a * b for a, b in zip(query_embed, chunk_embed))
    magOfA = magnitude(A)
    magOfB = magnitude (B)

    return dot_product / magOfA * magOfB


def magnitude(embed):

    return sqrt(sum(e**2 for e in embed))
