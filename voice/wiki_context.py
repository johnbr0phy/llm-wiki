"""Wiki loading, retrieval, and maintenance tools for the realtime voice model.

The model is given a compact "map" of the wiki (all INDEX files + every
article's TLDR) in its system instructions, then calls tools on demand:

  Read path (query):
    - search_wiki(query)   -> ranked matching articles with snippets
    - read_article(path)   -> full markdown of one article

  Maintain path (update):
    - save_voice_note(...) -> write a dictated note to raw/ for later compile
    - compile_wiki()       -> fold pending raw/ files into wiki/ articles

This mirrors the read-path defined in CLAUDE.md:
INDEX -> section INDEX -> TLDRs -> full article.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path

import wiki_compiler

# Resolve the wiki directory. Defaults to ../wiki relative to this file so the
# app works from a fresh clone; override with WIKI_VOICE_WIKI_DIR.
REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_ROOT = Path(
    os.environ.get("WIKI_VOICE_WIKI_DIR", REPO_ROOT / "wiki")
).resolve()
RAW_ROOT = (REPO_ROOT / "raw").resolve()

MAX_ARTICLE_CHARS = 8000  # cap a single read so one big article can't blow the budget
MAX_SEARCH_RESULTS = 5
SNIPPET_RADIUS = 160

RAW_FOLDERS = frozenset({"calls", "email", "docs", "slack"})
BLOCKING_TOOLS = frozenset({"compile_wiki", "save_voice_note"})
SESSION_REFRESH_TOOLS = frozenset({"compile_wiki"})


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


def _slugify(text: str, max_len: int = 48) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if not text:
        text = "note"
    return text[:max_len].strip("-") or "note"


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

    pending = wiki_compiler.find_pending_sources()
    if pending:
        lines.append("\n## Pending compile (raw/ not yet in wiki)\n")
        for item in pending:
            lines.append(f"- `{item['path']}` ({item['reason']})")

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


def save_voice_note(content: str, title: str = "", folder: str = "calls") -> str:
    """Save a dictated note to raw/ for the next compile."""
    content = (content or "").strip()
    if not content:
        return json.dumps({"error": "content is required"})

    folder = (folder or "calls").strip().lower()
    if folder not in RAW_FOLDERS:
        return json.dumps(
            {
                "error": f"folder must be one of: {', '.join(sorted(RAW_FOLDERS))}",
            }
        )

    title = (title or "").strip()
    if not title:
        title = " ".join(content.split()[:6])
    slug = _slugify(title)

    today = date.today().isoformat()
    dest_dir = RAW_ROOT / folder
    dest_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{today}_{slug}_Voice-Note.md"
    dest = dest_dir / base_name
    counter = 2
    while dest.exists():
        dest = dest_dir / f"{today}_{slug}_Voice-Note_{counter}.md"
        counter += 1

    body = (
        f"# Voice Note: {title}\n\n"
        f"**Recorded:** {today}\n"
        f"**Source:** voice\n\n"
        f"## Content\n\n"
        f"{content}\n"
    )
    dest.write_text(body, encoding="utf-8")

    rel = dest.relative_to(REPO_ROOT).as_posix()
    return json.dumps(
        {
            "status": "saved",
            "path": rel,
            "message": (
                f"Saved to {rel}. Call compile_wiki to fold it into the wiki, "
                "or ask the user if they want you to compile now."
            ),
        }
    )


def compile_wiki() -> str:
    """Run the incremental wiki compiler on pending raw/ files."""
    result = wiki_compiler.run_compile()
    return json.dumps(result)


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
    {
        "type": "function",
        "name": "save_voice_note",
        "description": (
            "Save something the user wants remembered into raw/ as a voice note. "
            "Use when they say 'remember', 'note that', 'add to the wiki', or "
            "dictate new facts, decisions, or updates. Does not update wiki "
            "articles directly — call compile_wiki afterward (offer to do so)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The fact or note to save, in clear prose.",
                },
                "title": {
                    "type": "string",
                    "description": "Short title for the note (optional).",
                },
                "folder": {
                    "type": "string",
                    "description": "raw/ subfolder: calls (default), docs, email, slack.",
                },
            },
            "required": ["content"],
        },
    },
    {
        "type": "function",
        "name": "compile_wiki",
        "description": (
            "Compile pending raw/ files into wiki/ articles. Takes several "
            "seconds. Use after save_voice_note, or when the user asks to "
            "'update the wiki', 'compile', or 'sync'. Tell the user you're "
            "working on it before calling."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
]

_DISPATCH = {
    "search_wiki": lambda args: search_wiki(args.get("query", "")),
    "read_article": lambda args: read_article(args.get("path", "")),
    "save_voice_note": lambda args: save_voice_note(
        args.get("content", ""),
        args.get("title", ""),
        args.get("folder", "calls"),
    ),
    "compile_wiki": lambda _args: compile_wiki(),
}


def call_tool(name: str, args: dict) -> str:
    fn = _DISPATCH.get(name)
    if fn is None:
        return json.dumps({"error": f"unknown tool '{name}'"})
    try:
        return fn(args)
    except Exception as exc:  # surface errors to the model rather than crashing
        return json.dumps({"error": f"{type(exc).__name__}: {exc}"})


def is_blocking_tool(name: str) -> bool:
    return name in BLOCKING_TOOLS


def should_refresh_session(name: str) -> bool:
    return name in SESSION_REFRESH_TOOLS


INSTRUCTIONS = """\
You are the voice of John's personal knowledge base ("the wiki"). You answer \
spoken questions and help maintain the wiki by voice.

Query rules:
- Answer factual questions ONLY from the wiki. Use search_wiki and read_article \
to ground every claim. Do not invent beyond what articles say.
- A map of the wiki (indexes + TLDRs + pending raw files) is below. Use it to \
decide what to read.
- If the wiki does not contain the answer, say so plainly. Never guess.

Maintain rules:
- When John wants to remember something ("note that", "remember", "add this"), \
call save_voice_note with clear prose, then offer to compile_wiki.
- compile_wiki takes several seconds — say "Give me a moment, updating the wiki" \
before calling it.
- After compile_wiki succeeds, briefly confirm what changed.
- Raw files are source material; wiki articles are compiled from them. Never \
claim something is in the wiki until compile_wiki has run.

Voice style:
- Keep answers short and natural — one to three sentences. Offer to go deeper.
- When useful, mention which article an answer came from.

--- WIKI MAP ---
{wiki_map}
--- END WIKI MAP ---
"""


def build_instructions() -> str:
    return INSTRUCTIONS.format(wiki_map=build_system_context())