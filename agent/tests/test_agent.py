"""
Offline tests: no network, no API key, no real LLM call.

Part 1 tests backend rules directly (evaluate, find_station, send_alert).
Part 2 tests the agent loop with a fake client that replays a script
of model replies.

    ../.venv/bin/pytest tests/ -v      (run from agent/)
"""

import json
import pathlib
import sys
import types
from datetime import timedelta

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import agent
import backend
from agent import reset_usage, run_agent
from config import FAKE_NOW, MAX_TURNS


# ── fixtures and helpers ──────────────────────────────────────
@pytest.fixture(autouse=True)
def alerts_dir(monkeypatch, tmp_path):
    """Every test writes alerts into its own temp folder, never agent/out/.
    AUTO_CONFIRM from the developer's shell must not leak into tests."""
    folder = tmp_path / "alerts"
    monkeypatch.setattr(backend, "ALERTS_DIR", folder)
    monkeypatch.delenv("AUTO_CONFIRM", raising=False)
    return folder


def sid(query):
    """Get a station_id the same way the model must: via find_station."""
    return backend.find_station(query)["stations"][0]["station_id"]


def alert_files(folder):
    return list(folder.glob("*.json")) if folder.exists() else []


# ── fake Anthropic client (from the course template) ──────────
def _resp(content, stop_reason):
    return types.SimpleNamespace(
        content=content, stop_reason=stop_reason,
        usage=types.SimpleNamespace(input_tokens=100, output_tokens=50))


def text_resp(text):
    return _resp([types.SimpleNamespace(type="text", text=text)], "end_turn")


def tool_resp(name, tool_input, tid="toolu_1"):
    block = types.SimpleNamespace(type="tool_use", id=tid, name=name,
                                  input=tool_input)
    return _resp([block], "tool_use")


class FakeClient:
    """Replays scripted replies; fails if the script runs out."""

    def __init__(self, script):
        self.script = list(script)
        self.messages = types.SimpleNamespace(create=self._create)
        self.calls = []

    def _create(self, **kwargs):
        # copy messages, because the agent keeps appending to the same list
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        if not self.script:
            raise AssertionError("Script exhausted: unexpected API call")
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def use_fake(monkeypatch, script):
    fake = FakeClient(script)
    monkeypatch.setattr(agent, "_client", fake)
    reset_usage()
    return fake


# ══ Part 1. Backend rules ═════════════════════════════════════

# ── evaluate(): the rule Python computes, not the model ───────
FRESH = FAKE_NOW - timedelta(minutes=15)
OLD = FAKE_NOW - timedelta(days=3)


@pytest.mark.parametrize("value, measured_at, warning, critical, expected", [
    (None, FRESH, 3.97, 4.2, "unknown"),     # no value
    (1.40, OLD,   1.35, 1.50, "stale"),      # above warning, but 3 days old
    (0.72, FRESH, 0.38, 0.60, "critical"),
    (4.05, FRESH, 3.97, 4.2, "warning"),
    (6.80, FRESH, 7.0,  7.3, "normal"),
    (3.97, FRESH, 3.97, 4.2, "warning"),     # exactly warning -> warning
    (4.2,  FRESH, 3.97, 4.2, "critical"),    # exactly critical -> critical
    (4.05, FAKE_NOW - timedelta(minutes=60), 3.97, 4.2, "warning"),  # 60 min is still fresh
])
def test_evaluate(value, measured_at, warning, critical, expected):
    assert backend.evaluate(value, measured_at, warning, critical) == expected


# ── find_station ──────────────────────────────────────────────
def test_find_station_single_case_insensitive():
    r = backend.find_station("kingston")
    assert [s["name"] for s in r["stations"]] == ["Kingston"]
    assert r["stations"][0]["station_id"].startswith("st_")


def test_find_station_several_by_river():
    r = backend.find_station("Thames")
    assert {s["name"] for s in r["stations"]} == {
        "Reading", "Kingston", "Sunbury Lock"}


def test_find_station_not_found():
    r = backend.find_station("Oxford")
    assert r["error"] == "not_found"
    assert "hint" in r


# ── send_alert ────────────────────────────────────────────────
@pytest.mark.parametrize("name, status", [
    ("Reading", "normal"),
    ("Walthamstow", "stale"),
    ("Sunbury", "unknown"),
])
def test_send_alert_not_alertable(monkeypatch, alerts_dir, name, status):
    monkeypatch.setenv("AUTO_CONFIRM", "y")
    r = backend.send_alert(sid(name), "test")
    assert r["error"] == "not_alertable"
    assert r["status"] == status
    assert alert_files(alerts_dir) == []


def test_send_alert_stale_even_if_level_above_threshold(monkeypatch, alerts_dir):
    """Walthamstow is above warning, but the reading is days old."""
    monkeypatch.setenv("AUTO_CONFIRM", "y")
    station = sid("Walthamstow")
    level = backend.get_latest_level(station)
    assert level["level_m"] > level["warning_m"]          # looks like a breach
    r = backend.send_alert(station, "test")
    assert r["error"] == "not_alertable" and r["status"] == "stale"
    assert alert_files(alerts_dir) == []


def test_send_alert_confirmed_writes_file(monkeypatch, alerts_dir):
    monkeypatch.setenv("AUTO_CONFIRM", "y")
    r = backend.send_alert(sid("Kingston"), "above warning")
    assert r["status"] == "sent"
    files = alert_files(alerts_dir)
    assert len(files) == 1
    saved = json.loads(files[0].read_text(encoding="utf-8"))
    assert saved["name"] == "Kingston" and saved["status"] == "warning"


