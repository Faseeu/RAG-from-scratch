"""OpenRouter System One compatibility API, not chat completions."""

from .http_client import HTTPJevClient


class OpenRouterJevClient(HTTPJevClient):
    endpoint = 'https://openrouter.ai/api/v1/systemone'
    key_env = 'OPENROUTER_API_KEY'
    default_model = 'jev-1.13'
