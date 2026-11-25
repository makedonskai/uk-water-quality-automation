"""Compare lexical vs vector retrieval on the questions in QUESTIONS.md.

No Claude model and no API calls: only local search over the knowledge base.
Run from the repo root:  .venv/bin/python agent/compare.py
Writes the table to agent/compare_results.md.
"""

import re
from datetime import date

import knowledge
from config import AGENT_DIR, RAG_THRESHOLD

QUESTIONS_FILE = AGENT_DIR / "QUESTIONS.md"
RESULTS_FILE = AGENT_DIR / "compare_results.md"

# A question row looks like "| A1 | What does a flood alert mean? | ...".
# Header rows ("| # | Question |") and separators ("|---|") do not match,
# because the first cell must be a capital letter followed by digits.
_ROW = re.compile(r"^\|\s*([A-Z]\d+)\s*\|\s*([^|]+?)\s*\|", re.M)


def load_questions() -> list[tuple[str, str]]:
    """Return (id, question) pairs from all tables in QUESTIONS.md."""
    text = QUESTIONS_FILE.read_text(encoding="utf-8")
    return _ROW.findall(text)


def _cell(text: str) -> str:
    """Make text safe inside a Markdown table cell."""
    return text.replace("|", "\\|")


def main():
    questions = load_questions()
    print(f"{len(questions)} questions, threshold {RAG_THRESHOLD}\n")

    rows = []
    for qid, question in questions:
        lex_score, lex_file, lex_section, _ = knowledge.lexical_retrieve(question, k=1)[0]
        lexical = f"{lex_file} — {lex_section} ({lex_score:g})"

        vector = []
        for score, file, section in knowledge.scores(question, k=3):
            # ✗ marks scores that vector_retrieve would drop (below threshold).
            mark = "" if score >= RAG_THRESHOLD else " ✗"
            vector.append(f"{file} — {section} ({score:.3f}{mark})")

        print(f"{qid}: {question}")
        print(f"  lexical: {lexical}")
        for i, v in enumerate(vector, 1):
            print(f"  vector {i}: {v}")
        print()
        rows.append([qid, question, lexical, *vector])

    lines = [
        "# Retrieval comparison: lexical vs vector",
        "",
        f"Generated: {date.today().isoformat()} · model: intfloat/multilingual-e5-small · "
        f"threshold: {RAG_THRESHOLD} (✗ = below threshold, would be dropped)",
        "",
        "| # | Question | Lexical top-1 (score) | Vector 1 | Vector 2 | Vector 3 |",
        "|---|---|---|---|---|---|",
    ]
    lines += ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows]
    RESULTS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {len(rows)} rows to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
