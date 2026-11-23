"""
Run the water-level duty-operator agent once.

    python run.py "What is the situation at Kingston?"
    python run.py "Яка ситуація на Темзі?"
    python run.py --budget 0.0003 "..."    # budget-guard demo, no API call
"""

import argparse
import json

from agent import reset_usage, run_agent
from config import BUDGET_USD, MAX_TURNS, MODEL

DEFAULT_QUERY = ("Яка зараз ситуація на станції Kingston? "
                 "Якщо рівень вище порогу, надішли сповіщення.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default=DEFAULT_QUERY)
    ap.add_argument("--budget", type=float, default=BUDGET_USD)
    args = ap.parse_args()

    print(f"Query: «{args.query}»")
    print(f"Model: {MODEL} · MAX_TURNS={MAX_TURNS} · budget ${args.budget}")
    print("─" * 70)

    reset_usage()
    result = run_agent(args.query, budget_usd=args.budget)

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
