from groq import Groq

# from dotenv import load_dotenv
# import os
# import json

# load_dotenv()  # reads .env file and loads all variables

# API_KEY = os.getenv("GROQ_API_KEY")


class GroqClient:
    def __init__(self, model: str, max_tokens: int = 1000, output_schema=None):

        self.client = Groq()
        self.model = model
        self.max_tokens = max_tokens
        self.schema = output_schema

    def generate(self, user_prompt: str) -> str:
        try:
            if self.schema is not None:
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[{"role": "user", "content": user_prompt}],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "schema_name",
                            "strict": True,
                            "schema": self.schema.model_json_schema(),
                        },
                    },
                )
                # return json.loads(response.choices[0].message.content)

            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[{"role": "user", "content": user_prompt}],
                )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error: LLM API failed with message: {str(e)}"
