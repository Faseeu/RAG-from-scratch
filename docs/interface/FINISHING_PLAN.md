# RAG finishing plan

Updated: 2026-10-11. This is the agreed implementation scope, not a claim that
these features are already connected. Existing application behavior is unchanged.

## Current status

| Area | Actual state |
| --- | --- |
| Original RAG | Existing PDF ingestion, dense + BM25Okapi retrieval, RRF, reranking, Groq generation, quote checks and memory. End-to-end quality is not established by an evaluation set. |
| Generic interfaces | Standalone boilerplate; pipeline-location docstrings now identify responsibilities. Not integrated. |
| Jev | Separate experimental HTTP clients and offline tests. No live calls verified; no application integration. |
| Shared payloads | Vector read/write payloads reuse ChunkPayload fields. Internal stages reuse Chunk/SearchHit rather than defining per-stage chunks. |
| Tracing, offline RAG evaluation, call consolidation, BM25S | Planned below; not implemented. |

## Data rules

- Pydantic validates external inputs and serializes external outputs.
- Dataclasses carry structured internal data between application functions.
- One canonical internal type per meaning. Chunk survives retrieval, fusion,
  reranking and context assembly with identity and provenance intact.
- A shared external base is appropriate for genuinely shared wire fields:
  ChunkPayload underlies ChunkWithEmbedding and VectorSearchHit without changing
  their flat JSON shape. Do not create one schema per provider when the wire
  format is shared.
- A Pydantic payload and an internal dataclass may intentionally have similar
  fields: they live on different sides of the boundary. Do not make the internal
  pipeline pass Pydantic objects just to eliminate that deliberate separation.
- Keep Choice, Noul and Score distinct: their criteria and answer shapes differ.
- Use short class/method docstrings naming the pipeline stage and responsibility.
- Do not merge semantically different types just because their current fields
  look similar (raw GenerationResult is not a verified Answer).

## Pipeline and observation points

```text
Ingestion:
DocumentInput → Document → PDFLoader → Page → TextChunker → Chunk
  → EmbeddingClient → EmbeddedChunk → VectorDB adapter → external DB

Question:
UserQuery → Query → FAQ/guard route → contextualization/query planning
  → dense + lexical retrieval → RRF → reranking → evidence/context
  → generation → structured Answer → deterministic citation checks
  → proposed advisory community Jev grounding decisions → Response

Every stage → one shared request trace → debugging / evaluation / final report
```

The second diagram describes the target observation points. It does not mean
these interfaces or the Jev stage have been wired into main.py.

## 1. Transparency and observability

- [ ] Preserve stable chunk/document IDs and source metadata across current
      string-only transitions. Retain page/section/version where available.
- [ ] One request trace with request ID, timestamps, status, configuration/model
      versions and collection/index version.
- [ ] Record each stage's duration, result/error, input/output counts and decisions.
- [ ] Record retrieval ranks and method-labeled scores, fused ranking, reranker
      scores, selected/dropped IDs, and context actually sent to generation.
- [ ] Record model calls, token usage and cost only where known; distinguish
      estimates from provider-reported usage.
- [ ] Explain drops using actual rules (cutoff/threshold), not invented reasoning.
- [ ] Raw questions, prompts and evidence are opt-in local debug data. Never log
      credentials; define retention. Do not collect private chain of thought.
- [ ] Reuse the trace format for evaluation and readable reports. No separate
      observability platform or elaborate dashboard is required.

## 2. Offline evaluation

- [ ] Begin with 30–50 manually reviewed questions and supporting passages;
      include factual, paraphrased, exact-code/number, follow-up, multi-part,
      conflicting-evidence and unanswerable cases.
- [ ] Reserve a held-out subset; version questions, labels and document inputs.
- [ ] Measure Recall@k, MRR/NDCG where labels support it, answer support,
      citation validity, abstention, latency, calls and usage.
- [ ] Compare baseline and final configurations on the same inputs.
- [ ] Jev cannot be the sole judge of its own improvement; retain deterministic
      checks and human-reviewed labels. Small-sample results are not universal
      accuracy claims.
