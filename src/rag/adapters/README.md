# Runtime adapters

This package contains the concrete integrations used by the RAG runtime. Its
counterpart is `rag.interface`, which defines boundary models and abstract
contracts. The query and ingestion algorithms remain in `rag.query`,
`rag.retrieval`, and `rag.ingest`.

The former `rag.providers` package was moved here as a package-layout change;
its implementations and runtime behavior were not rewritten.

## Current layout

- `llm/`: Groq client plus the current Groq-backed decomposition and rewriting
  helpers.
- `embeddings/`: embedding and batch-embedding integrations.
- `vectorstore/`: Qdrant client and the legacy JSON vector-store helpers.

## Adapter boundary rules

- Keep vendor SDK calls, request/response conversion, and provider-specific
  error handling inside this package.
- Keep retrieval, ingestion, and query orchestration in their existing
  application modules; adapters should not own the pipeline sequence.
- Prefer the models and contracts in `rag.interface` when evolving an adapter.
  Some live adapters still use legacy string/list shapes, so contract
  conformance must be introduced explicitly rather than assumed.
- Do not create clients, download models, or make network calls merely by
  importing an adapter module. Moving the current implementations here does
  not yet remove their existing import-time initialization; that can be
  addressed separately with tests.

This is an incremental boundary, not a claim that every current adapter already
implements every abstract contract.
