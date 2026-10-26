# Interface boilerplate

See [FINISHING_PLAN.md](FINISHING_PLAN.md) for the current implementation
checklist, community-only Jev policy, model reuse rules and stopping criteria.
The checklist explicitly separates completed scaffolding from pending behavior.

These contracts and boundary models remain scaffolding; they do not orchestrate or alter the active ingestion and retrieval pipeline. The live Groq adapter accepts both its historical string prompt and a `GenerationRequest`, but the rest of the new contract conversions are not wired into the pipeline.

- `boundary.py`: Pydantic models for external inputs and outputs.
- `data.py`: dataclasses for internal function-to-function data.
- `contracts.py`: abstract vector DB, AI client, PDF loader, chunker and embedder.
- `composition.py`: dependencies a future ingestion service can receive.

Intended flow: external payload → Pydantic validation → internal dataclass →
application functions → dataclass → Pydantic serialization → external service.
Conversions are deliberately not implemented. Primitive results such as bool
and None need no wrapper. Lists contain internal dataclasses.

`AIClient.generate` describes a dataclass request/result. `GroqClient.generate`
accepts either a raw prompt or `GenerationRequest`, preserving the CLI's string
call and raw-text response. It does not yet wrap responses in `GenerationResult`,
so the typed port is not fully integrated into the main pipeline. Model, token
limit and structured-output schema remain adapter configuration.

## Blind spots / decisions before implementation

1. **External means both directions.** AI prompts/replies, embedding requests,
   query vectors, and search results cross boundaries too. Their basic models
   are included. Collection administration, scroll wire envelopes, provider
   error envelopes, and persisted registry/memory schemas still need decisions
   when adapters are approved; this is not a complete provider wire protocol.
2. **Document transport.** `DocumentInput` assumes a file reference, matching
   current loading. Upload bytes, URLs, file size/type limits, path permissions,
   and OCR for scanned PDFs are not specified. The composition container is
   PDF-oriented; text loading will need a broader loader contract if required.
3. **Embedding integrity.** Index identifies an input within its batch. An
   adapter must check missing/duplicate indices, count, vector dimensions and
   model compatibility. Existing zip-based ingest can silently truncate unequal
   lists. Only finite, nonempty boundary vectors are declared here; cross-record
   validation is not implemented. Query embeddings must use the same model/space.
4. **IDs and provenance.** Current text-derived point IDs can collide for equal
   text across pages/documents. Decide stable document/chunk IDs and preserve
   source, page number and chunk index. Metadata keys also differ between the
   current text and PDF paths (`text` versus `page_text`). No ID policy is added.
5. **Collection lifecycle.** Current ingest combines registry writes, duplicate
   checks, collection deletion and upserts. Decide who owns the registry, how
   model changes are handled, and how partial writes/retries are recovered.
   Composition does not itself solve consistency or destructive re-ingestion.
6. **Retrieval semantics.** Keep scores and provenance through reranking and
   citations. Decide score direction, threshold meaning, filter syntax and
   pagination guarantees. Filters are intentionally omitted: the existing
   retrieval filter argument is not applied to the active query.
7. **AI output and failures.** Existing Groq generation may return None or JSON
   text. Decide refusal/no-answer handling, structured-output validation, error
   types, timeout/retry ownership, and whether streaming/async is needed. These
   contracts are synchronous, with no retry/error behavior implemented.
8. **Boundary validation is not security or full domain validation.** Nonempty
   strings can still be whitespace; dataclasses do not validate. Metadata must
   become JSON-compatible before leaving the system. Decide input limits,
   prompt-injection handling, and session/document access rules separately.

These gaps are documented only, not fixed. Any migration or concrete adapter
requires separate approval.

## Canonical types and pipeline comments

Class docstrings identify the producer/consumer stage and boundary. Reuse
`data.Chunk` through retrieval, fusion, reranking and context assembly; use
`SearchHit` to associate a score, recording its meaning in the producing stage.
`boundary.ChunkPayload` defines the common identity/text/metadata fields once
for external vector reads and writes. The flat JSON field shapes are unchanged.
Pydantic/dataclass counterparts are deliberate boundary representations, not
per-function variants. Existing runtime models are not migrated by this package.


## Compatibility with main's interfaces

`src/rag/interface/` is the single canonical package for these contracts.
`src/rag/interface/db.py` preserves main's original legacy scaffold signatures;
`contracts.py` and `data.py` contain the newer typed ports. The legacy scaffold
is not wired into the live retrieval or ingestion flow.

The legacy DB uses `connect/ingest/retrieve`, whereas `contracts.VectorDB` exposes
collection management, upsert, search and scroll. Likewise, the legacy boundary
chunk uses `chunk_text` without `document_id`, and its internal payload has explicit
page/title/token fields. These are not equivalent to `boundary.ChunkPayload` or
`data.Chunk`, so aliasing them would silently break their shapes. They remain
compatibility contracts, not new per-stage variants. New code should use
`contracts.py`, `data.py` and `boundary.py`; migrating legacy callers requires an
explicit adapter decision.

Offline checks (with Pydantic 2, pydantic-settings, requests, python-dotenv and
groq installed; no models/services required):

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m unittest discover -s experimental/jev/tests -v
```

The merge-regression suite mocks providers, embeddings, PDF libraries and the
reranker, and writes only to temporary directories. It checks main's retained
behavior plus compatibility names and single-pass streaming display; it is not
a live RAG quality evaluation.
