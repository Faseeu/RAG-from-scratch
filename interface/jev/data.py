"""Internal Jev data. No provider SDK or Pydantic objects travel here."""

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

JSON: TypeAlias = str | int | float | bool | None | list['JSON'] | dict[str, 'JSON']


@dataclass
class ChoiceQuestion:
    """Internal decision input: application/grounding task → Jev adapter; mutually

    exclusive labels and their criteria.
    """

    instructions: JSON
    criteria: dict[str, JSON]
    type: Literal['choice'] = field(default='choice', init=False)


@dataclass
class NoulQuestion:
    """Internal decision input: application → Jev adapter; asks for probability of yes, not

    a boolean.
    """

    instructions: JSON
    criteria: dict[str, JSON] | None = None
    type: Literal['noul'] = field(default='noul', init=False)


@dataclass
class ScoreQuestion:
    """Internal decision input: application → Jev adapter; ordered rubric levels, not

    arbitrary min/max bounds.
    """

    instructions: JSON
    criteria: list[JSON]
    type: Literal['score'] = field(default='score', init=False)


Question: TypeAlias = ChoiceQuestion | NoulQuestion | ScoreQuestion


@dataclass
class Evaluation:
    """Internal: decision-stage state and mixed questions → Jev adapter in one request. Not

    the offline RAG evaluation dataset.
    """

    state: JSON
    questions: dict[str, Question]


@dataclass
class ChoiceAnswer:
    """Internal: validated Jev choice → decision consumer/trace; not a proof of correctness."""

    choice: str
    probabilities: dict[str, float]
    confidence: float


@dataclass
class NoulAnswer:
    """Internal: validated Jev yes-probability → decision consumer/trace; threshold policy

    belongs to the caller.
    """

    noul: float


@dataclass
class ScoreAnswer:
    """Internal: validated Jev score → decision consumer/trace; preserve fractional scores

    and the rubric legend.
    """

    score: float
    legend: dict[str, JSON]
    probabilities: dict[str, float]
    confidence: float


Answer: TypeAlias = ChoiceAnswer | NoulAnswer | ScoreAnswer


@dataclass
class Usage:
    """Internal: Jev response → budget monitoring/trace; shared across all existing Jev

    provider clients.
    """

    input_tokens: int
    output_tokens: int
    cost: float | None = None
    charged_tokens: int | None = None
    charged_credits: float | None = None
    wallet: str | None = None


@dataclass
class EvaluationResult:
    """Internal: validated Jev response → advisory decision stage/trace. HTTP failures are

    exceptions, not insufficient-evidence verdicts.
    """

    model: str
    answers: dict[str, Answer]
    usage: Usage
    id: str | None = None
    provider: str | None = None
    model_version: str | None = None
    latency_ms: float | None = None