- [ ] Capture failures by stage, not just one overall score.

## 3. Consolidate query-preparation calls

- [ ] Compare current calls with one structured plan containing a standalone
      question, subqueries, dense variants and lexical variants.
- [ ] Also compare a simple path without unnecessary expansion/decomposition.
- [ ] Bound subquery/variant counts and validate the result.
- [ ] Keep answer generation separate: it needs evidence retrieved afterward.
- [ ] Adopt consolidation only if the measured quality/latency/cost tradeoff wins.

## 4. BM25S experiment

- [ ] Put BM25S behind the lexical retrieval boundary.
- [ ] Initially preserve preprocessing, tokenization, stemming/stopword policy,
      corpus, k1/b and retrieval limit. Explicitly verify scoring-variant defaults.
- [ ] Rebuild/version the lexical index deliberately.
- [ ] Compare index time, warm query latency, memory, result overlap and Recall@k.
- [ ] Do not simultaneously change chunking or embeddings and attribute all
      differences to BM25S. A rejected replacement is a completed experiment.

## 5. Jev: community only

Selected future integration: CommunityJevClient at
https://jev-ai.org/api/v1/systemone/ using JEV_API_KEY. Existing OfficialJevClient
and OpenRouterJevClient remain unused compatibility experiments. No automatic
provider routing or paid fallback.

The first recommended task is **advisory grounding** after generation and
citation checks: classify supplied claims/evidence as supported, contradicted,
or insufficient evidence. This is the proposed task, not yet implemented or
validated. Routing, retry-based answer repair and candidate filtering are deferred.

- [ ] Define the exact claim/evidence mapping without losing durable citations.
- [ ] Batch compatible questions within documented provider limits.
- [ ] Record provider/model, judgments, usage and latency in the shared trace.
- [ ] Enforce an explicit caller-owned request budget and total deadline.
- [ ] Keep automatic retries and automatic paid/provider fallback disabled.
- [ ] HTTP 402/quota, timeout and malformed responses mean unavailable/invalid,
      never unsupported, sufficient evidence or passed.
- [ ] Preserve deterministic quote checks. Jev probabilities are not proof of
      grounding or interchangeable with another model's self-reported confidence.
- [ ] Start advisory; gate answers only if later evaluation justifies it.

### Credit/billing constraint

Community access is **not unlimited free API use**. Documentation checked on
2026-10-11 says API calls spend purchased input-token balance first, otherwise
one credit per call; credits may come from welcome gifts/daily check-in. Without
sufficient tokens or a credit the API returns 402. Account balance is unknown.
A local call budget does not force the remote service to spend credits rather
than purchased tokens. No purchases, top-ups or calls are performed by this plan.

Source: https://jev-ai.org/docs/billing/

## 6. Correctness prerequisites and failure policy

- [x] Verify `_compute_hash` hashes the complete file in chunks and returns only after EOF; add a regression test for multi-chunk files.
- [ ] Review text-only chunk IDs for duplicate text across sources/pages.
- [ ] Define explicit behavior for empty retrieval, failed generation and invalid
      citations. Invalid output must not silently become a verified answer.
- [ ] Record parser/chunker, model, prompt and index/configuration versions.
- [ ] Make failure paths testable offline, without provider credits.

The file-hash check is covered by an offline regression test. The remaining
correctness items require deliberate implementation and tests; this
contract/documentation pass does not silently apply them.

## Finish and stop

- [ ] A request can be followed from input through evidence and verification.
- [ ] Baseline/final evaluations are reproducible.
- [ ] Query consolidation, BM25S and the bounded Jev task are evaluated and each
      is explicitly accepted or rejected.
- [ ] README includes architecture, setup, trace example, measured results,
      failure behavior and limitations.

Out of scope: universal model gateway, Rust/Go rewrite, GraphRAG, autonomous
agents, Kubernetes, commercial multi-tenancy, endless provider/model comparisons
and abstractions without consumers. Significant bug fixes are still appropriate
once the feature scope is frozen.

---

# RAG-From-Scratch: Feature & Refactoring Roadmap

