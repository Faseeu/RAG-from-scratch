FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    HF_HOME=/home/rag/.cache/huggingface

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY apps ./apps
COPY data ./data

RUN uv sync --frozen --no-dev \
    && useradd --create-home --uid 10001 rag \
    && mkdir -p "$HF_HOME" \
    && chown -R rag:rag /app /home/rag

USER rag

CMD ["/app/.venv/bin/rag-chat"]
