"""Offline checks for shared schemas and documented pipeline responsibilities."""

import inspect
import unittest
from dataclasses import is_dataclass

from pydantic import BaseModel, ValidationError

from interface import boundary, composition, contracts, data
from interface.jev import boundary as jev_boundary
from interface.jev import client as jev_client
from interface.jev import data as jev_data


class ContractTests(unittest.TestCase):
    def test_vector_payloads_share_fields_without_changing_wire_shape(self):
        common = {
            'chunk_id': 'chunk-1', 'document_id': 'doc-1',
            'text': 'Evidence', 'metadata': {'page_no': 1},
        }
        record = boundary.ChunkWithEmbedding(**common, vector=[0.1, 0.2])
        hit = boundary.VectorSearchHit(**common, score=0.9)
        self.assertIsInstance(record, boundary.ChunkPayload)
        self.assertIsInstance(hit, boundary.ChunkPayload)
        self.assertEqual(record.model_dump(), {**common, 'vector': [0.1, 0.2]})
        self.assertEqual(hit.model_dump(), {**common, 'score': 0.9})
        for cls, fields in ((boundary.ChunkWithEmbedding, {'vector': []}),
                            (boundary.VectorSearchHit, {'score': float('nan')})):
            with self.subTest(cls=cls.__name__), self.assertRaises(ValidationError):
                cls(**common, **fields)

    def test_default_metadata_is_not_shared(self):
        a = boundary.VectorSearchHit(chunk_id='a', document_id='d', text='a', score=1)
        b = boundary.ChunkWithEmbedding(chunk_id='b', document_id='d', text='b', vector=[1])
        a.metadata['source'] = 'a.pdf'
        self.assertEqual(b.metadata, {})

    def test_canonical_chunk_is_reused_internally(self):
        chunk = data.Chunk('c', 'd', 'Evidence', {'source': 'book.pdf'})
        hit = data.SearchHit(chunk, 0.9)
        embedded = data.EmbeddedChunk(chunk, data.Embedding(0, [0.1], 'model'))
        self.assertIs(hit.chunk, chunk)
        self.assertIs(embedded.chunk, chunk)
        self.assertTrue(is_dataclass(chunk))
        self.assertNotIsInstance(chunk, BaseModel)

    def test_public_classes_document_their_pipeline_role(self):
        modules = (boundary, data, contracts, composition,
                   jev_boundary, jev_data, jev_client)
        for module in modules:
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if cls.__module__ != module.__name__:
                    continue
                with self.subTest(module=module.__name__, cls=name):
                    self.assertTrue(cls.__doc__)
                    # Dataclasses generate a signature docstring if none is supplied.
                    self.assertFalse(cls.__doc__.startswith(name + '('))


if __name__ == '__main__':
    unittest.main()
