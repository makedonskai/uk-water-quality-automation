"""Knowledge base and retrievers for the water-level agent.

Documents are plain .md files in KB_DIR. Each file is split into chunks by
"## " headings (one section = one chunk). Every chunk keeps its file name and
section title so answers can cite the source.

Two retrieval methods with the same output shape:
- lexical_retrieve: counts shared words (shows where word matching fails);
- vector_retrieve: compares meaning using embeddings (multilingual-e5-small).

Based on domain/knowledge.py from olgaitlt/qa-knowledge-agent.
"""

import math
import re

from config import FASTEMBED_CACHE_DIR, KB_DIR, RAG_THRESHOLD, RAG_TOP_K

_MODEL_NAME = "intfloat/multilingual-e5-small"

_CHUNKS: list[tuple[str, str, str]] | None = None  # (file, section, text)
_model = None
_index: list[tuple[list[float], str, str, str]] | None = None  # (vector, file, section, text)


def _load_chunks() -> list[tuple[str, str, str]]:
    """Read every .md file in KB_DIR and split it by "## " headings.

    Only parts that start with "## " become chunks. Everything before the
    first "## " (the Source:/Retrieved: lines and the "# Title" line) is
    dropped, so metadata never ends up in the chunk text. Instead, the
    document title is added on top of every chunk for context.
    """
    chunks = []
    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        # re.M: "^" matches at the start of any line, not only the first one.
        # Needed because files start with Source:/Retrieved:, not with "# ".
        title_match = re.search(r"^#\s+(.+)", text, re.M)
        doc_title = title_match.group(1).strip() if title_match else path.stem

        # Split right before each line that starts with "## ".
        parts = [p.strip() for p in re.split(r"\n(?=## )", text) if p.strip()]
        body_parts = [p for p in parts if p.startswith("## ")]

        for part in body_parts:
            section_match = re.match(r"##\s+(.+)", part)
            section = section_match.group(1).strip() if section_match else doc_title
            enriched = f"# {doc_title}\n\n{part}"
            chunks.append((path.name, section, enriched))
    return chunks


def _ensure_chunks():
    """Load chunks once and keep them in memory."""
    global _CHUNKS
    if _CHUNKS is None:
        _CHUNKS = _load_chunks()


def _tokenize(text: str) -> set:
    """Lowercase words (Ukrainian or English letters and digits)."""
    return set(re.findall(r"[а-щьюяєіїʼ'a-z0-9]+", text.lower()))


def lexical_retrieve(query: str, k: int = 3) -> list[tuple[float, str, str, str]]:
    """Simple word-overlap score. Kept to show where it loses to meaning.

    score = 2 * (exact shared words) + (pairs of long words sharing the
    first 5 letters, e.g. "flooding" / "floods").
    """
    _ensure_chunks()
    qwords = _tokenize(query)
    scored = []
    for file, section, text in _CHUNKS:
        cwords = _tokenize(text)
        exact = len(qwords & cwords)
        partial = sum(
            1 for w in qwords for c in cwords
            if len(w) > 4 and len(c) > 4 and w[:5] == c[:5]
        )
        scored.append((float(exact * 2 + partial), file, section, text))
    scored.sort(key=lambda x: -x[0])
    return scored[:k]


def _embed(texts: list[str], kind: str) -> list[list[float]]:
    """Turn texts into 384-number vectors.

    kind: 'query' | 'passage'. e5 models were trained with these prefixes,
    so questions get "query: " and documents get "passage: ".
    """
    global _model
    if _model is None:
        try:
            from fastembed import TextEmbedding
            from fastembed.common.model_description import ModelSource, PoolingType
        except ImportError:
            raise SystemExit("Missing dependency: pip install -r agent/requirements.txt")
        # multilingual-e5-small is not in fastembed's built-in list,
        # so we describe it once: where to download it and how to pool.
        TextEmbedding.add_custom_model(
            model=_MODEL_NAME,
            pooling=PoolingType.MEAN,  # average of all token vectors
            normalization=True,        # vector length = 1
            sources=ModelSource(hf=_MODEL_NAME),
            dim=384,
        )
        _model = TextEmbedding(_MODEL_NAME, cache_dir=str(FASTEMBED_CACHE_DIR))
    vecs = _model.embed([f"{kind}: {t}" for t in texts])
    return [v.tolist() for v in vecs]


def _cos(a, b) -> float:
    """Cosine similarity: 1.0 = same direction (same meaning), lower = less similar."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb or 1.0)


def _ensure_index():
    """Embed every chunk once and keep the vectors in memory."""
    global _index
    _ensure_chunks()
    if _index is None:
        vecs = _embed([f"{section}. {text}" for _, section, text in _CHUNKS], kind="passage")
        _index = [(v, file, section, text)
                  for v, (file, section, text) in zip(vecs, _CHUNKS)]


def vector_retrieve(query: str, k: int = 3) -> list[tuple[float, str, str, str]]:
    """Top-k chunks by meaning, keeping only those at or above RAG_THRESHOLD."""
    _ensure_index()
    q = _embed([query], kind="query")[0]
    scored = sorted(
        ((_cos(q, v), file, section, text) for v, file, section, text in _index),
        key=lambda x: -x[0])
    return [(s, f, sec, t) for s, f, sec, t in scored[:k] if s >= RAG_THRESHOLD]


def scores(query: str, k: int = 5) -> list[tuple[float, str, str]]:
    """Debug helper: top-k with real similarity values, no threshold."""
    _ensure_index()
    q = _embed([query], kind="query")[0]
    scored = sorted(
        ((_cos(q, v), file, section) for v, file, section, _ in _index),
        key=lambda x: -x[0])
    return scored[:k]


def _format(hits: list[tuple[float, str, str, str]]) -> str:
    """Turn retrieved chunks into one text block, or "" if there are none."""
    if not hits:
        return ""  # fail-closed: better empty than a wrong fragment
    lines = [f"[Source: {file} — {section}]\n{text}" for _, file, section, text in hits]
    return "\n\nKnowledge base excerpts:\n" + "\n---\n".join(lines)


def as_context(query: str, k: int = 3) -> str:
    """Text block to paste into the model prompt, or "" if nothing passes the threshold."""
    return _format(vector_retrieve(query, k))


def build_context(query: str) -> tuple[str, list[tuple[float, str, str]]]:
    """Retrieve once and return (prompt text, hits) for the agent.

    text: excerpts wrapped in <knowledge_base> tags, ready to append to the
          system prompt; "" if no section passed RAG_THRESHOLD.
    hits: (score, file, section) for each section used, for printing.
    """
    found = vector_retrieve(query, RAG_TOP_K)  # threshold is applied inside
    if not found:
        return "", []
    # The tags show the model where reference text starts and ends,
    # so it can treat it as data, not as instructions.
    text = f"\n\n<knowledge_base>{_format(found)}\n</knowledge_base>"
    hits = [(score, file, section) for score, file, section, _ in found]
    return text, hits
