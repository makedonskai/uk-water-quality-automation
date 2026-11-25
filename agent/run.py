"""
Run the water-level duty-operator agent once.

    python run.py "What is the situation at Kingston?"
    python run.py "Яка ситуація на Темзі?"
    python run.py --budget 0.0003 "..."    # budget-guard demo, no API call
    python run.py --no-rag "..."           # without the knowledge base (as in M1)
"""

import argparse
import json

from agent import reset_usage, run_agent
from config import BUDGET_USD, MAX_TURNS, MODEL, SYSTEM_PROMPT
from knowledge import build_context

DEFAULT_QUERY = ("Яка зараз ситуація на станції Kingston? "
                 "Якщо рівень вище порогу, надішли сповіщення.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default=DEFAULT_QUERY)
    ap.add_argument("--budget", type=float, default=BUDGET_USD)
    ap.add_argument("--no-rag", action="store_true",
                    help="do not add knowledge base excerpts to the prompt")
    args = ap.parse_args()

    print(f"Query: «{args.query}»")
    print(f"Model: {MODEL} · MAX_TURNS={MAX_TURNS} · budget ${args.budget}")

    # Static RAG: search the knowledge base once, before the agent starts,
    # and append the found sections to the system prompt.
    system = SYSTEM_PROMPT
    if args.no_rag:
        print("RAG: off")
    else:
        kb_text, hits = build_context(args.query)
        if hits:
            print("RAG: on")
            for score, file, section in hits:
                print(f"  {score:.3f} {file} — {section}")
        else:
            print("RAG: no sections above threshold")
        system = SYSTEM_PROMPT + kb_text
    print("─" * 70)

    reset_usage()
    result = run_agent(args.query, system=system, budget_usd=args.budget)

    # each tool call: ✓ worked, ✗ returned an error
    for step in result["trace"]:
        mark = "✗" if step.get("failed") else "✓"
        print(f"  {mark} turn {step['turn']} · {step['tool']}"
              f"({json.dumps(step['input'], ensure_ascii=False)})")
        print(f"      → {json.dumps(step['output'], ensure_ascii=False)[:180]}")

    print("─" * 70)
    print(f"Answer: {result['answer']}")
    print(f"\noutcome: {result['outcome']}"
          + (" · no_tool_used!" if result.get("no_tool_used") else ""))
    if result["failures"]:
        print(f"tool failures: {result['failures']}")
    u = result["usage"]
    print(f"API calls: {u['calls']} · tokens {u['in']}→{u['out']} · "
          f"cost ${result['cost_usd']:.6f} · {result['elapsed_sec']}s")


if __name__ == "__main__":
    main()
