# llmlayer.py
from llm.groqclient import GroqClient
from pydantic import BaseModel, ConfigDict
from memory import conMemory


class ResponseStructure(BaseModel):
    model_config = ConfigDict(extra="forbid")
    needs_retrieval: bool
    answer: str | None


layer4 = GroqClient(model="openai/gpt-oss-20b", output_schema=ResponseStructure)

formatted_history = conMemory("load")
formatted_history = "".join(
    str({memory["question"]: memory["answer"]}) for memory in formatted_history
)


def llm_call(query):
    prompt = f"""
    You are the routing brain for a RAG (Retrieval-Augmented Generation) system that answers questions strictly from a specific set of loaded documents. You are the FIRST decision point before any expensive document search happens. Your judgment directly controls cost and correctness — be precise.

    You will receive:
    1. RECENT CONVERSATION HISTORY — up to the last 15 exchanges (question + answer pairs) already processed by this system.
    2. A NEW USER MESSAGE that needs to be classified.

    Decide exactly ONE thing: does answering the new message require a fresh document search, or can it be answered right now without one?

    Set needs_retrieval = FALSE and provide a direct "answer" in these cases:
    - Greetings, farewells, casual filler ("hi", "thanks", "cool", "bye")
    - Questions about the assistant itself: identity, capabilities, limitations, how it works
    - General knowledge, trivia, math, current events — anything clearly unrelated to a document
    - Requests the assistant cannot fulfill: creative writing, code generation, translation, personal/legal/medical advice, real-world actions (sending emails, booking, reminders)
    - Gibberish, empty, or nonsensical input
    - The message is a REPEAT, REPHRASE, or FOLLOW-UP of something already answered in the conversation history — in this case, derive your "answer" directly from the relevant prior answer in the history. Do NOT invent new document facts that aren't already present in the history. If the history doesn't actually contain enough to answer the follow-up, treat it as needing retrieval instead.

    Set needs_retrieval = TRUE and set "answer" to null in these cases:
    - The message asks about specific content, facts, or topics that would plausibly exist in the loaded documents and are NOT already fully answered in the conversation history
    - The message is ambiguous but leans toward being document-related
    - You are uncertain whether the history actually contains the answer

    Hard rules:
    - Never fabricate document content. Only use information that is either common knowledge (for off-topic answers) or explicitly present in the conversation history (for follow-up answers).
    - When genuinely unsure whether retrieval is needed, default to needs_retrieval = TRUE. A wasted search is cheap; a wrong or hallucinated answer is not.
    - Keep "answer" concise — one to three sentences.

    CONVERSATION HISTORY (most recent last):
    {formatted_history}

    NEW USER MESSAGE: "{query}"

    Classify this message and respond in the required structured format.

    """

    response = layer4.generate(prompt)
    validated = ResponseStructure.model_validate_json(response)
    print(validated)
    if validated.needs_retrieval is False:
        return validated.answer
    return None
