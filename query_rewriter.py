from groqclient import GroqClient

# from dotenv import load_dotenv
# import os

# load_dotenv()  # reads .env file and loads all variables

# API_KEY = os.getenv("GROQ_API_KEY")


def query_rewriter(query: str, extra_instructions: str, model="openai/gpt-oss-20b"):
    rewriter = GroqClient(model=model)
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
    {extra_instructions}

    """

    improved_query = rewriter.generate(rewriter_prompt)

    return improved_query
