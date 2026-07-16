from groqclient import GroqClient
from baseschema import QueryStructures
# from dotenv import load_dotenv
# import os

# load_dotenv()  # reads .env file and loads all variables

# API_KEY = os.getenv("GROQ_API_KEY")


def query_rewriter(query: str, extra_instructions: str, model="openai/gpt-oss-20b"):
    imp_instructions = """
    Create the query in 4 different versions
    The goal is to diversify the query
    Think of it like asking 4 different people to search for the same thing, each with a different mindset. 
    You're not changing what the user wants.
    You're changing the lens

    - Rephrase/Paraphrase:  Same question, different words (synonyms, different sentence structure)
    - Broaden(Zoom out):    Make the query more general/high-level
    - Narrow (zoom in):     Make the query more specific — add assumed detail
    - Perspective shift:    Ask it as if from a different angle e.g. "what would the answer look like", or a related sub-topic/assumption
    """
    rewriter = GroqClient(model=model, output_schema=QueryStructures)
    rewriter_prompt = f"""
    Rewrite the given query to make it more suitable for 
    - RAG

    Keep it concise. 
    Dont write any preamble.
    Dont write anything besides the query
    Never ever add any other sort of text or "```" around the query
    Make sure to keep it concise.
    Never add thngs like "Sure! Here's a rewritten version:"
    No need for greetings or goodbyes or his hellos
    Be cold and highly precise.
    Never add anything unecessary.
    Here is the QUERY:
    {query}
    Very Important instructions:
    {imp_instructions}
    {extra_instructions}

    """

    improved_query = rewriter.generate(rewriter_prompt)
    # print(improved_query)
    validate = QueryStructures.model_validate_json(improved_query)

    return validate.query
