import json
import string
from rapidfuzz import process, fuzz

filename = "basic_greets.json"
with open(filename, "r") as f:
    hashmap = json.load(f)


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

    result = process.extract(query, hashmap.keys(), scorer=fuzz.ratio)
    sliced = [best for best, score, index in result if int(score) > threshold]
    print(f"RESULTS FROM FUZZY SEARCH: {result}\n Sliced: {sliced}")
    # for best in sliced[0]
    greeting = hashmap[sliced[0]]
    return greeting


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


print(preprocessor(""))
