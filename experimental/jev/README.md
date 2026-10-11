# Jev experiment — isolated, opt-in

Three separate classes implement `interface.jev.client.JevClient`:

| Class / module | HTTP endpoint | Environment variable | Default model |
| --- | --- | --- | --- |
| `OfficialJevClient` / `official.py` | `https://api.typesafe.ai/v1/systemone` | `TYPESAFE_API_KEY` | `jev-latest` |
| `OpenRouterJevClient` / `openrouter.py` | `https://openrouter.ai/api/v1/systemone` | `OPENROUTER_API_KEY` | `jev-1.13` |
| `CommunityJevClient` / `community.py` | `https://jev-ai.org/api/v1/systemone/` | `JEV_API_KEY` | `jev-1.13` |

The providers have separate accounts, credentials, pricing and data policies.
`jev-ai.org` is an independent gateway, not the official TypeSafe service.
No SSH is used. No code here is imported by the existing RAG pipeline.
Construction/import does not make requests or read project settings.

## Selected integration target: community only

Use `CommunityJevClient` for the planned decision stage. Official and OpenRouter
clients remain separate, unused experiments; there is no active pipeline client
until you wire one in. No automatic switching, retries or paid fallback.

The community API is **credit-limited, not unlimited free**. Its billing docs say
it uses purchased input tokens first, otherwise one credit per call. Welcome and
daily check-in credits may be available; account balance has not been verified.
When neither wallet can pay it returns HTTP 402, exposed as `JevHTTPError(402)`.
The caller must record that as unavailable, not an evidence verdict. A local call
limit does not change which wallet the provider uses. No live calls were made.

Billing checked 2026-10-11: https://jev-ai.org/docs/billing/

See [the finishing plan](../../interface/FINISHING_PLAN.md) for the proposed
advisory grounding task, shared tracing, evaluation and budget checks (not yet
implemented).

## What Jev does

Jev evaluates application state against typed questions rather than generating
chat text. Its three primitives are:

- `choice(state, ChoiceQuestion(...))`: selected label, probabilities, confidence.
- `noul(state, NoulQuestion(...))`: probability of yes, **not a boolean**.
- `score(state, ScoreQuestion(...))`: fractional position on ordered levels,
  probabilities, confidence and legend. It is not an arbitrary min/max scale.
- `evaluate(Evaluation(...))`: multiple mixed questions about one state in a
  single request; returns all answers plus usage/provider metadata.
- `close()`: release an owned session. All clients also support `with`.

Routing, classification, ranking, guardrails and citation verification are uses
of these primitives, not additional provider endpoints. They are not wired in.
Model-list APIs are not common across these providers (OpenRouter returns a
different shape); no fictitious shared list-models API was added.

## Interface layout

- `interface/jev/client.py`: abstract class.
- `interface/jev/data.py`: internal request, question, answer and result dataclasses.
- `interface/jev/boundary.py`: Pydantic HTTP request/response/error envelopes.

Public client methods consume and return dataclasses. Only the HTTP adapter
converts to/from validated Pydantic models. Choice criteria are an object;
score criteria are an ordered array. JSON state/instructions are supported.
Responses retain documented usage fields, IDs, provider and model version;
unknown provider extension fields are ignored. Error bodies are JSON-validated
when possible but not retained or printed, to avoid leaking input or secrets.

## Manual use (makes a billable external call)

Run from the repository root in an environment with the project's existing
`requests` and Pydantic v2 dependencies. Set the provider key securely in your
shell environment; never put it in source control or chat.

```python
from experimental.jev.community import CommunityJevClient
from interface.jev.data import Evaluation, ChoiceQuestion, NoulQuestion, ScoreQuestion

# Reads JEV_API_KEY. Explicit manual call; consumes provider balance/credits.
with CommunityJevClient(timeout=30) as client:
    result = client.evaluate(Evaluation(
        state="The customer reports a duplicate invoice and asks for a refund.",
        questions={
            "queue": ChoiceQuestion("Which queue?", {
                "billing": "Invoices and refunds",
                "technical": "Bugs and outages",
            }),
            "urgent": NoulQuestion("Does this require urgent attention?"),
            "severity": ScoreQuestion("How severe?", ["Low", "Medium", "High"]),
        },
    ))
    print(result.answers)
    print(result.usage)
```

For a single question, use `client.noul(state, NoulQuestion("Is this relevant?"))`
(or the corresponding choice/score method). These helpers return only the answer;
use `evaluate` when you also need billing/usage metadata.

## Tests — no network, no keys, no charges

```sh
python -m unittest discover -s experimental/jev/tests -v
```

Nine tests with provider/error subcases cover endpoints, authentication, all
three primitives, mixed evaluation, wire shapes, metadata, validation, errors,
timeouts, environment isolation and session ownership. Live connectivity is
**not verified**. Requests are mocked; successful tests do not prove that an
account is funded, a model is accessible, or a provider's deployment matches docs.

## Intentional limits / blind spots

- Synchronous only; no automatic retries, async, streaming or background jobs.
  Avoiding retries avoids accidental duplicate billing. HTTP errors expose
  status and Retry-After; callers decide whether to retry.
- Redirects are refused, and the community URL includes its documented slash.
  There is no configurable arbitrary endpoint to accidentally receive a key.
- Provider-specific validation can change. The community 20-question limit is
  checked locally. Token/context limits remain provider-enforced.
- Probabilities must be finite, in range and sum to one within 0.01. Answer IDs,
  types, choice options, score levels/legend and score range are checked.
  Statistical calibration, correctness, and weighted-score consistency are not
  established by schema validation. Confidence is not the same as correctness.
- Classification thresholds and RAG-specific question wording need evaluation
  on your own data. No automatic yes/no thresholds or safety decisions are added.
- External requests send state to the selected provider. Review privacy and data
  policies before sending documents or personal information.
- A caller-injected Session is caller-owned and is not closed by this client.
  Clients should not be shared across threads without caller synchronization.

## Documentation consulted (2026-10-04)

- Official HTTP schema: https://docs.typesafe.ai/api.md
- Primitives and scope: https://openrouter.ai/docs/guides/community/jev
- OpenRouter System One compatibility, model names and endpoint:
  https://openrouter.ai/docs/guides/community/typesafe-sdk
- Community API, trailing slash and response format: https://jev-ai.org/docs/

No new project dependencies or changes to existing application files were needed.
