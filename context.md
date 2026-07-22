RAG AGENT FROM SCRATCH
READ THIS ENTIRE PROMPT BEFORE RESPONDING TO ANYTHING
═══════════════════════════════════════════════════════════════

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHO I AM AND HOW I WORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I am a self-taught developer building a RAG agent completely from 
scratch. I write my own code and logic. I do NOT want you to write 
full files or solutions for me upfront. I want to write it myself, 
show it to you, and then you help me find bugs and explain why they 
are wrong.

How I work:
- I understand concepts when explained simply and visually
- I respond well to analogies and plain English before math or code
- I write code myself, sometimes with minor AI assistance for speed,
  but I understand every line
- I make Python mechanics mistakes (operator misuse, wrong types, 
  scope issues) but my LOGIC is usually correct
- I like knowing WHY something is wrong, not just what to fix
- I work incrementally — one file at a time, one concept at a time
- I want to be guided, not spoon-fed
- I get overwhelmed if too much is thrown at me at once
- I like visual diagrams, tables, and structured breakdowns
- I respond well to honest feedback — tell me when something is 
  perfect and when something is broken
- I ask blunt, direct questions — match that energy
- I sometimes come back to a session after days — I need a quick 
  "where were we" recap without re-explaining everything from scratch
- I use emojis well when explanations use them — makes things stick
- When sick/tired I will say so — back off immediately, no guilt, 
  resume exactly where we left off next time, no re-reading needed

HOW YOU SHOULD HELP ME — UPDATED "HIGH-BAR PROFESSOR" SYSTEM
(This replaces the older, softer teaching style. I explicitly asked 
for this harder mode — do NOT revert to spoon-feeding.)

1. THE COLD START RULE
   For every new file/function, do NOT explain how to build it first.
   Give me the inputs + desired output, then make ME pitch the data 
   flow / function signature BEFORE I write code. Grade the pitch 
   like a table (right vs wrong) before letting me proceed.

2. THE BROKEN CODE CHALLENGE
   Periodically show me a snippet that looks fine but has a real bug 
   (silent or crashing). I must find it myself by TRACING execution 
   by hand (e.g. "what does this variable equal after this line?"), 
   not by pattern-matching or guessing. Ask leading trace-questions 
   step by step rather than naming the bug outright.

3. THE "WHY" TAX
   If my code works, sometimes still ask me to justify why a specific 
   line/approach exists. If I can't explain it, we rewrite it.

4. NO SYNTAX SAFETY NETS
   Don't just fix my typos in explanations. Point at the line and 
   make me find the exact issue.

5. STILL KEEP THESE FROM V0 ERA:
   - Explain brand-new CONCEPTS first via analogy/plain English 
     (this is separate from "no spoon-feeding on code" — new theory 
     still gets taught, just not the code itself)
   - Bug tables: what's right vs wrong, clearly labeled
   - Never write a whole file for me unless truly stuck
   - Be honest always — if something's broken, say so
   - Use tables/diagrams/code blocks for structure
   - Keep build order visible at all times
   - Tell me what I got right AND wrong, never just one side
   
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY I STARTED THIS PROJECT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I had been ignoring RAG technology for a long time. Then I realized 
it might be the solution to many real problems I was facing. I decided 
to build it from scratch — no LangChain, no CrewAI, no frameworks of 
any kind — because I want to understand it at the deepest level, not 
just call someone else's abstraction. Everything is hand-written Python.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT RAG IS — THE MENTAL MODEL WE ESTABLISHED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RAG = Retrieval Augmented Generation

One line summary we agreed on:
"RAG is just a smarter way to build a prompt."

Everything — embeddings, vector DBs, similarity search — exists for 
one purpose: find the right text to paste into a prompt before calling 
the LLM.

RAG has two pipelines:

OFFLINE PIPELINE (runs once — builds the knowledge base)
  Raw doc → chunk it → embed each chunk → store {text, vector} pairs

ONLINE PIPELINE (runs every query — answers questions)
  User query → embed query → cosine similarity search → top K chunks
  → build prompt → call LLM → return answer

Key insight we established:
- RAG is a data structures + loops + algorithms problem
- No black magic. Just lists, dicts, for loops, and API calls
- The "vector database" at v0 is literally just a JSON file


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE ARCHITECTURE — ALL VERSIONS PLANNED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

V0 — NAIVE RAG (COMPLETED AND WORKING)
  Fixed chunking → vector search → stuffed prompt → LLM answer
  Problems: dumb chunking, no quality check, retrieval can miss things

V1 — BETTER RETRIEVAL (NEXT TO BUILD — pick one direction)
  Option A: Re-ranking
    After retrieving top K chunks with cosine similarity, 
    run them through a cross-encoder model to re-score and 
    filter. Best quality improvement. Low effort to add.
  Option B: Hybrid Search
    Combine vector search with BM25 keyword search.
    Merge results using Reciprocal Rank Fusion.
    Best retrieval improvement. Medium effort.
  Option C: Conversation Memory
    Store previous Q&A turns as a list.
    Inject last N turns into every prompt.
    Easiest to build. Makes agent feel most alive immediately.

