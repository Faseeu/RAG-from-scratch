from llm.groqclient import GroqClient
from llm.queryschema import QueryStructures

decomposer = GroqClient(model="openai/gpt-oss-20b", output_schema=QueryStructures)


def query_decomposer(query):  # SUB QUERY DECOMPOSITION
    prompt = f"""
    You are a query decomposer.

    Determine whether the user's query contains multiple UNRELATED intents 
    or a single coherent question.

    Rules:
    - "Unrelated" means the sub-questions could be asked in completely 
    separate conversations with no loss of meaning.
    - A question that compares, contrasts, or connects two things 
    ("difference between X and Y", "how does X relate to Y") is ONE 
    question, not two. Do NOT split these.
    - Each sub-query you return must be fully self-contained — it should 
    make complete sense on its own without needing the other sub-queries 
    for context.
    - If the query is a single question, return it unchanged.
    - Do not add, invent, or answer anything. Only split or preserve.

    HERE IS THE USER QUERY:
    {query}
    """

    broken_query = decomposer.generate(prompt)
    validated_query = QueryStructures.model_validate_json(broken_query)

    return validated_query.query


if __name__ == "__main__":
    response = query_decomposer(
        "How do i make sure i act on the goldilocks principle. Also how do i apply the method the japanese factories use to maximize productivity. Also suggest me a new method to build a strong identity daily."
    )
    print(response)
    print(type(response))
    print(len(response))
    for r in response:
        print(type(r), repr(r))
