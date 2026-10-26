set shell := ["bash", "-cu"]

chat:
    uv run rag-chat

test:
    PYTHONPATH=src uv run --no-project --with pytest --with pydantic --with pydantic-settings --with python-dotenv --with groq --with requests pytest -q

lint:
    uv run --no-project --with ruff ruff check .

fix:
    uv run --no-project --with ruff ruff check --fix .

build:
    uv build

docker-build:
    docker compose build

docker-up:
    docker compose up -d qdrant

docker-chat:
    docker compose run --rm chat

docker-import:
    docker compose run --rm data-import

docker-logs:
    docker compose logs -f qdrant

docker-down:
    docker compose down

clean:
    rm -rf .pytest_cache .ruff_cache build dist *.egg-info
    find . -type d -name __pycache__ -prune -exec rm -rf {} +
