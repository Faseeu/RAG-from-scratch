"""Offline merge regressions: fake providers/models; all file I/O is temporary.

Run: python -m unittest discover -s tests -v
No API keys, model downloads, Qdrant server, or live Jev calls are required.
"""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def stub(**attributes):
    module = ModuleType("offline_stub")
    module.__dict__.update(attributes)
    return module


def load_file(relative, dependencies=None):
    """Load a real source file while replacing only its external collaborators."""
    name = "offline_" + relative.replace("/", "_").replace(".py", "")
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {name: module, **(dependencies or {})}):
        spec.loader.exec_module(module)
    return module


class MergeCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        previous = Path.cwd()
        os.chdir(self.temp.name)
        self.addCleanup(os.chdir, previous)
        Path("data").mkdir()
        self.env = patch.dict(os.environ, {}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.output = io.StringIO()
        self.capture = contextlib.redirect_stdout(self.output)
        self.capture.__enter__()
        self.addCleanup(self.capture.__exit__, None, None, None)

    def test_legacy_interface_contracts_keep_shapes(self):
        from rag.interface import db

        self.assertEqual(db.VectorDB.__abstractmethods__, {"connect", "ingest", "retrieve"})
        self.assertIs(db.VectorDB.__annotations__["ingest"], db.Ingest)
        chunk = db.Chunk(chunk_id="c", chunk_text="text", metadata={})
        self.assertEqual(chunk.model_dump(), {"chunk_id": "c", "chunk_text": "text", "metadata": {}})
        payload = db.ChunkPayload("text", 1, "title", "book.pdf", 3, 1.0, 0)
        self.assertEqual(payload.page_no, 1)

    def test_settings_accept_both_names_and_share_one_value(self):
        module = load_file("src/rag/config.py")
        for key in ("RAG_text_filename", "rag_filename"):
            settings = module.Settings(**{key: "custom.json"}, stream_response=True)
            self.assertEqual(settings.rag_filename, "custom.json")
            self.assertEqual(settings.RAG_text_filename, "custom.json")
            settings.rag_filename = "other.json"
            self.assertEqual(settings.RAG_text_filename, "other.json")
            settings.RAG_text_filename = "third.json"
            self.assertEqual(settings.rag_filename, "third.json")
            self.assertTrue(settings.stream_response)

    def test_settings_accept_both_environment_names(self):
        cls = load_file("src/rag/config.py").Settings
        for name in ("RAG_TEXT_FILENAME", "RAG_FILENAME"):
            with patch.dict(os.environ, {name: "env.json"}, clear=True):
                self.assertEqual(cls().rag_filename, "env.json")

    def test_saved_settings_accept_both_names_and_streaming(self):
        for key in ("RAG_text_filename", "rag_filename"):
            Path("data/settings.json").write_text(json.dumps({key: "saved.json", "stream_response": True}))
            settings = load_file("src/rag/config.py").settings
            self.assertEqual(settings.rag_filename, "saved.json")
            self.assertEqual(settings.RAG_text_filename, "saved.json")
            self.assertTrue(settings.stream_response)

    def test_memory_both_window_names_and_persistence(self):
        module = load_file("src/rag/memory/conversation.py")
        session = module.Session("s", "test", "2026-10-11")
        memory = module.ConversationMemory(session, last_n=1, data_dir=Path("sessions"))
        for i in range(3):
            memory.store(module.MemTurn(str(i), f"answer {i}"))
        self.assertEqual(len(memory.load()), 1)
        memory.last_N = 2
        self.assertEqual(memory.last_n, 2)
        self.assertEqual(len(memory.load()), 2)
        memory.last_n = 1
        self.assertEqual(memory.last_N, 1)
        resumed = module.ConversationMemory(session, last_N=2, data_dir=Path("sessions"))
        self.assertEqual(len(resumed.load()), 2)
        self.assertEqual(len(resumed.load(complete=True)), 3)

    def test_registry_deletion_still_persists(self):
        module = load_file("src/rag/ingest/registry.py")
        registry = module.collections_index
        registry.catalog = [{"file_hash": "remove"}, {"file_hash": "keep"}]
        registry.remove_by_hash("remove")
        self.assertEqual(module.CollectionsIndex().catalog, [{"file_hash": "keep"}])

    def groq_module(self):
        return load_file("src/rag/providers/llm/groqclient.py", {
            "rag.config": stub(settings=NS(max_tokens=100, stream_response=False)),
            "dotenv": stub(load_dotenv=Mock()),
        })

    def test_groq_stream_prints_once_and_returns_complete_text(self):
        module = self.groq_module()
        fake_sdk = Mock()
        fake_sdk.chat.completions.create.return_value = [
            NS(choices=[NS(delta=NS(content=token))]) for token in (None, "hello", " world")
        ]
        with patch.object(module, "Groq", return_value=fake_sdk):
            client = module.GroqClient("model", stream=True)
        with patch("builtins.print") as output:
            self.assertEqual(client.generate("question"), "hello world")
        self.assertEqual(output.call_args_list[0].args, ("hello",))
        self.assertEqual(output.call_args_list[1].args, (" world",))
        self.assertIs(output.call_args_list[0].kwargs["flush"], True)
        self.assertEqual(output.call_count, 3)  # two tokens and final newline
        self.assertTrue(fake_sdk.chat.completions.create.call_args.kwargs["stream"])

    def test_groq_accepts_typed_generation_request(self):
        from rag.interface.data import GenerationRequest

        module = self.groq_module()
        fake_sdk = Mock()
        fake_sdk.chat.completions.create.return_value = NS(
            choices=[NS(message=NS(content="answer"))]
        )
        with patch.object(module, "Groq", return_value=fake_sdk):
            client = module.GroqClient("model")

        self.assertEqual(client.generate(GenerationRequest(user_prompt="typed prompt")), "answer")
        sent = fake_sdk.chat.completions.create.call_args.kwargs["messages"]
        self.assertEqual(sent, [{"role": "user", "content": "typed prompt"}])

    def test_groq_nonstreaming_structured_output_still_returns_text(self):
        module = self.groq_module()
        fake_sdk = Mock()
        fake_sdk.chat.completions.create.return_value = NS(choices=[NS(message=NS(content='{"query": []}'))])
        schema = Mock()
        schema.model_json_schema.return_value = {"type": "object"}
        with patch.object(module, "Groq", return_value=fake_sdk):
            client = module.GroqClient("model", output_schema=schema)
        self.assertEqual(client.generate("question"), '{"query": []}')
        arguments = fake_sdk.chat.completions.create.call_args.kwargs
        self.assertFalse(arguments["stream"])
        self.assertEqual(arguments["response_format"]["json_schema"]["schema"], {"type": "object"})

    def retrieval_module(self, catalog):
        self.embed = Mock(return_value=[[0.1]])
        self.db = Mock()
        return load_file("src/rag/retrieval/dense.py", {
            "rag.config": stub(settings=NS(collection_name="docs", embedding_model="model", retrieval_top_k=5, retrieval_threshold=0.5)),
            "rag.ingest.registry": stub(collections_index=NS(catalog=catalog)),
            "rag.providers.embeddings.embedding": stub(embed=self.embed),
            "rag.providers.vectorstore.client": stub(client=self.db),
        })

    def test_missing_embedding_model_is_a_clear_error_not_keyerror(self):
        module = self.retrieval_module([{"collection_name": "docs"}])
        with self.assertRaisesRegex(RuntimeError, "Collection built with None"):
            module.retrieve("query")
        self.embed.assert_not_called()
        self.db.query_points.assert_not_called()

    def test_retrieval_preserves_main_page_text_payload(self):
        module = self.retrieval_module([{"collection_name": "docs", "embedding_model": "model"}])
        payload = {"page_text": "evidence", "page_no": 2, "source": "book.pdf"}
        self.db.query_points.return_value = NS(points=[NS(score=0.9, payload=payload)])
        result = module.retrieve("query")
        self.assertEqual(result[0].text, "evidence")
        self.assertEqual(result[0].metadata, {"page_no": 2, "source": "book.pdf"})
        self.assertIn("page_text", payload)
        self.assertEqual(self.db.query_points.call_args.kwargs["limit"], 5)
        # Both historical keyword spellings remain accepted, not newly applied.
        module.retrieve("query", filter={"source": "book.pdf"})
        module.retrieve("query", query_filter={"source": "book.pdf"})
        self.assertNotIn("query_filter", self.db.query_points.call_args.kwargs)

    def test_query_rewriter_preserves_five_versions_including_original(self):
        client = Mock()
        versions = ["original", "paraphrase", "broaden", "narrow", "perspective"]
        client.generate.return_value = json.dumps({"query": versions})
        module = load_file("src/rag/providers/llm/query_rewriter.py", {
            "rag.providers.llm.groqclient": stub(GroqClient=Mock(return_value=client)),
            "rag.config": stub(settings=NS(router_llm_model="model")),
        })
        self.assertEqual(module.query_rewriter("original", "use vector search"), versions)
        prompt = client.generate.call_args.args[0]
        self.assertIn("5 different versions", prompt)
        self.assertIn("Base/The given one", prompt)
        self.assertNotIn("4 queries", prompt)

    def test_pdf_loader_still_uses_markdown_and_one_based_pages(self):
        class Document(list):
            metadata = {"title": "Book"}
        document = Document([object(), object()])
        markdown = Mock(side_effect=[" # Page one ", " Page two "])
        module = load_file("src/rag/ingest/loaders/pdf.py", {
            "pymupdf": stub(open=Mock(return_value=document)),
            "pymupdf4llm": stub(to_markdown=markdown),
            "rag.config": stub(settings=NS(filename="book.pdf")),
        })
        parser = module.PDFParser()
        result = parser.parse()
        self.assertEqual([page.page_no for page in result], [1, 2])
        self.assertEqual(result[0].page_text, "# Page one")
        self.assertEqual(result[0].book_title, "Book")
        self.assertEqual(markdown.call_args_list[1].kwargs, {"pages": [1]})
        self.assertIs(parser.parse(), result)
        self.assertEqual(markdown.call_count, 2)

    def test_main_parses_completed_stream_and_stores_answer(self):
        from rag.verify.answerschema import AnswerStructure
        from rag.memory.conversation import MemTurn
        memory = Mock()
        memory.load.return_value = []
        raw = json.dumps({"answer": "Grounded answer", "citations": [{"chunk_id": 0, "quote": "evidence"}]})
        client = Mock()
        client.generate.return_value = raw
        factory = Mock(return_value=client)
        rerank = Mock(return_value=["evidence"])
        module = load_file("apps/cli/chat.py", {
            "rag.query.contextualize": stub(contextualize_query=Mock(return_value="context query")),
            "rag.ingest.registry": stub(collections_index=NS(list_collections=Mock(return_value=["docs"]))),
            "rag.query.guard.preprocessor": stub(preprocessor=Mock(return_value=None)),
            "rag.providers.llm.decomposer": stub(query_decomposer=Mock(return_value=["context query"])),
            "rag.providers.llm.groqclient": stub(GroqClient=factory),
            "rag.providers.llm.query_rewriter": stub(query_rewriter=Mock(return_value=["query"])),
            "rag.memory.conversation": stub(MemTurn=MemTurn, resume_or_create_session=Mock(return_value=memory)),
            "rag.generation.prompt": stub(prompt_builder=Mock(return_value="prompt")),
            "rag.retrieval.dense": stub(get_corpus_from_qdrant=Mock(return_value=["evidence"]), retrieve=Mock(return_value=[NS(text="evidence")])),
            "rag.retrieval.sparse": stub(BM25=Mock(return_value=NS(bm25_search=Mock(return_value=["evidence"])))),
            "rag.retrieval.fusion": stub(rrf_merge=Mock(return_value=["evidence"])),
            "rag.config": stub(settings=NS()),
            "rag.verify.quote_score": stub(quote_score=Mock(return_value=1.0)),
        })
        with patch.dict(sys.modules, {"rag.retrieval.rerank": stub(rerank=rerank)}), patch("builtins.input", side_effect=["0", "question", "exit"]):
            module.main()
        self.assertTrue(factory.call_args.kwargs["stream"])
        self.assertIs(factory.call_args.kwargs["output_schema"], AnswerStructure)
        stored = memory.store.call_args.args[0]
        self.assertEqual(stored.question, "context query")
        self.assertIn("Grounded answer", stored.answer)
        self.assertNotIn(raw, self.output.getvalue())  # completed JSON is not replayed
        rerank.assert_called_once()


if __name__ == "__main__":
    unittest.main()