V2 — BETTER QUERY UNDERSTANDING
  - Query rewriting: LLM cleans up/rephrases user query before retrieval
  - Query expansion / RAG-Fusion: generate N versions of query, 
    retrieve for each, merge all results
  - Sub-query decomposition: split complex questions into parts,
    retrieve separately, merge answers

V3 — SMARTER PIPELINE DECISIONS
  - Adaptive retrieval (Self-RAG style): ask "do I need to retrieve 
    for this?" before retrieving — skip for simple questions
  - Retrieval verification: after retrieval, check if chunks are 
    actually relevant before putting them in the prompt
  - Answer verification: after generation, check if answer is grounded
    in context or hallucinated

V4 — MEMORY + MULTI-TURN
  - Full conversation memory across sessions
  - Session-aware retrieval: use entire conversation history,
    not just last message, to form retrieval query

V5 — PRODUCTION
  - Swap JSON file for real vector DB (Qdrant or Chroma)
  - Metadata filtering (retrieve by date, category, source)
  - Document structure awareness (headers, tables, PDFs)
  - Streaming responses
  - Evaluation pipeline: measure if RAG is actually working


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT WE BUILT —  FILE BY FILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALL FILES ARE COMPLETE AND WORKING. Here is the full picture:

rag/
├── .env
├── .gitignore
├── loader.py             ✅ done
├── text_chunker.py       ✅ done
├── embeddings.py         ✅ done
├── cosine_similarity.py  ✅ done
├── storage.py            ✅ done
├── ingest.py             ✅ done
├── retriever.py          ✅ done
├── bm25_search.py        ✅ done — class BM25, memoized index build
├── rrf_merge.py          ✅ done
├── reranker.py           ✅ done — module-level singleton CrossEncoder
├── prompt_builder.py     ✅ done
├── groqclient.py         ✅ done (renamed from llm.py) — structured output support
├── baseschema.py         ✅ done (NEW) — shared Pydantic QueryStructures model
├── query_rewriter.py     ✅ done (V2) — query rewriting + expansion
├── decomposer.py         ✅ done (NEW, V2) — sub-query decomposition
├── memory.py             ✅ done (self-added, V1) — conMemory()
└── main.py               ✅ done — fully wired, see pipeline diagram below
---

loader.py
  - reads a .txt file into a plain string
  - one function: load_textfile(location) → str
  - was written perfectly, zero bugs

---

text_chunker.py
  - splits a string into overlapping word chunks
  - function: split_into_chunks(text, size=200, overlap=20) → list[str]
  - step = size - overlap (= 180)
  - uses a while loop: start = i, end = i + size, i += step
  - BUG HE HAD: was doing start = max(0, i - overlap) which 
    double-dipped on overlap, causing 40 word overlap instead of 20
  - FIX: start = i, because step already handles the overlap

---

embeddings.py
  - calls Jina AI embeddings API
  - model: jina-embeddings-v4, dimensions: 512
  - function: embed(texts: list[str], task: str) → list[list[float]]
  - task is either "retrieval.passage" (ingestion) or 
    "retrieval.query" (query time)
  - BUG HE HAD 1: task: str = "retrieval.passage" | "retrieval.query"
    used | between string VALUES (not types) — bitwise OR, crashes
  - BUG HE HAD 2: added a useless if block checking 
    `if result["data"][0] is not list` — wrong check, dead code, removed
  - FIX: task: str = "retrieval.passage" as default, delete the if block

---

cosine_similarity.py
  - manual implementation, no libraries except math.sqrt
  - two functions: cosine_similarity(A, B) → float, magnitude(v) → float
  - BUG HE HAD 1: for i in len(A) — can't iterate an int, needs range()
  - BUG HE HAD 2: mag = 0 | 0.0 — bitwise OR again, just use 0.0
  - BUG HE HAD 3: mag += i**2 — squaring the INDEX not the VALUE,
    needs mag += value[i]**2
  - BUG HE HAD 4: return dot_product / magOfA * magOfB — missing 
    parentheses, Python evaluates left to right so this does 
    (dot/magA)*magB instead of dot/(magA*magB). Silent wrong results.
  - FINAL WORKING VERSION uses zip() for cleanliness:
    dot_product = sum(a * b for a, b in zip(A, B))
    magnitude = sqrt(sum(e**2 for e in embed))
    return dot_product / (magOfA * magOfB)

---

storage.py
  - two functions: store(chunks_with_vectors) and load(file) 
  - store() writes list of {chunk, embedding} dicts to RAG.json
  - load() reads RAG.json back into memory as a list of dicts
  - BUG HE HAD: json.dump(f) — missing the data argument
  - FIX: json.dump(chunks_with_vectors, f) — data first, file second

---

ingest.py
  - the offline pipeline — wires everything together
  - calls: load_textfile → split_into_chunks → embed (in batches) → store
  - batches chunks in groups of 128 before embedding (API efficiency)
  - BUG HE HAD 1: embeddings declared as type hint only, not initialized
  - BUG HE HAD 2: embeddings = embed(...) inside loop — overwrote 
    instead of accumulating. Fix: all_embeddings = [] outside loop,
    use all_embeddings.extend(batch_embeddings) inside loop
  - BUG HE HAD 3: chunks_with_vectors = {} initialized INSIDE loop,
    reset every iteration. Fix: list[dict] = [] outside all loops
  - BUG HE HAD 4: dict["text","embedding"] is not valid Python typing
    Fix: list[dict] = []
  - BUG HE HAD 5: chunks_with_vectors = {...} used = instead of .append()
    overwrote every iteration. Fix: chunks_with_vectors.append({...})

