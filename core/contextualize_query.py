from llm.groqclient import GroqClient

contextualizer = GroqClient(model="openai/gpt-oss-20b")


def contextualize_query(query: str, history: list[dict]):
    last_n = history[-5:]

    if last_n:
        formatted_history = "\n\n".join(
            f"Q{i} : {memory['question']}\nA{i}: {memory['answer']}"
            for i, memory in enumerate(last_n)
        )
    else:
        formatted_history = "No prior conversation history."
    prompt = f"""
    You are a query rewriting assistant. You will be given recent conversation
    history (previous questions and answers) and a NEW user message that may be
    vague, incomplete, or rely on references to earlier turns (e.g. "the second
    one", "that", "what about it").

    Your job: rewrite the NEW message into a single, fully self-contained question
    that means the same thing, but no longer depends on the history to be understood.

    Rules:
    - Output ONLY the rewritten question. No explanation, no preamble, no quotes,
    no "here's the rewritten question" — just the question itself.
    - If the NEW message is already self-contained and doesn't rely on history,
    return it EXACTLY unchanged.
    - If the NEW message is unrelated to the history (a new topic), return it
    EXACTLY unchanged. Do NOT force a connection to history that isn't there.
    - Do not answer the question. Do not add facts that aren't implied by the
    history or the new message — only resolve references, never invent new content.
    - If there is no history, return the new message EXACTLY unchanged.
    History:
    {formatted_history}

    New message: {query}

    Rewritten standalone question:
    """

    response = contextualizer.generate(prompt)
    if not response or not response.strip():
        return query
    print("Query Contextualized")
    return response.strip()
