# RAG From Scratch

**By Faseeh Ur Rehman — aka [Faseeu](https://github.com/Faseeu)**

A Retrieval-Augmented Generation agent built from the ground up — **no RAG frameworks**. No LangChain, no LlamaIndex. The hybrid retrieval, RRF fusion, reranking, query rewriting, guard layers, conversation memory, and citation verification are all written by hand, and every line is understood.

![Main pipeline](Main_Flowchart.png)

## The query pipeline (V5)

Run `main.py`, pick a collection, and every query walks this path:

1. **Guard preprocessor (4 layers, cheap → expensive)** — `guard/preprocessor.py`
   Exact-match greetings → fuzzy match → cached-FAQ vector search → small-LLM classifier.
   Simple queries ("hey", "who are you?") get answered here without ever hitting the full pipeline.
2. **Contextualization** — `core/contextualize_query.py`
   Rewrites the query into a standalone question using conversation memory, so follow-ups like *"and why does that happen?"* work.
3. **Decomposition** — `llm/decomposer.py`
   Splits the query into independent sub-queries.
4. **Dual query rewriting** — `llm/query_rewriter.py`
   5 semantic rewrites for the vector search + 5 keyword-dense rewrites for BM25 — the two retrievers want *opposite* phrasings.
5. **Hybrid retrieval** — `qdrantDB/retrieve.py` + `search/bm25_search.py`
   Dense retrieval from Qdrant (Snowflake `arctic-embed-s`, 384-dim) plus BM25 lexical search over the corpus.
6. **RRF fusion** — `search/rrf_merge.py`
   Reciprocal-rank fusion merges both result lists into one ranked set.
7. **Cross-encoder rerank** — `search/reranker.py`
   `ms-marco-MiniLM-L-6-v2` re-scores the fused chunks and keeps the best.
8. **Prompt building** — `prompt_builder.py`
   Context chunks + recent conversation memory → final prompt.
9. **Answer generation** — `llm/groqclient.py` + `verify/answerschema.py`
   Groq (`openai/gpt-oss-120b`) streams a **structured** answer (answer + citations), validated with Pydantic.
10. **Citation verification** — `verify/quote_score.py`
    Every cited quote is fuzzy-matched (rapidfuzz) against the chunk it claims to come from, and a score is printed — so hallucinated citations get flagged, not silently accepted.

## Ingestion

![Ingestion flow](Ingest.png)

`qdrantDB/db_ingest.py` → PDF → markdown (`pymupdf4llm`) → token-aware chunking → batch embedding → a Qdrant collection with deterministic UUID5 ids and sanitized collection names.

## Project layout

```
main.py              # entry point — the V5 query pipeline
settings.py          # pydantic-settings: API keys, models, every tunable (.env-aware)
memory.py            # session-based conversation memory (sessions/)
prompt_builder.py    # final prompt assembly (context + memory)
core/                # building blocks: loader, chunker, JSON vector store, retriever
embedding/           # local (sentence-transformers) & Jina embeddings, batch embedding
qdrantDB/            # Qdrant client, ingestion, retrieval
search/              # BM25, RRF fusion, cross-encoder reranking
llm/                 # Groq client, contextualizer, decomposer, query rewriter
guard/               # 4-layer preprocessor (greeting/FAQ fast path)
verify/              # structured answer schema + quote-score citation checks
interface/           # typed ports & contracts (see interface/README.md)
experimental/        # experiments (jev evaluation clients)
utils/               # helpers: sanitize_name, cleanRAG
data/                # greet & FAQ caches, corpus
tests/               # merge-compatibility tests
```

## Getting started

**Prerequisites:** Python 3.12+, [`uv`](https://docs.astral.sh/uv/), Docker (for Qdrant).

```bash
# 1. Install dependencies
uv sync

# 2. Start Qdrant
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# 3. Create your .env (this file is gitignored — never commit it)
echo "GROQ_API_KEY=your-key-here" > .env

# 4. Run
uv run python main.py
```

On the first run there are no collections yet, so it offers to ingest — point it at a PDF (the default corpus is `basic_ai.txt`). After that, pick a collection and ask away. Type `q` to quit.

### Environment variables

| Variable        | Used by                                   | Required               |
| --------------- | ----------------------------------------- | ---------------------- |
| `GROQ_API_KEY`  | all LLM calls (answers, rewriting, guard) | yes                    |
| `HF_TOKEN`     | cross-encoder reranker                    | recommended            |
| `JINA_API_KEY` | `embedding_mode="jina"`, FAQ cache build  | only for Jina mode     |

## Configuration

Every tunable lives in `settings.py` and can be overridden from `.env` (pydantic-settings). Highlights:

| Setting                | Default                                 | Controls                       |
| ---------------------- | --------------------------------------- | ------------------------------ |
| `default_llm_model`    | `openai/gpt-oss-120b`                   | main answer model (Groq)       |
| `router_llm_model`     | `openai/gpt-oss-20b`                    | small routing/rewrite model    |
| `guard_llm_model`      | `openai/gpt-oss-20b`                    | guard-layer classifier         |
| `embedding_model`      | `Snowflake/snowflake-arctic-embed-s`    | local embedder (384-dim)       |
| `embedding_mode`       | `local`                                 | `local` or `jina`              |
| `chunk_size`           | `450`                                   | chunk token budget             |
| `chunk_overlap`        | `70`                                    | chunk overlap                  |
| `retrieval_top_k`      | `15`                                    | candidates per retriever       |
| `retrieval_threshold`  | `0.5`                                   | Qdrant similarity floor        |
| `rrf_merge_top_k`      | `10`                                    | fused results kept             |
| `rerank_top_k`         | `5`                                     | chunks kept after rerank       |
| `rerank_model`         | `cross-encoder/ms-marco-MiniLM-L-6-v2`  | reranker                       |
| `batch_size`           | `128`                                   | embedding batch size           |

`settings.save()` snapshots the tunables to `data/settings.json` (gitignored), which is re-loaded on startup.

## Notes

- Earlier iterations (V1–V4) used a flat JSON vector store — that code lives on in `core/` (`storage.py`, `ingest.py`), and `utils/cleanRAG.py` is a small maintenance script for it.
- Everything generated at runtime — `sessions/`, `qdrant_storage/`, `data/RAG.json`, `conversation_memory.json` — is gitignored on purpose; the repo only carries source and seed data.
- Tests: `uv run pytest`
