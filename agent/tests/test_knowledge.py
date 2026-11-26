"""
Offline tests for build_context: no model download, no network.

vector_retrieve is replaced with a fake via monkeypatch, so only the
formatting logic of build_context is tested here.

    ../.venv/bin/pytest tests/ -v      (run from agent/)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import knowledge


def fake_retrieve(result):
    """A stand-in for vector_retrieve that always returns `result`."""
    def _retrieve(query, k=3):
        return result
    return _retrieve


def test_build_context_empty_when_nothing_above_threshold(monkeypatch):
    monkeypatch.setattr(knowledge, "vector_retrieve", fake_retrieve([]))
    text, hits = knowledge.build_context("Who is the head of the Environment Agency?")
    assert text == ""
    assert hits == []


def test_build_context_wraps_text_in_knowledge_base_tags(monkeypatch):
    found = [(0.8, "f.md", "Sec", "# Doc\n\n## Sec\nSome text.")]
    monkeypatch.setattr(knowledge, "vector_retrieve", fake_retrieve(found))
    text, hits = knowledge.build_context("What does a flood alert mean?")
    body = text.strip()
    assert body.startswith("<knowledge_base>")
    assert body.endswith("</knowledge_base>")
    assert "[Source: f.md — Sec]" in text
    assert "Some text." in text
    assert hits == [(0.8, "f.md", "Sec")]
