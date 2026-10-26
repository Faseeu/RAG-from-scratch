set shell := ["bash", "-cu"]

chat:
    uv run rag-chat

test:
    uv run pytest -q

lint:
    uv run ruff check . && uv run ruff format --check .

fix:
    uv run ruff check --fix . && uv run ruff format .

clean:
    rm -rf .pytest_cache .ruff_cache build dist *.egg-info
    find . -type d -name __pycache__ -prune -exec rm -rf {} +
