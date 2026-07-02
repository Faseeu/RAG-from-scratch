def prompt_builder(query, chunks):
    strict = """
    Use ONLY the context provided
    Don't make things up
    If the answer isn't there, say so"""
    rag = "\n\n".join(chunks)
    
    prompt = f"""
    You are a helpful assistant.
    Answer the user's question using ONLY the context provided below.
    If the answer is not in the context, say "I don't know."
    STRICT INSTRUCTIONS\n
    {strict}

    --- CONTEXT ---
    {rag}
    --- END CONTEXT ---
    SER QUESTION:
    {query}

    ANSWER:               

   """

    return prompt
