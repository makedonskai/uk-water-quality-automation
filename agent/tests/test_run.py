"""
Offline tests for run.py: prompt assembly and the outcome line.

No API call and no model download: build_context and run_agent are
replaced via monkeypatch.

    ../.venv/bin/pytest tests/ -v      (run from agent/)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import run
from config import BASE_PROMPT, RAG_RULES


def test_no_rag_prompt_has_no_knowledge_base():
    system = run.build_system(use_rag=False, kb_text="<knowledge_base>x</knowledge_base>")
    assert system == BASE_PROMPT
    assert "knowledge_base" not in system


def test_rag_prompt_contains_rag_rules_even_without_sections():
    system = run.build_system(use_rag=True, kb_text="")
    assert system.startswith(BASE_PROMPT)
    assert RAG_RULES in system


def test_answered_from_kb_printed(monkeypatch, capsys):
    """Sections were found and no tool was used: KB answer, not a warning."""
    monkeypatch.setattr(run, "build_context", lambda q: (
        "\n\n<knowledge_base>...</knowledge_base>",
        [(0.884, "flood-alerts-and-warnings.md", "Floodline")]))
    monkeypatch.setattr(run, "run_agent", lambda query, system, budget_usd: {
        "answer": "0345 988 1188", "outcome": "ok", "trace": [],
        "failures": [], "no_tool_used": True, "elapsed_sec": 0.1,
        "usage": {"calls": 1, "in": 100, "out": 50}, "cost_usd": 0.0})
    monkeypatch.setattr(sys, "argv", ["run.py", "What is the Floodline number?"])
    run.main()
    out = capsys.readouterr().out
    assert "answered from KB" in out
    assert "no_tool_used!" not in out
