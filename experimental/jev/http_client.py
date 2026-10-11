"""Shared transport; provider classes fix their endpoint and key environment name."""

import math
import os
from dataclasses import asdict
from typing import cast

import requests
from pydantic import ValidationError

from interface.jev import boundary as wire
from interface.jev import data
from interface.jev.client import JevClient

from .errors import JevHTTPError, JevResponseError, JevTransportError


class HTTPJevClient(JevClient):
    # Intentionally no arbitrary endpoint override: avoids sending keys to a
    # different provider by accident. Subclasses set the documented endpoint.
    endpoint: str
    key_env: str
    default_model: str
    max_questions: int | None = None

    def __init__(
        self, api_key: str | None = None, *, model: str | None = None,
        timeout: float = 30.0, session: requests.Session | None = None,
    ):
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('timeout must be positive and finite')
        key = api_key if api_key is not None else os.environ.get(self.key_env, '')
        if not key.strip() or any(c in key for c in '\r\n'):
            raise ValueError(f'Set {self.key_env} or provide a valid api_key')
        self._key = key
        self.model = model if model is not None else self.default_model
        if not self.model.strip():
            raise ValueError('model must not be blank')
        self.timeout = timeout
        self._session = session if session is not None else requests.Session()
        self._owns_session = session is None
        self._closed = False

    def evaluate(self, request: data.Evaluation) -> data.EvaluationResult:
        if self._closed:
            raise RuntimeError('Client is closed')
        payload = wire.EvaluationRequest.model_validate(
            {'model': self.model, **asdict(request)}
        )
        if self.max_questions is not None and len(payload.questions) > self.max_questions:
            raise ValueError(f'This provider accepts at most {self.max_questions} questions')
        # Omit optional noul criteria, but preserve null option descriptions.
        body = payload.model_dump(mode='json')
        for question in body['questions'].values():
            if question['type'] == 'noul' and question['criteria'] is None:
                del question['criteria']
        try:
            response = self._session.post(
                self.endpoint, json=body,
                headers={'Authorization': f'Bearer {self._key}', 'Content-Type': 'application/json'},
                timeout=self.timeout, allow_redirects=False,
            )
        except requests.RequestException:
            raise JevTransportError('Jev connection failed or timed out') from None
        try:
            if not 200 <= response.status_code < 300:
                # Validate JSON errors when present, but never expose their body:
                # some gateways echo sensitive inputs or authorization details.
                try:
                    wire.ErrorPayload(body=response.json())
                except (ValueError, ValidationError):
                    pass
                raise JevHTTPError(response.status_code, response.headers.get('Retry-After'))
            try:
                result = wire.EvaluationResponse.model_validate(response.json())
                self._validate_answers(payload, result)
            except (ValueError, ValidationError):
                raise JevResponseError('Invalid or mismatched Jev response') from None
        finally:
            response.close()
        answers = {}
        for name, answer in result.answers.items():
            values = answer.model_dump(exclude={'type'})
            cls = {'choice': data.ChoiceAnswer, 'noul': data.NoulAnswer, 'score': data.ScoreAnswer}[answer.type]
            answers[name] = cls(**values)
        return data.EvaluationResult(
            model=result.model, answers=answers, usage=data.Usage(**result.usage.model_dump()),
            id=result.id, provider=result.provider, model_version=result.model_version,
            latency_ms=result.latency_ms,
        )

    @staticmethod
    def _validate_answers(request: wire.EvaluationRequest, response: wire.EvaluationResponse) -> None:
        if request.questions.keys() != response.answers.keys():
            raise ValueError('Answer IDs do not match question IDs')
        for name, question in request.questions.items():
            answer = response.answers[name]
            if question.type != answer.type:
                raise ValueError('Answer type mismatch')
            if isinstance(question, wire.ChoiceQuestionPayload):
                if set(answer.probabilities) != set(question.criteria):
                    raise ValueError('Choice options mismatch')
            elif isinstance(question, wire.ScoreQuestionPayload):
                keys = {str(i) for i in range(len(question.criteria))}
                if set(answer.probabilities) != keys or set(answer.legend) != keys:
                    raise ValueError('Score levels mismatch')
                if any(answer.legend[str(i)] != level for i, level in enumerate(question.criteria)):
                    raise ValueError('Score legend mismatch')
                if not 0 <= answer.score <= len(question.criteria) - 1:
                    raise ValueError('Score out of range')

    def choice(self, state: data.JSON, question: data.ChoiceQuestion) -> data.ChoiceAnswer:
        if not isinstance(question, data.ChoiceQuestion):
            raise TypeError('choice requires ChoiceQuestion')
        return cast(data.ChoiceAnswer, self.evaluate(data.Evaluation(state, {'answer': question})).answers['answer'])

    def noul(self, state: data.JSON, question: data.NoulQuestion) -> data.NoulAnswer:
        if not isinstance(question, data.NoulQuestion):
            raise TypeError('noul requires NoulQuestion')
        return cast(data.NoulAnswer, self.evaluate(data.Evaluation(state, {'answer': question})).answers['answer'])

    def score(self, state: data.JSON, question: data.ScoreQuestion) -> data.ScoreAnswer:
        if not isinstance(question, data.ScoreQuestion):
            raise TypeError('score requires ScoreQuestion')
        return cast(data.ScoreAnswer, self.evaluate(data.Evaluation(state, {'answer': question})).answers['answer'])

    def close(self) -> None:
        if not self._closed and self._owns_session:
            self._session.close()
        self._closed = True

    def __enter__(self):
        if self._closed:
            raise RuntimeError('Client is closed')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