This phased roadmap expands the implementation plan above with explicit
stabilization, reliability, quality-control, and capability milestones. Items
are proposals until implemented and validated; a checkbox is not a claim about
current behavior.

## Phase 1: Stabilization & Engine Extraction (Reaching “Epic”)

These features separate the core RAG logic from the user interface, making it a
true backend engine.

- [ ] **Remove Compatibility Shims:** Delete duplicate aliases (e.g.,
  `rag_filename` vs `RAG_text_filename`, dual `generate()` input types) to
  enforce one clear standard.
- [ ] **Lazy Loading Initialization:** Stop loading embedding models and LLM
  clients at import time. Move initialization to a dedicated startup function
  or lazy loaders.
- [ ] **Headless Engine Extraction:** Extract the core RAG query flow into
  `rag.engine.run_query()`.
- [ ] **CLI Isolation:** Move all `input()`, `print()`, and session-selection
  prompts strictly into the `apps/cli/` layer.
- [ ] **Safe Ingestion Pipeline:** Refactor `Ingest` to separate construction
  from execution, fix `zip` mismatch bugs, and prevent destructive collection
  deletion on model changes.

## Phase 2: Provenance & Reliability

These features ensure data is trackable, debugging is easy, and the system
never fakes a successful answer.

- [ ] **End-to-End Provenance:** Carry Chunk IDs, retrieval scores, and source
  metadata continuously through Dense/Sparse Search → RRF → Rerank → Prompting
  → Citations.
- [ ] **Strict Typing:** Enforce the use of `rag.interface` dataclasses (e.g.,
  `Chunk`, `SearchHit`, `Answer`) instead of passing raw dictionaries between
  stages.
- [ ] **Explicit Failure Modes:** Implement custom exceptions (`NoEvidenceFound`,
  `GenerationFailed`, `InvalidAnswerJSON`) so the CLI/API can gracefully handle
  and report errors instead of hallucinating.
- [ ] **Performance Tracing:** Add a `RAG_DEBUG=1` flag to log milliseconds taken
  and hits returned for every single stage of the pipeline.

## Phase 3: Measurement & Quality Control

These features add the testing and evaluation safety nets required for a
production-grade project.

- [ ] **Golden Dataset:** Create `evals/golden/basic.jsonl` with 15–20
  handwritten questions mapped to the exact Chunk IDs that contain the answer.
- [ ] **Automated Evaluation Script:** Build a `just eval` command to run the
  golden dataset and print `Recall@K` and `MRR` (Mean Reciprocal Rank) for the
  retrieval stages.
- [ ] **Boundary Tests:** Add a unit test that mechanically enforces architecture
  rules (e.g., `src/rag` is strictly forbidden from importing `apps` or
  `experimental`).
- [ ] **CI/CD Pipeline:** Add GitHub Actions to run Ruff formatting, linting,
  and `pytest` automatically on Python 3.12 for every push.

## Phase 4: Advanced Capabilities (Reaching “Legendary”)

These are the major new functional features that expand what the application
can do.

- [ ] **Streaming Generation:** Stream LLM tokens back through the engine to
  the CLI in real time, rather than waiting for the entire generation to finish.
- [ ] **FastAPI HTTP API:** Build `apps/api/main.py` to expose the headless
  engine as a REST API (endpoints for `/chat`, `/ingest`, `/health`).
- [ ] **Metadata Filtering:** Allow queries to include hard filters (e.g.,
  “date > 2024”, “source == 'manual.pdf'”) passed down into the Qdrant retrieval
  engine.
- [ ] **Multi-Format Ingestion:** Expand the loaders to handle Markdown, HTML,
  and Docx with proper structural parsing.
- [ ] **Advanced Chunking Strategies:** Implement Semantic Chunking and
  Layout-Aware Chunking, and use the Phase 3 Evaluation script to mathematically
  prove which chunker performs best.
- [ ] **Asynchronous Execution:** Convert the engine to use `asyncio` to allow
  parallel dense/sparse retrieval and parallel LLM guard/rewrite calls for
  massive speedups.