def test_send_alert_declined_writes_nothing(monkeypatch, alerts_dir):
    monkeypatch.setenv("AUTO_CONFIRM", "n")
    r = backend.send_alert(sid("Merton"), "critical")
    assert r["status"] == "declined_by_user"
    assert alert_files(alerts_dir) == []


def test_confirm_empty_answer_means_no(monkeypatch, alerts_dir):
    """No AUTO_CONFIRM: a real input() happens; Enter alone means no."""
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    r = backend.send_alert(sid("Merton"), "critical")
    assert r["status"] == "declined_by_user"
    assert alert_files(alerts_dir) == []


def test_send_alert_duplicate(monkeypatch, alerts_dir):
    monkeypatch.setenv("AUTO_CONFIRM", "y")
    station = sid("Kingston")
    first = backend.send_alert(station, "above warning")
    assert first["status"] == "sent"

    # The duplicate check must come BEFORE asking the human.
    def must_not_ask(prompt):
        raise AssertionError("_confirm called for a duplicate")
    monkeypatch.setattr(backend, "_confirm", must_not_ask)

    second = backend.send_alert(station, "above warning")
    assert second["status"] == "already_sent"
    assert second["alert_file"] == first["alert_file"]
    assert len(alert_files(alerts_dir)) == 1


def test_send_alert_unknown_station(monkeypatch, alerts_dir):
    monkeypatch.setenv("AUTO_CONFIRM", "y")
    r = backend.send_alert("st_fake", "test")
    assert r["error"] == "station_not_found"
    assert alert_files(alerts_dir) == []


# ── dispatch ──────────────────────────────────────────────────
def test_dispatch_errors(monkeypatch):
    assert backend.dispatch("delete_river", {})["error"] == "unknown_tool"
    assert backend.dispatch("get_latest_level", {})["error"] == "bad_args"

    def broken(ea_code):
        raise ValueError("bug")
    monkeypatch.setattr(backend, "_read_latest", broken)
    r = backend.dispatch("get_latest_level", {"station_id": sid("Kingston")})
    assert r["error"] == "tool_crashed"


# ══ Part 2. Agent loop with the fake client ═══════════════════

def test_happy_chain_kingston(monkeypatch, alerts_dir):
    """find_station -> get_latest_level -> send_alert -> ok, file created."""
    monkeypatch.setenv("AUTO_CONFIRM", "y")
    kingston = sid("Kingston")
    use_fake(monkeypatch, [
        tool_resp("find_station", {"query": "Kingston"}),
        tool_resp("get_latest_level", {"station_id": kingston}),
        tool_resp("send_alert", {"station_id": kingston,
                                 "reason": "Level above warning"}),
        text_resp("Kingston: 4.05 m, warning. Alert sent."),
    ])
    r = run_agent("Яка ситуація в Kingston? Якщо вище порогу, надішли сповіщення.")
    assert r["outcome"] == "ok"
    assert [s["tool"] for s in r["trace"]] == [
        "find_station", "get_latest_level", "send_alert"]
    assert r["trace"][1]["output"]["status"] == "warning"
    assert r["trace"][2]["output"]["status"] == "sent"
    assert not r["failures"]
    assert len(alert_files(alerts_dir)) == 1


def test_tool_error_reported_honestly(monkeypatch):
    """A tool returned an error: it is in failures and sent to the model."""
    fake = use_fake(monkeypatch, [
        tool_resp("find_station", {"query": "Oxford"}),
        text_resp("Станцію Oxford не моніторимо."),
    ])
    r = run_agent("Який рівень в Oxford?")
    assert r["outcome"] == "ok"
    assert r["failures"] and r["failures"][0]["error"] == "not_found"
    # the tool result the model saw contains the error, not invented data
    sent = fake.calls[1]["messages"][-1]
    result = sent["content"][0]
    assert sent["role"] == "user" and result["type"] == "tool_result"
    assert "not_found" in result["content"] and result["is_error"] is True


def test_api_error(monkeypatch):
    """The API is down: outcome=api_error and an honest answer."""
    use_fake(monkeypatch, [RuntimeError("boom")])
    r = run_agent("Kingston?")
    assert r["outcome"] == "api_error"
    assert "недоступний" in r["answer"]


def test_turns_exhausted(monkeypatch):
    """The model loops on tools: expect an explicit turns_exhausted."""
    use_fake(monkeypatch, [
        tool_resp("get_latest_level", {"station_id": sid("Kingston")})
    ] * MAX_TURNS)
    r = run_agent("Kingston?")
    assert r["outcome"] == "turns_exhausted"
    assert r["turns"] == MAX_TURNS
    assert "оператору" in r["answer"]


def test_budget_guard_stops_before_first_call(monkeypatch):
    """Budget $0.0003 is below one call's estimate: stop before any call."""
    fake = use_fake(monkeypatch, [])          # any call would fail the test
    r = run_agent("Kingston?", budget_usd=0.0003)
    assert r["outcome"] == "budget_exceeded"
    assert r["usage"]["calls"] == 0
    assert r["cost_usd"] == 0
    assert fake.calls == []


def test_run_agent_passes_system_to_client(monkeypatch):
    """run.py adds RAG excerpts via `system`; it must reach the API call."""
    fake = use_fake(monkeypatch, [text_resp("ok")])
    run_agent("Kingston?", system="CUSTOM PROMPT")
    assert fake.calls[0]["system"] == "CUSTOM PROMPT"


def test_no_tool_used_flag(monkeypatch):
    """The model answered without tools: no_tool_used flag is set."""
    use_fake(monkeypatch, [text_resp("Рівень у нормі, мабуть.")])
    r = run_agent("Kingston?")
    assert r["outcome"] == "ok"
    assert r["no_tool_used"] is True
