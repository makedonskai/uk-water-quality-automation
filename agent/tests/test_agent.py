"""
Офлайн-тести agent loop без жодного реального виклику LLM.

Фейковий клієнт програє заздалегідь заданий сценарій відповідей моделі.
Тести перевіряють логіку циклу: ланцюжок, помилки, ліміти, бюджет.

    .venv/bin/pytest tests/ -v
"""

import json
import sys
import pathlib
import types

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import agent
import backend
from agent import run_agent, reset_usage
from config import MAX_TURNS


# ── фейковий Anthropic-клієнт ─────────────────────────────────
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
    """Віддає відповіді за сценарієм; падає, якщо сценарій вичерпано."""

    def __init__(self, script):
        self.script = list(script)
        self.messages = types.SimpleNamespace(create=self._create)
        self.calls = []

    def _create(self, **kwargs):
        # копія messages, бо агент далі дописує в той самий список
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        if not self.script:
            raise AssertionError("Сценарій вичерпано, зайвий виклик API")
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def use_fake(monkeypatch, script):
    fake = FakeClient(script)
    monkeypatch.setattr(agent, "_client", fake)
    reset_usage()
    return fake


# ── тести ─────────────────────────────────────────────────────
def test_happy_chain(monkeypatch, tmp_path):
    """Ланцюжок find → details → create_refund → ok, файл заявки створено."""
    monkeypatch.setattr(backend, "REFUNDS_DIR", tmp_path)
    monkeypatch.setenv("AUTO_CONFIRM", "y")
    use_fake(monkeypatch, [
        tool_resp("find_orders_by_email", {"email": "anna@example.com"}),
        tool_resp("get_order_details", {"order_id": "ord_7f3a"}),
        tool_resp("create_refund_request",
                  {"order_id": "ord_7f3a", "reason": "прострочення"}),
        text_resp("Заявку RF-1001 створено, повернемо $12.5."),
    ])
    r = run_agent("Замовлення на anna@example.com не прийшло, поверніть за доставку")
    assert r["outcome"] == "ok"
    assert [s["tool"] for s in r["trace"]] == [
        "find_orders_by_email", "get_order_details", "create_refund_request"]
    assert not r["failures"]
    assert (tmp_path / "ord_7f3a.json").exists()


def test_tool_error_reported_honestly(monkeypatch):
    """Інструмент повернув помилку. Вона у failures і передана моделі."""
    fake = use_fake(monkeypatch, [
        tool_resp("find_orders_by_email", {"email": "ghost@example.com"}),
        text_resp("Клієнта з таким email не знайдено. Перевірте адресу."),
    ])
    r = run_agent("Де замовлення на ghost@example.com?")
    assert r["outcome"] == "ok"
    assert r["failures"] and r["failures"][0]["error"] == "not_found"
    # результат інструмента, який побачила модель, містить помилку, а не вигадку
    sent = fake.calls[1]["messages"][-1]
    result = sent["content"][0]
    assert sent["role"] == "user" and result["type"] == "tool_result"
    assert "not_found" in result["content"] and result["is_error"] is True


def test_turns_exhausted(monkeypatch):
    """Модель зациклилась на інструментах. Очікуємо явний turns_exhausted."""
    use_fake(monkeypatch, [
        tool_resp("get_order_details", {"order_id": "ord_7f3a"})
    ] * MAX_TURNS)
    r = run_agent("питання")
    assert r["outcome"] == "turns_exhausted"
    assert r["turns"] == MAX_TURNS
    assert "оператору" in r["answer"]


def test_api_error(monkeypatch):
    """API впало. Очікуємо outcome=api_error і чесну відповідь."""
    use_fake(monkeypatch, [RuntimeError("boom")])
    r = run_agent("питання")
    assert r["outcome"] == "api_error"
    assert "недоступний" in r["answer"]


def test_no_tool_used_flag(monkeypatch):
    """Модель відповіла без інструментів. Очікуємо прапорець no_tool_used."""
    use_fake(monkeypatch, [text_resp("Відповідь з голови")])
    r = run_agent("питання")
    assert r["outcome"] == "ok"
    assert r["no_tool_used"] is True


def test_budget_guard_stops_before_first_call(monkeypatch):
    """Бюджет $0.0003 менший за оцінку одного виклику. Очікуємо стоп до
    першого платного виклику, calls=0 і cost=0."""
    fake = use_fake(monkeypatch, [])          # будь-який виклик завалить тест
    r = run_agent("питання", budget_usd=0.0003)
    assert r["outcome"] == "budget_exceeded"
    assert r["usage"]["calls"] == 0
    assert r["cost_usd"] == 0
    assert fake.calls == []


def test_refund_idempotent(monkeypatch, tmp_path):
    """Повторний create_refund_request не створює дублікат."""
    monkeypatch.setattr(backend, "REFUNDS_DIR", tmp_path)
    monkeypatch.setenv("AUTO_CONFIRM", "y")
    first = backend.create_refund_request("ord_7f3a", "прострочення")
    assert first["status"] == "created"
    second = backend.create_refund_request("ord_7f3a", "прострочення")
    assert second["status"] == "already_exists"
    assert second["refund_id"] == first["refund_id"]
    assert len(list(tmp_path.glob("*.json"))) == 1
