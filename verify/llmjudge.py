from pydantic import BaseModel, ConfigDict

from llm.groqclient import GroqClient


class JudgeStructure(BaseModel):
    model_config = ConfigDict(extra="forbid")
    needs_retry: bool
    reason: str


judge = GroqClient(model="openai/gpt-oss-120b", output_schema=JudgeStructure)


def judge_output(query: str, chunks: list[str], answer: str, citations: list[dict]):
    context = "\n\n".join(f"[chunk {i}]: {chunk}" for i, chunk in enumerate(chunks))
    citations_text = "\n\n".join(
        f' * Cites chunk: {c["chunk_id"]}: "{c["quote"]}' for c in citations
    )
    prompt = f"""
    You are a strict grounding judge for a RAG system. You do NOT answer the user's question.
    Your ONLY job is to verify whether the ANSWER below is fully supported by the CONTEXT below.

    Set needs_retry to TRUE if ANY of these are true:
    - The answer states a fact that does not appear anywhere in the context
    - A citation's quote does not accurately reflect its labeled chunk
    - The answer contains claims with NO citation backing them at all
    - The answer does not actually address the user's query

    Set needs_retry to FALSE only if every claim in the answer is grounded in the
    labeled context AND the query is directly addressed.

    If needs_retry is TRUE, explain EXACTLY which claim is the problem and which
    chunk (if any) actually contains the correct information, so it can be fixed.
    If needs_retry is FALSE, fixes should just be an empty string.

    USER QUERY:
    {query}

    CONTEXT:
    {context}

    CITATIONS PROVIDED BY THE ANSWER:
    {citations_text}

    ANSWER TO JUDGE:
    {answer}
    """

    judge_response = judge.generate(prompt)

    validated_response = JudgeStructure.model_validate_json(judge_response)

    if validated_response.needs_retry is True:
        retrier_prompt = f"""
        You are a post judgement llm in a RAG system
        The older generations had issues and the judge model has passed verdict
        that thye need to be fixed
        Here is what the Judge says needs to be fixed:
        {validated_response.reason}

        Here are the chunks for context
        {chunks}

        Here is the previous output:
        {answer}

        USER QUERY
        {query}
        """
        retrier = GroqClient(model="openai/gpt-oss-20b")

        response = retrier.generate(retrier_prompt)
        return response

    return answer
