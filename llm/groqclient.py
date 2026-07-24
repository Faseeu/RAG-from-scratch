from groq import Groq, RateLimitError, APIConnectionError, APIStatusError
import time
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

    def generate(self, user_prompt: str):

        max_retries = 3
        for i in range(max_retries):
            
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

            except RateLimitError as e:
                max_retries -= 1
                time.sleep(2)
                if max_retries == 0:
                    raise RuntimeError("Rate limit persisted after 3 retries") from e

            except APIConnectionError as e:
                raise RuntimeError(
                    f"API CONNECTION ERROR: {str(e)} \n MAYBE TRY AGAIN"
                ) from e
            except APIStatusError as e:
                raise RuntimeError(
                    f"API STATUS ERROR: {str(e)} \n THE PROBLEM SEEMS SEVERE"
                ) from e
            except Exception as e:
                raise RuntimeError(
                    f"Error: LLM API failed with message: {str(e)}"
                ) from e
