"""Offline tests: every session is mocked; no credentials or network required."""

import copy
import unittest
from dataclasses import is_dataclass
from unittest.mock import Mock, patch

import requests
from pydantic import ValidationError

from experimental.jev.community import CommunityJevClient
from experimental.jev.errors import JevHTTPError, JevResponseError, JevTransportError
from experimental.jev.official import OfficialJevClient
from experimental.jev.openrouter import OpenRouterJevClient
from interface.jev.client import JevClient
from interface.jev.data import ChoiceQuestion, Evaluation, NoulQuestion, ScoreQuestion

PROVIDERS = (
    (OfficialJevClient, 'https://api.typesafe.ai/v1/systemone', 'jev-latest'),
    (OpenRouterJevClient, 'https://openrouter.ai/api/v1/systemone', 'jev-1.13'),
    (CommunityJevClient, 'https://jev-ai.org/api/v1/systemone/', 'jev-1.13'),
)
QUESTIONS = {
    'route': ChoiceQuestion('Which queue?', {'billing': None, 'technical': 'Bugs'}),
    'urgent': NoulQuestion('Urgent?'),
    'severity': ScoreQuestion('How severe?', ['low', 'high']),
}
RESPONSE = {
    'model': 'jev-1.13',
    'answers': {
        'route': {'type': 'choice', 'choice': 'billing', 'probabilities': {'billing': .8, 'technical': .2}, 'confidence': .6},
        'urgent': {'type': 'noul', 'noul': .9},
        'severity': {'type': 'score', 'score': .7, 'legend': {'0': 'low', '1': 'high'}, 'probabilities': {'0': .3, '1': .7}, 'confidence': .4},
    },
    'usage': {'input_tokens': 100, 'output_tokens': 20, 'cost': .001, 'charged_tokens': 100, 'charged_credits': 0, 'wallet': 'tokens'},
    'id': 'request-1', 'provider': 'test', 'model_version': 'test-version', 'latency_ms': 100,
}


def mock_session(body=None, status=200):
    session = Mock(spec=requests.Session)
    response = Mock()
    response.status_code = status
    response.headers = {'Retry-After': '5'}
    response.json.return_value = copy.deepcopy(RESPONSE if body is None else body)
    session.post.return_value = response
    return session