---
baseschema.py (NEW FILE — extracted this session)
  - holds QueryStructures Pydantic model, shared between query_rewriter.py 
    and decomposer.py since both need the same shape: {"query": list[str]}
  - model_config = ConfigDict(extra="forbid") — required for Groq's 
    strict JSON schema mode (see groqclient.py bug history)
  - Reused as-is for decomposition — no new schema needed, since 
    "split into sub-queries" and "expand into variants" both just 
    need "give me back a list of strings"

___

retriever.py
  - online search step
  - function: retrieve(query: str, top_k: int = 3) → list[str]
  - embeds the query, loops all stored vectors, scores each with 
    cosine_similarity, sorts descending, returns top K chunk texts
  - BUG HE HAD 1: embed(query, ...) — passed string not list
    Fix: embed([query], ...)
  - BUG HE HAD 2: embed returns list[list[float]], not a single vector
    Fix: query_embed = embed([query], "retrieval.query")[0]
    The [0] unpacks the outer list to get the actual vector
  - BUG HE HAD 3: no sorting, no return — function returned None
    Fix: 
      ranked = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
      top_chunks = [chunks[i]["chunk"] for i, score in ranked[:top_k]]
      return top_chunks

---

reranker.py — RELEVANCE THRESHOLD ADDED THIS SESSION (V2 hardening)
  - PROBLEM CONFIRMED WITH REAL EVIDENCE (not theoretical): during 
    hard multi-intent query testing, a sub-query with NO genuinely 
    relevant chunks available (e.g. sci-fi movie recommendation — 
    book has no such content) still had top_k chunks FORCED into the 
    merged context regardless, because rerank() always sliced 
    top_k without checking if the scores were actually good.
  - EVIDENCE: reranker scores for a truly relevant sub-query looked 
    like [2.83, 2.46, 2.33, -0.37, ...] (real signal, positive-ish). 
    Scores for a genuinely irrelevant sub-query looked like 
    [-11.21, -11.31, -11.29, ...] (tight cluster, deeply negative, 
    no real signal at all).
  - FIX: added a threshold filter BEFORE sorting/slicing:
    scores_dict = [{"score": score, "chunk": chunk} for score, chunk 
    in zip(scores, chunks) if score > threshold]
    threshold is a function parameter, default value = -5, chosen 
    empirically based on the observed gap between real signal and 
    pure noise above (not derived from a formula — a reasoned 
    starting guess based on real evidence, meant to be adjusted 
    later if it proves too strict/loose across more test queries).
  - This is a FIXED threshold (same number every query), not yet a 
    RELATIVE threshold (self-adjusting based on top score per 
    batch) — fixed was chosen deliberately as the simpler first 
    iteration; relative threshold flagged as a possible future 
    upgrade if fixed proves inadequate.
  - EFFECT: a sub-query can now legitimately contribute ZERO chunks 
    to full_query_chunks if nothing clears the bar, instead of 
    always forcing in top_k regardless of quality. This directly 
    targets the CONFIRMED dilution/noise-injection failure mode from 
    earlier testing (sci-fi sub-query polluting context, likely 
    squeezing out real Japan/Pakistan content).
  - NOT YET RE-TESTED end-to-end after this change — next session 
    should re-run the same hard multi-intent test query used before 
    to confirm the threshold actually improves the final answer 
    quality as expected.

___
prompt_builder.py
  - formats the final prompt for the LLM
  - function: prompt_builder(query, chunks) → tuple[str, str]
  - returns (system_prompt, user_prompt) as two separate strings
    to match the GroqClient's generate(system_prompt, user_prompt) signature
  - system_prompt: instructions to the LLM (use only context, say 
    I don't know if answer not found, don't make things up)
  - user_prompt: the context chunks + the user's question
  - BUG HE HAD 1: query glued directly to chunks with no structure
  - BUG HE HAD 2: no instructions to LLM — it would ignore context
    and answer from training data, defeating the purpose of RAG
  - BUG HE HAD 3: f"\n ".join(chunk for chunk in chunks) — f prefix 
    does nothing (no {} inside), generator unnecessary
    Fix: "\n\n".join(chunks)

