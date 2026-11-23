"""
Agent loop «міркуй → дій → спостерігай» на Anthropic Messages API.

Окрім щасливого шляху явно обробляються:
  tool_error       інструмент повернув помилку, видно у failures
  turns_exhausted  вичерпано MAX_TURNS, чесна відповідь замість обриву
  api_error        API недоступне після ретраїв
  no_tool_used     модель відповіла без бекенду, прапорець у результаті
  budget_exceeded  жорсткий ліміт бюджету, стоп до наступного платного виклику
"""

import json
import time
from config import API_KEY, MODEL, MAX_TOKENS, MAX_TURNS, BUDGET_USD, SYSTEM_PROMPT
from backend import dispatch, TOOLS

# ціни $/Mtok (input, output)
PRICES = {"claude-haiku-4-5": (1.00, 5.00),
          "claude-sonnet-4-6": (3.00, 15.00)}

# Консервативна оцінка вартості одного виклику, приблизно 1000 токенів входу.
# Потрібна, щоб бюджет-гвард зупиняв до платного виклику, а не після.
EST_CALL_COST_USD = 0.003

USAGE = {"calls": 0, "in": 0, "out": 0}

_client = None


def _get_client():
    global _client
    if _client is None:
        if not API_KEY:
            raise SystemExit("Не знайдено ANTHROPIC_API_KEY.\n"
                             "  cp .env.example .env  і впишіть ключ.")
        from anthropic import Anthropic
        _client = Anthropic(api_key=API_KEY)
    return _client


def reset_usage():
    USAGE.update({"calls": 0, "in": 0, "out": 0})


def cost_usd() -> float:
    p_in, p_out = PRICES.get(MODEL, (3.00, 15.00))
    return USAGE["in"] / 1e6 * p_in + USAGE["out"] / 1e6 * p_out


def _call(**kwargs):
    """Виклик API з ретраями на перевантаження і rate limit."""
    from anthropic import APIError, APIStatusError
    for attempt in range(3):
        try:
            resp = _get_client().messages.create(**kwargs)
            USAGE["calls"] += 1
            USAGE["in"] += resp.usage.input_tokens
            USAGE["out"] += resp.usage.output_tokens
            return resp
        except APIStatusError as e:
            if e.status_code in (429, 500, 503, 529) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise
        except APIError:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise


def to_anthropic_tools(tools: list) -> list:
    """Схеми з backend.py в OpenAI-форматі перетворює у формат Anthropic."""
    out = []
    for t in tools:
        f = t["function"]
        out.append({"name": f["name"], "description": f["description"],
                    "input_schema": f["parameters"]})
    return out


def _result(answer, outcome, trace, failures, turns, started, **extra):
    return {"answer": answer, "outcome": outcome, "trace": trace,
            "failures": failures, "turns": turns,
            "no_tool_used": outcome == "ok" and not trace,
            "elapsed_sec": round(time.time() - started, 2),
            "usage": dict(USAGE), "cost_usd": round(cost_usd(), 6), **extra}


def run_agent(query: str, system: str = SYSTEM_PROMPT, tools: list = None,
              budget_usd: float = BUDGET_USD) -> dict:
    tools = to_anthropic_tools(TOOLS if tools is None else tools)
    # Системний промпт в Anthropic передається окремим параметром, не в messages.
    messages = [{"role": "user", "content": query}]
    trace, failures = [], []
    started = time.time()

    for turn in range(MAX_TURNS):
        # Бюджет перевіряється до платного виклику. Якщо витрачене плюс
        # оцінка наступного виклику перевищує ліміт, зупиняємось.
        if cost_usd() + EST_CALL_COST_USD > budget_usd:
            return _result(
                "Обробку зупинено: вичерпано ліміт бюджету на запит "
                f"(${budget_usd}). Зверніться до оператора.",
                "budget_exceeded", trace, failures, turn, started,
                budget_usd=budget_usd)

        try:
            resp = _call(model=MODEL, max_tokens=MAX_TOKENS, system=system,
                         messages=messages, tools=tools)
        except Exception as e:
            return _result(
                "Сервіс тимчасово недоступний. Спробуйте пізніше або "
                "зверніться до оператора.",
                "api_error", trace, failures, turn, started,
                error=f"{type(e).__name__}: {e}")

        tool_uses = [b for b in resp.content if b.type == "tool_use"]

        if resp.stop_reason != "tool_use" or not tool_uses:   # фінальна відповідь
            text = "".join(b.text for b in resp.content if b.type == "text")
            return _result(text.strip(), "ok",
                           trace, failures, turn + 1, started)

        # Відповідь моделі повертається в історію як є, разом з блоками tool_use.
        messages.append({"role": "assistant", "content": resp.content})

        results = [] 
        for tu in tool_uses:
            args = tu.input or {}
            output = dispatch(tu.name, args)
            step = {"turn": turn, "tool": tu.name, "input": args,
                    "output": output}
            failed = "error" in output
            if failed:
                step["failed"] = True
                failures.append({"tool": tu.name, "error": output["error"]})
            trace.append(step)
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": json.dumps(output, ensure_ascii=False),
                            "is_error": failed})

        # Усі результати інструментів ідуть одним повідомленням від user.
        messages.append({"role": "user", "content": results})

    return _result(
        "Не вдалося завершити обробку за відведену кількість кроків. "
        "Передаю звернення оператору.",
        "turns_exhausted", trace, failures, MAX_TURNS, started)
