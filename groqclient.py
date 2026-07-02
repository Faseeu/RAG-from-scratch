from groq import Groq


class GroqClient:
    def __init__(self, model: str, max_tokens: int = 1000):

        self.client = Groq()
        self.model = model
        self.max_tokens = max_tokens

    def generate(self, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: LLM API failed with message: {str(e)}"
