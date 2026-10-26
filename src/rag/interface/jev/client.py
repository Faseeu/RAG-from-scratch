"""Common synchronous contract for all three providers."""

from abc import ABC, abstractmethod

from .data import (
    JSON, ChoiceAnswer, ChoiceQuestion, Evaluation, EvaluationResult,
    NoulAnswer, NoulQuestion, ScoreAnswer, ScoreQuestion,
)


class JevClient(ABC):
    """Decision port: application task → Jev adapter. Community is the selected integration

    target; other existing adapters remain unused. This port does not generate answers.
    """

    @abstractmethod
    def evaluate(self, request: Evaluation) -> EvaluationResult:
        """Evaluate multiple typed questions against one state in one call."""
        ...

    @abstractmethod
    def choice(self, state: JSON, question: ChoiceQuestion) -> ChoiceAnswer:
        ...

    @abstractmethod
    def noul(self, state: JSON, question: NoulQuestion) -> NoulAnswer:
        ...

    @abstractmethod
    def score(self, state: JSON, question: ScoreQuestion) -> ScoreAnswer:
        ...

    @abstractmethod
    def close(self) -> None:
        """Release resources owned by the client."""
        ...