class ClientTests(unittest.TestCase):
    def test_contract_is_abstract(self):
        with self.assertRaises(TypeError):
            JevClient()

    def test_three_providers_and_wire_payload(self):
        for cls, endpoint, model in PROVIDERS:
            with self.subTest(provider=cls.__name__):
                session = mock_session()
                client = cls('test-key', session=session, timeout=7)
                result = client.evaluate(Evaluation({'ticket': 'Refund'}, QUESTIONS))
                args, kwargs = session.post.call_args
                self.assertEqual(args, (endpoint,))
                self.assertEqual(kwargs['json']['model'], model)
                self.assertEqual(kwargs['json']['state'], {'ticket': 'Refund'})
                self.assertEqual(kwargs['timeout'], 7)
                self.assertFalse(kwargs['allow_redirects'])
                self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test-key')
                self.assertNotIn('criteria', kwargs['json']['questions']['urgent'])
                self.assertIsNone(kwargs['json']['questions']['route']['criteria']['billing'])
                self.assertIsInstance(kwargs['json']['questions']['severity']['criteria'], list)
                self.assertTrue(is_dataclass(result))
                self.assertTrue(all(is_dataclass(a) for a in result.answers.values()))
                self.assertEqual(result.answers['severity'].score, .7)
                self.assertEqual(result.usage.cost, .001)
                self.assertEqual(result.model_version, 'test-version')
                session.post.return_value.close.assert_called_once()

    def test_convenience_methods_for_every_provider(self):
        for cls, _, _ in PROVIDERS:
            for method, name in [('choice', 'route'), ('noul', 'urgent'), ('score', 'severity')]:
                with self.subTest(provider=cls.__name__, method=method):
                    body = copy.deepcopy(RESPONSE)
                    body['answers'] = {'answer': body['answers'][name]}
                    session = mock_session(body)
                    result = getattr(cls('test', session=session), method)('state', QUESTIONS[name])
                    self.assertTrue(is_dataclass(result))
                    session.post.assert_called_once()

    def test_invalid_input_never_calls_http(self):
        for questions in ({}, {'s': ScoreQuestion('score', ['one'])}, {'c': ChoiceQuestion('choose', {'one': None})}, {'n': NoulQuestion('yes?', {'bad': 'no'})}):
            session = mock_session()
            with self.assertRaises(ValidationError):
                OfficialJevClient('test', session=session).evaluate(Evaluation('state', questions))
            session.post.assert_not_called()
        session = mock_session()
        with self.assertRaises(ValueError):
            CommunityJevClient('test', session=session).evaluate(Evaluation('s', {str(i): QUESTIONS['urgent'] for i in range(21)}))
        session.post.assert_not_called()

    def test_invalid_response_rejected(self):
        bad_bodies = []
        for change in ('missing', 'extra', 'type', 'probability', 'sum', 'choice', 'legend', 'score', 'nan', 'usage'):
            body = copy.deepcopy(RESPONSE)
            if change == 'missing':
                del body['answers']['urgent']
            elif change == 'extra':
                body['answers']['other'] = {'type': 'noul', 'noul': .5}
            elif change == 'type':
                body['answers']['urgent'] = body['answers']['route']
            elif change == 'probability':
                body['answers']['urgent']['noul'] = 1.1
            elif change == 'sum':
                body['answers']['route']['probabilities']['billing'] = .2
            elif change == 'choice':
                body['answers']['route']['choice'] = 'unknown'
            elif change == 'legend':
                body['answers']['severity']['legend']['0'] = 'wrong'
            elif change == 'score':
                body['answers']['severity']['score'] = 20
            elif change == 'nan':
                body['answers']['urgent']['noul'] = float('nan')
            else:
                body['usage']['input_tokens'] = -1
            bad_bodies.append((change, body))
        for name, body in bad_bodies:
            with self.subTest(case=name):
                session = mock_session(body)
                with self.assertRaises(JevResponseError):
                    OfficialJevClient('test', session=session).evaluate(Evaluation('s', QUESTIONS))
                session.post.return_value.close.assert_called_once()

    def test_http_failures_are_safe_and_not_retried(self):
        for cls, _, _ in PROVIDERS:
            for status in (308, 400, 401, 402, 403, 422, 429, 500, 529):
                with self.subTest(provider=cls.__name__, status=status):
                    session = mock_session({'error': 'sensitive-test-key'}, status)
                    with self.assertRaises(JevHTTPError) as error:
                        cls('sensitive-test-key', session=session).evaluate(Evaluation('s', QUESTIONS))
                    self.assertEqual(error.exception.status_code, status)
                    self.assertEqual(error.exception.retry_after, '5')
                    self.assertNotIn('sensitive', str(error.exception))
                    session.post.assert_called_once()

    def test_timeout_and_malformed_json(self):
        session = mock_session()
        session.post.side_effect = requests.Timeout('secret')
        with self.assertRaises(JevTransportError) as error:
            OfficialJevClient('test', session=session).evaluate(Evaluation('s', QUESTIONS))
        self.assertNotIn('secret', str(error.exception))
        session = mock_session()
        session.post.return_value.json.side_effect = ValueError('bad json')
        with self.assertRaises(JevResponseError):
            OfficialJevClient('test', session=session).evaluate(Evaluation('s', QUESTIONS))
        session.post.return_value.close.assert_called_once()

    def test_config_and_key_isolation(self):
        for cls, _, _ in PROVIDERS:
            with patch.dict('os.environ', {}, clear=True):
                with self.assertRaises(ValueError):
                    cls(session=mock_session())
            with patch.dict('os.environ', {cls.key_env: 'provider-key'}, clear=True):
                session = mock_session()
                cls(model='custom-model', session=session).evaluate(Evaluation('s', QUESTIONS))
                self.assertEqual(session.post.call_args.kwargs['json']['model'], 'custom-model')
                self.assertEqual(session.post.call_args.kwargs['headers']['Authorization'], 'Bearer provider-key')
        for timeout in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                OfficialJevClient('test', timeout=timeout)
        for key in ('', ' ', 'key\nheader'):
            with self.assertRaises(ValueError):
                OfficialJevClient(key)

    def test_session_ownership_and_close(self):
        injected = mock_session()
        with OfficialJevClient('test', session=injected) as client:
            self.assertIsInstance(client, JevClient)
        injected.close.assert_not_called()
        with self.assertRaises(RuntimeError):
            client.evaluate(Evaluation('s', QUESTIONS))
        with patch('experimental.jev.http_client.requests.Session') as factory:
            owned = OfficialJevClient('test')
            owned.close()
            owned.close()
            factory.return_value.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
