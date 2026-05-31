"""Wiki loading + retrieval tools exposed to the realtime voice model.

The model is given a compact "map" of the wiki (all INDEX files + every
article's TLDR) in its system instructions, then calls two tools to pull
detail on demand:

  - search_wiki(query)  -> ranked matching articles with snippets
  - read_article(path)  -> full markdown of one article

This mirrors the read-path defined in CLAUDE.md:
INDEX -> section INDEX -> TLDRs -> full article.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# Resolve the wiki directory. Defaults to ../wiki relative to this file so the
# app works from a fresh clone; override with WIKI_VOICE_WIKI_DIR.
WIKI_ROOT = Path(
    os.environ.get("WIKI_VOICE_WIKI_DIR", Path(__file__).resolve().parent.parent / "wiki")
).resolve()

MAX_ARTICLE_CHARS = 8000  # cap a single read so one big article can't blow the budget
MAX_SEARCH_RESULTS = 5
SNIPPET_RADIUS = 160


def _all_markdown() -> list[Path]:
    return sorted(WIKI_ROOT.rglob("*.md"))


def _rel(path: Path) -> str:
    return path.relative_to(WIKI_ROOT).as_posix()


def _tldr(text: str) -> str | None:
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("**TLDR:**"):
            return s.removeprefix("**TLDR:**").strip()
    return None


def _safe_resolve(rel_path: str) -> Path | None:
    """Resolve a user/model-supplied path under WIKI_ROOT, blocking traversal."""
    rel_path = rel_path.strip().lstrip("/")
    # tolerate paths passed as "wiki/projects/foo.md"
    if rel_path.startswith("wiki/"):
        rel_path = rel_path[len("wiki/") :]
    candidate = (WIKI_ROOT / rel_path).resolve()
    if WIKI_ROOT not in candidate.parents and candidate != WIKI_ROOT:
        return None
    if candidate.suffix != ".md" or not candidate.is_file():
        return None
    return candidate


def build_system_context() -> str:
    """Compact map of the wiki for the model's instructions (gets cached)."""
    lines: list[str] = []

    index = WIKI_ROOT / "INDEX.md"
    if index.is_file():
        lines.append("## Wiki top-level index\n")
        lines.append(index.read_text(encoding="utf-8").strip())
        lines.append("")

    articles = [
        p
        for p in _all_markdown()
        if p.name not in {"INDEX.md", "log.md"}
    ]
    if articles:
        lines.append("## Articles (path - TLDR)\n")
        for p in articles:
            tldr = _tldr(p.read_text(encoding="utf-8")) or "(no TLDR)"
            lines.append(f"- `{_rel(p)}` - {tldr}")
    else:
        lines.append(
            "## Articles\n\n(The wiki currently has no articles yet - only the "
            "section scaffolding. Say so plainly if asked about content.)"
        )

    return "\n".join(lines)


def search_wiki(query: str) -> str:
    """Keyword search across article bodies. Returns JSON text for the model."""
    terms = [t for t in query.lower().split() if t]
    if not terms:
        return json.dumps({"results": [], "note": "empty query"})

    scored = []
    for p in _all_markdown():
        if p.name in {"INDEX.md", "log.md"}:
            continue
        text = p.read_text(encoding="utf-8")
        low = text.lower()
        score = sum(low.count(t) for t in terms)
        if score == 0:
            continue
        # snippet around first hit
        pos = min((low.find(t) for t in terms if low.find(t) != -1), default=0)
        start = max(0, pos - SNIPPET_RADIUS)
        end = min(len(text), pos + SNIPPET_RADIUS)
        snippet = text[start:end].replace("\n", " ").strip()
        scored.append(
            {
                "path": _rel(p),
                "score": score,
                "tldr": _tldr(text),
                "snippet": f"...{snippet}...",
            }
        )

    scored.sort(key=lambda r: r["score"], reverse=True)
    results = scored[:MAX_SEARCH_RESULTS]
    note = None if results else "No matching articles found in the wiki."
    return json.dumps({"results": results, "note": note})


def read_article(path: str) -> str:
    """Return the full markdown of one wiki article (capped)."""
    resolved = _safe_resolve(path)
    if resolved is None:
        return json.dumps(
            {"error": f"No readable wiki article at '{path}'. Use search_wiki to find paths."}
        )
    text = resolved.read_text(encoding="utf-8")
    truncated = len(text) > MAX_ARTICLE_CHARS
    return json.dumps(
        {
            "path": _rel(resolved),
            "content": text[:MAX_ARTICLE_CHARS],
            "truncated": truncated,
        }
    )


# --- tool registry shared with the realtime client -------------------------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "search_wiki",
        "description": (
            "Search the personal knowledge base (wiki) for articles relevant to "
            "the user's question. Returns matching article paths, TLDRs, and "
            "snippets. Call this first when you need information you don't "
            "already have from the wiki map."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keywords or phrase to search for.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "type": "function",
        "name": "read_article",
        "description": (
            "Read the full markdown of a single wiki article by its path "
            "(e.g. 'projects/acme.md'). Use after search_wiki, or directly if "
            "the wiki map already shows the right article."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Article path relative to the wiki root.",
                }
            },
            "required": ["path"],
        },
    },
]

_DISPATCH = {
    "search_wiki": lambda args: search_wiki(args.get("query", "")),
    "read_article": lambda args: read_article(args.get("path", "")),
}


def call_tool(name: str, args: dict) -> str:
    fn = _DISPATCH.get(name)
    if fn is None:
        return json.dumps({"error": f"unknown tool '{name}'"})
    try:
        return fn(args)
    except Exception as exc:  # surface errors to the model rather than crashing
        return json.dumps({"error": f"{type(exc).__name__}: {exc}"})


INSTRUCTIONS = """\
You are the voice of John's personal knowledge base ("the wiki"). You answer \
spoken questions about his projects, people, decisions, concepts, and timeline.

Rules:
- Answer ONLY from the wiki. Use the search_wiki and read_article tools to \
ground every factual claim. Do not invent or generalize beyond what the \
articles say.
- A map of the wiki (indexes + every article's TLDR) is included below. Use it \
to decide what to read. If a TLDR already answers the question, you may answer \
directly; otherwise read the article.
- If the wiki does not contain the answer, say so plainly ("I don't have that \
in the wiki yet"). Never guess.
- This is a voice conversation. Keep answers short and natural - usually one to \
three sentences. Offer to go deeper rather than dumping everything.
- When useful, mention which article the answer came from by its short name.

--- WIKI MAP ---
{wiki_map}
--- END WIKI MAP ---
"""


def build_instructions() -> str:
    return INSTRUCTIONS.format(wiki_map=build_system_context())
