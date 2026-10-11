"""Direct TypeSafe API; requires its own TypeSafe credentials."""

from .http_client import HTTPJevClient


class OfficialJevClient(HTTPJevClient):
    endpoint = 'https://api.typesafe.ai/v1/systemone'
    key_env = 'TYPESAFE_API_KEY'
    default_model = 'jev-latest'
