# Interface boilerplate

See [FINISHING_PLAN.md](FINISHING_PLAN.md) for the current implementation
checklist, community-only Jev policy, model reuse rules and stopping criteria.
The checklist explicitly separates completed scaffolding from pending behavior.

Nothing here is connected to existing code. No adapters, conversions, ingestion
algorithm, provider calls, or changes to existing functionality are implemented.

- `boundary.py`: Pydantic models for external inputs and outputs.
- `data.py`: dataclasses for internal function-to-function data.
- `contracts.py`: abstract vector DB, AI client, PDF loader, chunker and embedder.
- `composition.py`: dependencies a future ingestion service can receive.

Intended flow: external payload → Pydantic validation → internal dataclass →
application functions → dataclass → Pydantic serialization → external service.
Conversions are deliberately not implemented. Primitive results such as bool
and None need no wrapper. Lists contain internal dataclasses.

`AIClient.generate` keeps the existing operation name, but uses a dataclass
request/result. A future Groq adapter can delegate to the current
`GroqClient.generate(request.user_prompt)` and wrap its result. The existing
class is **not** changed or automatically compatible with this new contract.
Model, token limit and structured-output schema remain adapter configuration.

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
