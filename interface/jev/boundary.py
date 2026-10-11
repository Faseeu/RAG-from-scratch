"""System One HTTP payloads, validated at the external boundary."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, JsonValue, model_validator

Probability = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
Description = str | dict[str, JsonValue] | list[JsonValue]


class RequestModel(BaseModel):
    """Shared outbound Jev validation policy; used by every provider, not a provider-

    specific schema.
    """

    model_config = ConfigDict(extra='forbid')


class ChoiceQuestionPayload(RequestModel):
    """Output boundary: internal ChoiceQuestion → question within the Jev HTTP request."""

    type: Literal['choice']
    instructions: Description
    criteria: dict[str, JsonValue] = Field(min_length=2, max_length=255)


class NoulQuestionPayload(RequestModel):
    """Output boundary: internal NoulQuestion → question within the Jev HTTP request."""

    type: Literal['noul']
    instructions: Description
    criteria: dict[Literal['true', 'false'], JsonValue] | None = None


class ScoreQuestionPayload(RequestModel):
    """Output boundary: internal ScoreQuestion → question within the Jev HTTP request."""

    type: Literal['score']
    instructions: Description
    criteria: list[JsonValue] = Field(min_length=2, max_length=10)


QuestionPayload = Annotated[
    ChoiceQuestionPayload | NoulQuestionPayload | ScoreQuestionPayload,
    Field(discriminator='type'),
]


class EvaluationRequest(RequestModel):
    """Output boundary: internal Evaluation plus adapter model → Jev System One endpoint."""

    model: str = Field(min_length=1)
    state: Description
    questions: dict[str, QuestionPayload] = Field(min_length=1)


class Distribution(BaseModel):
    """Shared inbound probability fields for Choice and Score; validation does not

    establish calibration.
    """

    probabilities: dict[str, Probability] = Field(min_length=2)
    confidence: Probability

    @model_validator(mode='after')
    def check_distribution(self):
        if abs(sum(self.probabilities.values()) - 1.0) > 0.01:
            raise ValueError('Probabilities must sum to one (tolerance 0.01)')
        return self


class ChoiceAnswerPayload(Distribution):
    """Input boundary: Jev HTTP choice → validation → internal ChoiceAnswer."""

    type: Literal['choice']
    choice: str

    @model_validator(mode='after')
    def check_choice(self):
        if self.choice not in self.probabilities:
            raise ValueError('Selected choice is absent from probabilities')
        return self


class NoulAnswerPayload(BaseModel):
    """Input boundary: Jev HTTP noul → validation → internal NoulAnswer."""

    type: Literal['noul']
    noul: Probability


class ScoreAnswerPayload(Distribution):
    """Input boundary: Jev HTTP score → validation → internal ScoreAnswer."""

    type: Literal['score']
    score: FiniteFloat
    legend: dict[str, JsonValue]


AnswerPayload = Annotated[
    ChoiceAnswerPayload | NoulAnswerPayload | ScoreAnswerPayload,
    Field(discriminator='type'),
]


class UsagePayload(BaseModel):
    """Input boundary: Jev usage → internal Usage → budget/trace reporting; provider

    extensions stay optional.
    """

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cost: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    charged_tokens: int | None = Field(default=None, ge=0)
    charged_credits: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    wallet: str | None = None


class EvaluationResponse(BaseModel):
    """Input boundary: Jev HTTP response → validated internal EvaluationResult; one shared

    schema for compatible providers.
    """

    model: str
    answers: dict[str, AnswerPayload]
    usage: UsagePayload
    id: str | None = None
    provider: str | None = None
    model_version: str | None = None
    latency_ms: float | None = Field(default=None, ge=0, allow_inf_nan=False)


class ErrorPayload(BaseModel):
    """Input boundary: provider error JSON → validation in HTTP adapter; never print or

    persist potentially sensitive error bodies.
    """

    body: JsonValue
