"""Independent jev-ai.org gateway, with separate credentials and billing."""

from .http_client import HTTPJevClient


class CommunityJevClient(HTTPJevClient):
    """Selected future decision adapter: internal Evaluation → jev-ai.org →

    EvaluationResult. Credit-limited, not unlimited free; no pipeline wiring or
    fallback.
    """

    endpoint = 'https://jev-ai.org/api/v1/systemone/'
    key_env = 'JEV_API_KEY'
    default_model = 'jev-1.13'
    max_questions = 20