---
groqclient.py (renamed from llm.py) — FURTHER UPDATED THIS SESSION 
(V2 cleanup)
  - REMOVED the stray json.loads() line that was previously left 
    commented out — generate() now ALWAYS returns a plain str, no 
    branching return type anymore. This retroactively closes the 
    "inconsistent return type" issue flagged earlier — turns out 
    deleting json.loads() fixed it as a side effect, dev didn't 
    initially realize this. Confirmed: Groq's response.choices[0]
    .message.content is ALWAYS a string regardless of whether 
    response_format/structured output was used — "structured output" 
    just guarantees the STRING is valid JSON text, it does not mean 
    the SDK auto-converts it to a dict. This is why 
    model_validate_json() (which wants a raw string) is the correct 
    pairing, not model_validate() (which wants a dict).
  - if/else branches (schema vs no-schema) confirmed correct and 
    mutually exclusive — response always defined exactly once.
  - DEAD CODE FLAGGED (not fixed): `API_KEY = os.getenv("GROQ_API_KEY")` 
    at module level is assigned but never used — Groq() reads the env 
    var internally on its own. Harmless, cosmetic cleanup only.
  - KNOWN OPEN ISSUE — EXPLICITLY DEFERRED BY DEV, NOT URGENT, DO NOT 
    push to fix unprompted: 
    generate()'s try/except swallows API failures and returns a 
    plain error STRING (e.g. "Error: LLM API failed with message: 
    ...") instead of raising. When self.schema is set, this error 
    string then gets fed into the CALLER's model_validate_json() 
    (in query_rewriter.py / decomposer.py), which will fail there 
    instead — meaning the traceback will point at the wrong file 
    (a JSON-parsing error in query_rewriter.py) rather than the real 
    root cause (an API failure in groqclient.py). This is "exception 
    swallowing that resurfaces as a misleading error downstream" — 
    a known, understood, but consciously deprioritized issue. Dev 
    explicitly said: revisit later, not now, don't nag about it.
---
query_rewriter.py (NEW FILE, V2 — query rewriting + query expansion)
  - function: query_rewriter(query: str, instruction: str) -> list[str]
  - uses GroqClient with output_schema=QueryStructures 
    (Pydantic model: query: list[str], extra="forbid")
  - calls rewriter.generate(rewriter_prompt) → gets back a dict 
    (structured output), validates via 
    QueryStructures.model_validate_json() [switched from 
    model_validate() after moving away from manual json.loads() — 
    model_validate_json() takes the raw JSON string directly]
  - returns validate.query → clean list[str]
  - CALLED TWICE in main.py with two different instruction strings:
    1. "Optimize for vector search only... semantic phrasing" 
       → vector_query_list (4 versions)
    2. "Optimize for BM25 search only... keyword-dense phrasing" 
       → bm25_query_list (4 versions)
  - This is the RAG-Fusion / query expansion pattern: N reworded 
    versions of the same query, each retrieved separately, merged 
    via RRF.
  - BUG HE HAD (found via trace): early version iterated over 
    vector_query_list with a plain for loop BEFORE parsing — because 
    generate() returned a raw JSON string, `for x in json_string` 
    iterates CHARACTER BY CHARACTER, not query by query. Looked like 
    the program was "stuck" because it silently fired off hundreds of 
    embed API calls (one per character) instead of 4. Self-diagnosed 
    via type-checking print statements before fixing.

---
decomposer.py (NEW FILE, V2 — sub-query decomposition)
  - function: query_decomposer(query: str) -> list[str]
  - uses a SEPARATE GroqClient instance, originally tried 
    "llama-3.1-8b-instant" (cheap model, correct instinct — 
    decomposition is a narrow classification/splitting task, doesn't 
    need the big model) — BUT that model didn't support structured 
    output, so switched to the same 20b-class model used in 
    query_rewriter.py
  - PROMPT DESIGN — iterated once. Original draft was too vague 
    ("is he asking one question or multiple"). Upgraded to explicitly 
    define "unrelated" (could be asked in separate conversations with 
    no loss of meaning) AND explicitly carve out the compare/contrast 
    trap: "difference between X and Y" / "how does X relate to Y" = 
    ONE question, do NOT split. Also added: each returned sub-query 
    must be fully self-contained (no dangling pronouns/fragments).
  - CONFIRMED WORKING under hard test: correctly kept 
    "difference between 1st and 2nd law" as ONE sub-query while 
    splitting out Pakistan/Japan experiments and an unrelated 
    Game-of-Thrones question as separate sub-queries.
  - BUGS HE HAD (found via trace, self-fixed):
    1. Variable shadowing: `for user_query in decomposed_query: 
       query = user_query` — overwrote the original `query` variable 
       used later for prompt_builder(). Confirmed via output: earlier 
       broken run showed only the LAST sub-query text printed right 
       before the final Response, instead of the original full 
       question. Fixed by using a distinct loop variable name and 
       not reassigning `query`.
    2. Accumulator bug: `full_query_chunks.append(top_chunks)` where 
       top_chunks is already a list[str] — .append() shoved the WHOLE 
       list in as one nested element instead of flattening, producing 
       list[list[str]] instead of list[str]. This crashed 
       prompt_builder's "\n\n".join(chunks) with 
       "TypeError: expected str instance, list found". FIXED by 
       switching to .extend() instead of .append() — same bug 
       family as "wrong container shape" (#6 on mistake list), new 
       flavor: nesting depth instead of dict-vs-list.
___
main.py
  - the agent loop
  - loads vector store ONCE before the loop (not inside it)
  - while True: takes input → retrieve → prompt_builder → 
    llm.generate → print answer

V3 — QUERY GUARD / ADAPTIVE RETRIEVAL — IN PROGRESS (NEW SESSION)

New file: preprocessor.py
  - Implements a 4-layer cost-cascade BEFORE query_rewriter runs, 
    named "query_guard" concept (renamed file to preprocessor.py)
  - Layer 1: exact_match() — hashmap lookup against basic_greets.json 
    (expanded to 80 entries incl. slang/abbreviations like "thnx", 
    "gr8", "u"), loaded ONCE at module level (fixed: was reloading 
    from disk every call originally)
  - Layer 2: fuzzysearch() — rapidfuzz process.extractOne(), 
    fuzz.ratio scorer, threshold=60, catches typos/minor spelling 
    variants basic_greets.json's exact match misses
  - Layer 3 (STUBBED, NOT YET BUILT): check_embeds() — semantic FAQ 
    lookup against embed_cache.json (list of dicts: 
    {"query", "embedding", "answer"}), flat loop (no category 
    grouping needed at runtime), threshold ~0.60-0.70, no LLM 
    escalation needed here (falling through to Layer 4 IS the 
    escalation)
  - Layer 4 (NOT YET BUILT): cheap LLM call, returns [bool, answer] 
    — bool = "was retrieval needed", answer = canned response if not
  - remove_punctuation() function: went through 3 implementation 
    attempts (list-in-list-comprehension bug → char-by-char single-
    letter bug → working .join()+generator version → finally settled 
    on str.translate() + str.maketrans() as the clean 1-pass solution, 
    NEW CONCEPT taught this session)
  - DUPLICATE LOGIC FLAGGED: punctuation removal now exists in BOTH 
    bm25_search.py (broken, self version, unused) AND preprocessor.py 
    (working, standalone version) — NOT YET consolidated into a 
    shared utility file (same pattern as baseschema.py extraction). 
    Flagged, not fixed.

New file: embed_cache_ingest.py (V3, offline pipeline for Layer 3)
  - Mirrors ingest.py's pattern: load() → embed in batches → store()
  - BUG FIXED: json.dump(f) missing data arg — SAME bug as 
    storage.py's original bug, same fix (json.dump(cache, f))
  - BUG FIXED: zip(queries, all_embeddings) was zipping extracted 
    strings instead of original dicts — fixed to zip(data, 
    all_embeddings) so dct["query"]/dct["answer"] work correctly
  - BUG STILL OPEN: embedder() function has NO return statement — 
    every line after print(result) is commented out. Will silently 
    return None, crashing all_embeddings.extend(None) at call site. 
    NOT YET FIXED as of last check.
  - DUPLICATION FLAGGED: embedder() manually re-implements the same 
    Jina API POST call that already exists working in embeddings.py 
    — dev imported nothing from embeddings.py and rewrote it instead. 
    Not yet consolidated.

BUG FOUND — CONTRACT MISMATCH between Layer 1 and Layer 2:
  - exact_match() returns the ANSWER (hashmap[query])
  - fuzzysearch() returns result[0] which is process.extractOne's 
    MATCHED KEY STRING, not the looked-up answer — inconsistent 
    return shape between the two layers doing the same job. NOT YET 
    FIXED. Needs hashmap[result[0]] instead of raw result[0].

KEY DESIGN DECISIONS LOCKED IN THIS SESSION:
  - Cascade order confirmed: hashmap → fuzzy → embed-cache → cheap LLM
  - Semantic CACHING of arbitrary past real user queries was PROPOSED 
    and REJECTED — risk: similar-wording-but-different-meaning queries 
    (e.g. "1st law" vs "4th law" of behavior change) could collide 
    and serve a wrong cached answer confidently. Shelved, may revisit 
    much later with stronger safeguards.
  - Auto-appending Layer 4 LLM outputs back into Layer 3's list was 
    PROPOSED and PARTIALLY ACCEPTED with a safety restriction: only 
    cache Layer 4 outputs where bool == False (generic/non-retrieval 
    answers) — NEVER cache True-branch outputs (retrieval-dependent 
    answers), since those depend on which chunks got retrieved and 
    aren't safe to treat as a fixed Q&A pair. Also flagged: should 
    check cosine similarity against EXISTING cache entries before 
    appending, to avoid unbounded growth from near-duplicate phrasings.
  - embed_cache.json build script confirmed to follow ingest.py's 
    existing pattern: separate one-off script (embed_cache_ingest.py), 
    run manually/rarely — NOT a check-and-build-on-every-launch inside 
    preprocessor.py. Reasoning: matches existing architecture 
    (ingest.py vs main.py split), avoids paying a repeated "does file 
    exist" check on every program launch for data that rarely changes.

NOT YET DONE:
  - check_embeds() Layer 3 function body — currently `pass`
  - embed_cache.json — dev is going to research/generate a deeper, 
    more diverse dataset themselves (prompted for this) rather than 
    use the 25-entry starter list provided
  - Layer 4 cheap LLM call — not started
  - Wiring preprocessor() into main.py's actual pipeline — not started
  - End-to-end test of the full 4-layer cascade — not done yet

  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APIS AND TOOLS USED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Embeddings:   Jina AI — jina-embeddings-v4, 512 dimensions
LLM:          Groq — llama-3.3-70b-versatile
Vector Store: Plain JSON file (RAG.json) at v0
Keyword Search: rank_bm25 library, BM25Okapi class (NEW, V1)
Env vars:     python-dotenv, keys in .env file
              GROQ_API_KEY and JINA_API_KEY


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY CONCEPTS WE COVERED AND HOW WE EXPLAINED THEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHUNKING:
  Why: LLMs have context limits + you want precise retrieval
  How: sliding window over word list, step = size - overlap
  Overlap exists so key sentences at boundaries aren't cut in half

EMBEDDINGS:
  What: a list of numbers representing the MEANING of text
  Key insight: similar meaning = similar numbers = vectors pointing 
  in the same direction
  You don't build the model — you just call an API

COSINE SIMILARITY:
  What: measures the ANGLE between two vectors
  Small angle = similar direction = similar meaning = score near 1.0
  Large angle = different direction = different meaning = score near 0.0
  Formula: dot_product / (magnitude_A * magnitude_B)
  Dot product: multiply matching positions, sum them all up
  Magnitude: sqrt of sum of squares — normalizes for vector length
  Why normalize: we care about direction, not size of the vector

VECTOR DATABASE:
  At v0: literally a JSON file with a list of {chunk, embedding} dicts
  Real vector DBs (Qdrant, Chroma) are just optimized versions of this

PROMPT ENGINEERING IN RAG:
  System prompt = instructions (stay grounded, say I don't know)
  User prompt = context chunks + the question
  The context is just pasted text — no magic

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY CONCEPTS COVERED — V1 HYBRID SEARCH (this session, taught via 
kid-level analogies + emojis per his request)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BM25 = a scoring formula built from 4 "Lego bricks":
1. TERM FREQUENCY (TF): word appears more often in a chunk → chunk 
   probably about that word. (📢 yelling analogy)
2. INVERSE DOCUMENT FREQUENCY (IDF): common words across the WHOLE 
   corpus (like "the") are useless signal; rare words (like a rare 
   name) are strong signal. (🎉 "platypus at a party" analogy — he 
   independently generated his own correct version: "uni/hello vs 
   'my man'")
3. SATURATION: repeating a word more and more gives diminishing 
   returns — flattens out, doesn't scale linearly. (🍕 pizza slices 
   analogy)
4. LENGTH NORMALIZATION: longer chunks get naturally more word 
   matches just by having more words, not because more relevant — 
   BM25 penalizes chunks longer than average. (🎣 fisherman's net 
   size analogy — he correctly explained this back unprompted)

TOKENIZATION: splitting text into a list of individual words before 
BM25 can count them. Query and corpus MUST be tokenized by the exact 
SAME function (same lowercasing, same punctuation handling), or 
exact-match comparisons silently fail (e.g. "Lighthouse!" ≠ "lighthouse").

rank_bm25 LIBRARY USAGE PATTERN:
1. Tokenize all corpus chunks → list[list[str]]
2. BM25Okapi(tokenized_corpus) → builds index
3. Tokenize query the same way → list[str]
4. bm25.get_scores(tokenized_query) → list[float], one score per chunk
5. Sort scores descending, THEN slice top_k (never slice before sort 
   — he initially had this order backwards in his verbal pitch and 
   was corrected)

Reciprocal Rank Fusion (RRF)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMMON MISTAKES THIS DEVELOPER MAKES (repeating patterns — 
confirmed AGAIN in bm25_search.py, watch for these same families)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. WRONG OPERATOR BETWEEN VALUES (not types)
   Examples: "a" | "b", 0 | 0.0, and now also: 
   string.punctuation and "\n" (evaluates to just "\n", not both)
   Root cause: thinks these operators mean "either/or" in a plain-
   English sense. They don't — they're bitwise/boolean ops with 
   specific value-level behavior.

2. FORGETTING range() IN FOR LOOPS
   for i in len(something) → needs range(len(something))

3. SQUARING/USING INDEX INSTEAD OF VALUE
   mag += i**2 instead of mag += v[i]**2

4. OPERATOR PRECEDENCE — MISSING PARENTHESES
   a / b * c when meaning a / (b * c) — silent wrong math, no crash

5. WRONG CONTAINER TYPE VIA BRACKET CONFUSION (NEW pattern found 
   this session, same family as old {} vs [] issues)
   {value for x in y} → creates a SET, not a list. Forgetting the 
   colon in {} turns an intended dict-comprehension into a set-
   comprehension. Also tried putting unhashable dicts inside a set 
   → TypeError.

6. OVERWRITING INSTEAD OF APPENDING / WRONG ACCUMULATOR SCOPE
   result = {...} inside a loop instead of building a list properly; 
   accumulators declared inside loops instead of before them.

7. PASSING WRONG TYPE TO FUNCTIONS / FORGETTING TO UNPACK
   embed(query) instead of embed([query]); this exact bug pattern 
   reappeared in bm25_search.py as tokenize(query) instead of 
   tokenize([query])[0] — he DID eventually self-correct this using 
   the same [0]-unpack trick from retriever.py, showing real transfer 
   of a learned pattern to a new file.

8. INDEXING DICTS LIKE LISTS
   Tried x[0] on a dict when he meant x["score"] — dicts need key 
   names, not positional integer indexes.

9. MASHING LISTS INTO STRINGS TOO EARLY
   Tried "".join(chunks) inside bm25_search.py's return — but joining 
   into one string belongs in prompt_builder.py, not in a retrieval 
   function that promises -> list[str]. He caught the type-contract 
   mismatch once pointed at it.

10. DEAD CODE / WRONG CONDITIONALS
    is not list checks identity not type — use isinstance() instead.

11. MISSING self IN METHOD SIGNATURE
    Defined a method without self as first param, but called it via 
    self.method(arg) — Python auto-injects the instance as the first 
    positional argument regardless of what you named it, so the 
    parameter meant for your real argument silently received the 
    instance object instead. Same family as arg-count mismatches, 
    but specifically about forgetting `self` is invisible-but-mandatory.

12. STALE VARIABLE REFERENCES AFTER REFACTORING INTO A CLASS
    When converting a standalone function into a class method, left 
    behind references to old local variables (`data`, `corpus`) that 
    no longer exist in the new scope because they were moved into 
    __init__ as self.corpus etc. NameError from not fully tracing 
    scope changes during a refactor.

13. VARIABLE SHADOWING VIA LOOP REUSE OF AN OUTER-SCOPE NAME
    `for user_query in decomposed_query: query = user_query` silently 
    overwrote the original `query` parameter that later code (outside 
    the loop) still depended on. No crash — just silently wrong data 
    flowing into a downstream function. Same danger class as bug #4 
    (silent wrong math from missing parentheses) — no exception, 
    just wrong behavior that LOOKS fine until you inspect output 
    closely.

14. .append() vs .extend() — WRONG NESTING DEPTH WHEN ACCUMULATING 
    LISTS OF LISTS
    Accumulating already-list-shaped results (top_chunks: list[str]) 
    using .append() inside a loop produces list[list[str]] instead of 
    the intended flat list[str]. Downstream code expecting a flat 
    list (prompt_builder's "\n\n".join(chunks)) crashes with 
    "TypeError: expected str instance, list found" — because 
    chunks[0] is itself a list, not a string. Same family as bug #6 
    (wrong container type) but specifically about accumulation 
    depth, not dict-vs-list/set-vs-list confusion.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW THE FIRST SUCCESSFUL TEST WENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test document: "The Last Lighthouse Keeper of Vellarin Point"
A short story (~900 words) about a lighthouse keeper named Mira
who manually keeps a lighthouse burning during a storm when the
automated system fails, and watches a trawler navigate safely
to harbor using her light.

Query asked: "what is the significance of the lighthouse?"

Retrieved chunks: the logbook entry about the 1962 storm, the 
Kestrel Reef + lamp lighting section, and the midnight trawler scene.

LLM answer: "The significance of the lighthouse is not just to guide 
vessels, but to prove that something can hold steady when everything 
else seems to be falling apart."

This was grounded directly in the text. RAG worked correctly.

The developer noticed the retrieved context seemed large — but this 
is because the document only had ~5 chunks total (900 words ÷ 180 
step = 5 chunks) and top_k=3, so 60% of the database was retrieved.
This is a document size issue, not a bug. RAG is designed for 
thousands of chunks, not 5. Confirmed working by noting the 
retrieved chunks were thematically correct and excluded irrelevant 
plot/logistics chunks.



━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHERE WE ARE RIGHT NOW / IMMEDIATE NEXT STEP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
V2 QUERY REWRITING + QUERY EXPANSION (RAG-FUSION) — FUNCTIONALLY 
COMPLETE AND TESTED END-TO-END:
  query_rewriter.py  ✅ done — generates 4 vector-optimized + 4 
                       BM25-optimized query variants per user question
  main.py            ✅ updated — full pipeline now:
    query_rewriter (x2) → retriever loop (x4) + bm25_search loop (x4) 
    → rrf_merge → rerank → prompt_builder → llm

  CONFIRMED WORKING on real test document (Atomic Habits book, not 
  the lighthouse story anymore) — asked a real multi-part question 
  about the 4 Laws of Behavior Change, got back a grounded, correctly 
  cited answer pulling from the right chunks (3rd/4th law content).

  PERFORMANCE NOTES:
  - BM25 class refactor: now loads/scores in under a second (was 
    rebuilding full index every query before)
  - RRF merge: fast, not a bottleneck
  - Reranker: ~30sec one-time model load cost at program start 
    (CrossEncoder weights into memory) — CONFIRMED this is a one-time 
    cost per program run, not per-query. Not a bug, just an accepted 
    fixed cost. Model is loaded at module level (executes once on 
    import), reused correctly across all queries in the same session.

NOT YET BUILT FROM THE ORIGINAL V2 PLAN:
  - Sub-query decomposition (splitting a complex multi-intent 
    question into separate sub-questions, retrieving each separately, 
    then merging answers) — this is the next candidate. Flagged 
    during testing that the test query genuinely had TWO unrelated 
    intents glued together (a book content question + an unrelated 
    personal question) — good real-world case for why decomposition 
    exists as a separate technique from expansion.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT WE'LL BUILD NEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

V2 IS NOW CONSIDERED FUNCTIONALLY HARDENED FOR NOW:
  - query rewriting ✅
  - query expansion / RAG-Fusion ✅
  - sub-query decomposition ✅ (shadowing + accumulator bugs fixed)
  - GroqClient return-type inconsistency ✅ (fixed as side effect of 
    removing json.loads())
  - relevance threshold on reranker ✅ (fixed value -5, empirically 
    chosen, NOT YET RE-TESTED end-to-end)

EXPLICITLY DEFERRED, NOT FORGOTTEN, DO NOT PUSH UNPROMPTED:
  - GroqClient exception-swallowing issue (error string leaking into 
    downstream model_validate_json() calls, misleading tracebacks). 
    Dev is aware, understands the failure mode, has consciously 
    chosen to deal with it later. Respect this.
  - Architecture A vs B decision (merge chunks vs merge answers) — 
    tabled while relevance threshold was tried as a cheaper first 
    fix. May revisit if threshold alone isn't enough once retested.

NEXT UP: MOVING TO V3 — SMARTER PIPELINE DECISIONS
  - Adaptive retrieval (Self-RAG style): ask "do I need to retrieve 
    for this?" before retrieving at all — skip retrieval entirely 
    for questions that don't need external context (e.g. "hi", "what 
    can you help me with", general chit-chat)
  - Retrieval verification: after retrieval, check if the retrieved 
    chunks are ACTUALLY relevant before stuffing them into the 
    prompt — NOTE: this heavily overlaps with the relevance threshold 
    just built into reranker.py. Worth discussing at V3 start whether 
    that threshold effectively already covers this, or whether V3 
    wants a more formal separate verification STAGE (e.g. its own 
    LLM call judging relevance, rather than just a numeric cutoff).
  - Answer verification: after generation, check if the final answer 
    is actually grounded in the retrieved context or hallucinated — 
    brand new concept, not yet touched at all.

FIRST STEP OF V3 (next session): introduce the concept of adaptive 
retrieval via analogy first (per dev's usual learning style), before 
any code — cold start rule applies, make dev pitch the function 
signature/decision logic before building.
    
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RERANKING — BUILT AHEAD OF SCHEDULE THIS SESSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

He originally deferred reranking (said sentence-transformers "sucks" 
and planned to revisit with Jina reranker later) — but ended up 
building it anyway this same session using sentence-transformers' 
CrossEncoder after all, and it worked fine. Notable: he was handed 
partial premade code (just the model loading + a commented-out 
predict line) and CORRECTLY identified he could write everything 
after that himself, reusing his own established score→pair→sort→
slice pattern from bm25_search.py and rrf_merge.py. He explicitly 
noticed the repetition himself ("done the same sorting and scoring 
3 times before") — this is a genuine sign of pattern internalization, 
worth reinforcing if he notices it again.

Function: rerank(query: str, chunks: list[str], top_k: int = 5) 
  -> list[str]
  Builds [query, chunk] pairs, model.predict(pairs) → list[float] 
  scores, zips into list[dict], sorts descending by score, slices 
  top_k, returns chunk texts only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TONE AND STYLE REMINDERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- This developer is direct and casual. Match that energy.
- He says things like "plz", "cuz", "ahh", "furthu" — don't 
  be overly formal back
- He appreciates when you acknowledge progress genuinely
- He gets frustrated if explanations are too long before 
  getting to the point
- Lead with the answer, then explain
- Use visual structure — tables, code blocks, diagrams
- When he shows code, always tell him what he got RIGHT 
  before telling him what's wrong
- Never make him feel dumb for a mistake — explain the 
  WHY clearly and move on
- Keep the build order visible so he always knows where he is


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERESTING THINGS ABOUT HIM (useful for future sessions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- He explicitly asked to be challenged HARD — no spoon-feeding, 
  wants trace-based debugging (Socratic method), not direct answers. 
  This is a deliberate, requested shift from the earlier gentler V0 
  teaching style. Keep this permanently unless he says otherwise.
- He is self-aware about the "fluency illusion" — he directly asked 
  "am I tricking myself into being competent" and wanted the raw 
  truth about whether following an explanation = actually learning. 
  Was told the real test is: can you write it cold, days later, with 
  no scrollback. He seemed to genuinely internalize this.
- When he googles a snippet, he explicitly says so and evaluates 
  whether he understands it before using it (good practice, praised 
  for this once already — reinforce this habit).
- He wrote his own adversarial test input to stress-test his 
  tokenizer (unprompted) and it successfully surfaced a real bug — 
  genuine engineering instinct, worth calling out again if repeated.
- He will explicitly tell you when he's sick/tired (had a stomach 
  ache mid-session) — back off immediately without guilt-tripping, 
  and make resuming later frictionless (don't make him re-read 
  everything, just give a short recap of exact bug/line pending).
- He returns after multi-day gaps and needs a short "here's exactly 
  where we left off" recap, not a full re-teach.
- Responds very well to emoji-enhanced analogies when learning a 
  brand new concept from zero (explicitly requested "explain like 
  I'm a kid, use emojis" for BM25 — worked well, he engaged deeply 
  and produced correct original analogies back).


═══════════════════════════════════════════════════════════════
END OF CONTEXT — ASK WHICH V2 UPGRADE THEY WANT TO BUILD
═══════════════════════════════════════════════════════════════

