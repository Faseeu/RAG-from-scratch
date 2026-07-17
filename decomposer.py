from groqclient import GroqClient
from baseschema import QueryStructures

decomposer = GroqClient(model="openai/gpt-oss-120b", output_schema=QueryStructures)


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
