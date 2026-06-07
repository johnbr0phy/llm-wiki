# Caliper Voice Demo 🎙️

Fictional company **Caliper Inc.** — governed-metrics B2B SaaS. The wiki is pre-compiled from 7 raw sources.

## One-time setup

```bash
cd ~/llm-wiki/voice
./setup.sh
```

Edit `voice/.env` and replace the placeholder:

```
OPENAI_API_KEY=sk-your-real-key-here
```

Then launch:

```bash
./run.sh
```

Press **Option + Space** to toggle the mic.

> macOS: grant **Microphone** + **Accessibility** to your terminal app (System Settings → Privacy & Security).

## Demo script — Query (read)

Try these after toggling the hotkey:

| Say this | What it tests |
|----------|----------------|
| "What is Caliper?" | Company overview from wiki |
| "What's the status of Atlas?" | Project article + RLS/SAML |
| "Tell me about the Northwind deal" | Timeline + enterprise win ($140k) |
| "Why was Beacon v2 delayed?" | Decision article |
| "What is John Brophy working on?" | People article (you're the eng lead) |
| "Snowflake or BigQuery?" | Warehouse decision |
| "How much legacy Postgres traffic is left?" | Migration project (~18%) |

## Demo script — Maintain (write)

| Say this | What happens |
|----------|----------------|
| "Note that Brightpath Health signed on June 10th for 95k" | `save_voice_note` → `raw/calls/` |
| "Update the wiki" | `compile_wiki` folds the note into articles |

## What's in the wiki

| Section | Count | Examples |
|---------|-------|----------|
| Projects | 3 | Atlas, Beacon, Platform Migration |
| People | 7 | Maya, James, Priya, John, Elena, Dev, Sofia |
| Decisions | 2 | Snowflake primary, Beacon delay |
| Concepts | 2 | Governed metrics, Warehouse-first |
| Timeline | 2 | 2026 Q1, Q2 |

Raw sources live in `raw/docs/`, `raw/calls/`, `raw/email/`, `raw/slack/` (Caliper-* files).

## Quick verify (no API key needed)

```bash
cd ~/llm-wiki/voice
./.venv/bin/python -c "import wiki_context; print(len([l for l in wiki_context.build_system_context().splitlines() if l.startswith('- \`')]), 'articles in map')"
```

Should print **16 articles in map**.