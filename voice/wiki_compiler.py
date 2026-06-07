"""Compile raw/ sources into wiki/ using OpenAI + the compile-wiki skill.

Invoked by wiki_context.compile_wiki() when the voice agent (or a manual call)
asks to fold new raw material into the wiki.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_ROOT = Path(
    os.environ.get("WIKI_VOICE_WIKI_DIR", REPO_ROOT / "wiki")
).resolve()
RAW_ROOT = (REPO_ROOT / "raw").resolve()
MANIFEST_PATH = RAW_ROOT / ".manifest.json"
SKILL_PATH = REPO_ROOT / "skills" / "compile-wiki" / "SKILL.md"

RAW_FOLDERS = ("calls", "email", "docs", "slack")
SKIP_RAW_NAMES = frozenset({"HOW-TO-AUTOMATE.md", ".manifest.json", ".gitkeep"})

DEFAULT_COMPILE_MODEL = os.environ.get("WIKI_COMPILE_MODEL", "gpt-4.1")
MAX_ITERATIONS = int(os.environ.get("WIKI_COMPILE_MAX_ITERATIONS", "40"))


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel_repo(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _raw_rel(path: Path) -> str:
    """Path relative to raw/ — matches compile skill manifest keys."""
    return path.relative_to(RAW_ROOT).as_posix()


def _manifest_entry(processed: dict, raw_rel: str) -> dict | None:
    """Look up manifest metadata (tolerates raw/ prefix or not)."""
    return processed.get(raw_rel) or processed.get(f"raw/{raw_rel}")


def _safe_read_path(rel_path: str) -> Path | None:
    rel_path = rel_path.strip().lstrip("/")
    if rel_path.startswith("wiki/"):
        candidate = (REPO_ROOT / rel_path).resolve()
    elif rel_path.startswith("raw/"):
        candidate = (REPO_ROOT / rel_path).resolve()
    elif rel_path.startswith("skills/"):
        candidate = (REPO_ROOT / rel_path).resolve()
    elif rel_path in {"CLAUDE.md", "README.md"}:
        candidate = (REPO_ROOT / rel_path).resolve()
    else:
        return None
    if REPO_ROOT not in candidate.parents and candidate != REPO_ROOT:
        return None
    if not candidate.is_file():
        return None
    return candidate


def _safe_write_path(rel_path: str) -> Path | None:
    rel_path = rel_path.strip().lstrip("/")
    if rel_path == "raw/.manifest.json":
        return MANIFEST_PATH
    if not rel_path.startswith("wiki/"):
        return None
    candidate = (REPO_ROOT / rel_path).resolve()
    if WIKI_ROOT not in candidate.parents and candidate != WIKI_ROOT:
        return None
    if candidate.suffix != ".md":
        return None
    return candidate


def load_manifest() -> dict:
    if MANIFEST_PATH.is_file():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"last_compile": None, "processed": {}}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _iter_raw_files() -> list[Path]:
    files: list[Path] = []
    for folder in RAW_FOLDERS:
        folder_path = RAW_ROOT / folder
        if not folder_path.is_dir():
            continue
        for path in sorted(folder_path.iterdir()):
            if path.is_file() and path.name not in SKIP_RAW_NAMES:
                files.append(path)
    return files


def find_pending_sources(manifest: dict | None = None) -> list[dict]:
    manifest = manifest or load_manifest()
    processed = manifest.get("processed", {})
    pending: list[dict] = []

    for path in _iter_raw_files():
        rel = _rel_repo(path)
        raw_rel = _raw_rel(path)
        stat = path.stat()
        prev = _manifest_entry(processed, raw_rel)
        if prev is None:
            reason = "new"
        elif prev.get("size") != stat.st_size:
            reason = "changed"
        else:
            continue
        pending.append(
            {
                "path": rel,
                "raw_rel": raw_rel,
                "reason": reason,
                "size": stat.st_size,
            }
        )
    return pending


def _compiler_read_file(rel_path: str) -> str:
    resolved = _safe_read_path(rel_path)
    if resolved is None:
        return json.dumps({"error": f"Cannot read '{rel_path}'."})
    text = resolved.read_text(encoding="utf-8")
    return json.dumps({"path": _rel_repo(resolved), "content": text})


def _compiler_write_file(rel_path: str, content: str) -> str:
    resolved = _safe_write_path(rel_path)
    if resolved is None:
        return json.dumps(
            {
                "error": (
                    f"Cannot write '{rel_path}'. Only wiki/*.md and "
                    "raw/.manifest.json are writable."
                )
            }
        )
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")
    return json.dumps({"path": _rel_repo(resolved), "bytes": len(content.encode("utf-8"))})


def _apply_manifest_updates(
    manifest: dict,
    processed_sources: list[str],
    affected_by_source: dict[str, list[str]],
) -> dict:
    now = _utc_now()
    manifest["last_compile"] = now
    processed = manifest.setdefault("processed", {})
    for rel in processed_sources:
        # Accept raw/calls/foo or calls/foo manifest keys.
        path = REPO_ROOT / rel
        if not path.is_file() and not rel.startswith("raw/"):
            path = RAW_ROOT / rel
        key = rel.removeprefix("raw/") if rel.startswith("raw/") else rel
        if not path.is_file():
            continue
        processed[key] = {
            "processed_at": now,
            "size": path.stat().st_size,
            "affected_articles": affected_by_source.get(rel, []),
        }
    save_manifest(manifest)
    return manifest


_COMPILER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a repo file (wiki/, raw/, skills/, CLAUDE.md).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to repo root, e.g. raw/calls/foo.md",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write or overwrite a wiki markdown file, or raw/.manifest.json. "
                "Follow the compile-wiki skill for article structure."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish_compile",
            "description": (
                "Call when the compile is complete. Summarize what changed. "
                "List every raw source you processed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Short summary for the user (1-3 sentences).",
                    },
                    "processed_sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Raw file paths compiled, e.g. raw/calls/foo.md",
                    },
                    "updated_articles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Wiki paths updated, e.g. wiki/projects/foo.md",
                    },
                    "created_articles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Wiki paths created this compile.",
                    },
                    "affected_by_source": {
                        "type": "object",
                        "description": (
                            "Map each processed raw path to wiki article paths it touched."
                        ),
                        "additionalProperties": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
                "required": ["summary", "processed_sources"],
            },
        },
    },
]


def _dispatch_compiler_tool(name: str, args: dict) -> tuple[str, dict | None]:
    """Return (tool_output_json, finish_payload_or_none)."""
    if name == "read_file":
        return _compiler_read_file(args.get("path", "")), None
    if name == "write_file":
        return _compiler_write_file(args.get("path", ""), args.get("content", "")), None
    if name == "finish_compile":
        return json.dumps({"status": "finished"}), args
    return json.dumps({"error": f"unknown tool '{name}'"}), None


def run_compile() -> dict:
    """Run an incremental wiki compile. Returns a result dict for the voice model."""
    pending = find_pending_sources()
    if not pending:
        return {
            "status": "noop",
            "message": "No new raw files to compile.",
            "pending_sources": [],
        }

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "OPENAI_API_KEY is not set (needed for compile_wiki).",
        }

    if not SKILL_PATH.is_file():
        return {
            "status": "error",
            "message": f"Compile skill not found at {SKILL_PATH}.",
        }

    try:
        from openai import OpenAI
    except ImportError:
        return {
            "status": "error",
            "message": "openai package not installed. Re-run voice/setup.sh.",
        }

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    pending_lines = "\n".join(
        f"- {item['path']} ({item['reason']}, {item['size']} bytes)"
        for item in pending
    )
    system = (
        "You are the wiki compiler for a personal knowledge base. "
        "Follow the compile-wiki skill exactly. Use read_file and write_file "
        "to update wiki articles incrementally. Never modify raw/ source files "
        "(except you may write raw/.manifest.json if needed, though finish_compile "
        "also records processed sources). When done, call finish_compile.\n\n"
        f"--- COMPILE SKILL ---\n{skill_text}\n--- END SKILL ---"
    )
    user = (
        "Compile the following pending raw sources into the wiki:\n"
        f"{pending_lines}\n\n"
        "Steps: read each source, read relevant existing wiki articles, "
        "update or create articles, update section INDEX.md files and "
        "wiki/INDEX.md counts if needed, append wiki/log.md, then finish_compile."
    )

    client = OpenAI(api_key=api_key)
    messages: list[dict] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    finish_payload: dict | None = None

    for _ in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=DEFAULT_COMPILE_MODEL,
            messages=messages,
            tools=_COMPILER_TOOLS,
            tool_choice="auto",
        )
        choice = response.choices[0]
        assistant_msg = choice.message
        assistant_record: dict = {"role": "assistant", "content": assistant_msg.content or ""}
        if assistant_msg.tool_calls:
            assistant_record["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_msg.tool_calls
            ]
        messages.append(assistant_record)

        if not assistant_msg.tool_calls:
            break

        for tc in assistant_msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            output, finish = _dispatch_compiler_tool(tc.function.name, args)
            if finish is not None:
                finish_payload = finish
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": output,
                }
            )

        if finish_payload is not None:
            break

    if finish_payload is None:
        return {
            "status": "error",
            "message": (
                "Compile did not finish in time. Try again or compile manually "
                "with Claude Code ('compile the wiki')."
            ),
            "pending_sources": [p["path"] for p in pending],
        }

    processed = finish_payload.get("processed_sources") or []
    affected = finish_payload.get("affected_by_source") or {}
    manifest = load_manifest()
    _apply_manifest_updates(manifest, processed, affected)

    return {
        "status": "ok",
        "message": finish_payload.get("summary", "Wiki compiled."),
        "processed_sources": processed,
        "updated_articles": finish_payload.get("updated_articles") or [],
        "created_articles": finish_payload.get("created_articles") or [],
        "wiki_map_hint": "Wiki map refreshed — new articles are now searchable.",
    }