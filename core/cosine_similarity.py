from math import sqrt

# cosine similarity = A . B / |A| x |B|
# A is a vector (meaning a list of floats)
# B is the same as A
# |A| is magnitude(meaninig it is just the strength)
#  I remember these from high school physics


def cosine_similarity(query_embed, chunk_embed):

    A = query_embed
    B = chunk_embed

    dot_product = sum(a * b for a, b in zip(query_embed, chunk_embed))
    magOfA = magnitude(A)
    magOfB = magnitude(B)
    if magOfA == 0 or magOfB == 0:
        return 0.0

    return dot_product / (magOfA * magOfB)


def magnitude(embed):

    return sqrt(sum(e**2 for e in embed))
