# LLM-Compiled Wiki

A personal knowledge base that an LLM maintains for you. Drop raw data in (call transcripts, emails, docs), run the compiler, and get a structured, interlinked wiki you can query instantly.

Inspired by [Andrej Karpathy's approach](https://x.com/karpathy/status/1908244578702254571) to using LLMs as knowledge compilers.

## How It Works

```
You drop raw files in ──> LLM compiles them ──> Wiki updates automatically
     (transcripts,          (reads new data,       (structured articles
      emails, docs)          updates articles)       you can query)
```

**Two layers:**
- `raw/` - Your source material. Transcripts, emails, docs. Never edited by the LLM.
- `wiki/` - LLM-compiled articles. Structured, interlinked, searchable. The LLM maintains this - you read it.

**Three operations:**
1. **Ingest** - Drop a new file in `raw/`, run the compiler, wiki updates
2. **Query** - Ask a question, LLM reads the wiki and gives you a sourced answer
3. **Lint** - Periodic health check finds contradictions, stale content, broken links

## Quick Start

### 1. Set up your project

Open this folder in Claude Code or as a Cowork project. The `CLAUDE.md` file tells Claude how to use the wiki.

### 2. Drop your first raw files

Put some source material in the right folder:
- Call transcripts/meeting notes -> `raw/calls/`
- Email summaries -> `raw/email/`
- Everything else (docs, specs, research) -> `raw/docs/`

Name files: `YYYY-MM-DD_Description_Type.ext` (e.g., `2025-06-15_Sprint-Review_Summary.md`)

### 3. Run the first compile

Tell Claude: "compile the wiki"

It will read your raw files, generate wiki articles, and populate the indexes. Your first compile builds the wiki from scratch. After that, compiles are incremental - only new data gets processed.

### 4. Start querying

Ask questions like:
- "What's the current state of Project X?"
- "What decisions have we made about integrations?"
- "What has Sarah been involved in this quarter?"
- "What's on my plate this week?"

Claude reads the wiki index, finds the relevant articles, and gives you a sourced answer.

### 5. Keep feeding it

The more raw data you add, the smarter the wiki gets. Set up automated ingest for email (scheduled task) and transcripts (file watcher or manual drop).

## Directory Structure

```
llm-wiki/
├── CLAUDE.md                  <- Instructions for Claude (routing, rules, conventions)
├── plan.md                    <- Implementation guide and phasing
├── build_wiki.py              <- Static HTML site generator (optional)
├── skills/
│   ├── compile-wiki/SKILL.md  <- How to compile raw data into wiki articles
│   └── lint-wiki/SKILL.md     <- How to run wiki health checks
├── wiki/
│   ├── INDEX.md               <- Top-level index (section pointers only)
│   ├── log.md                 <- Append-only changelog
│   ├── projects/              <- One article per project
│   ├── people/                <- One article per person
│   ├── decisions/             <- Major decisions, date-prefixed
│   ├── concepts/              <- Cross-cutting patterns and ideas
│   └── timeline/              <- Quarterly summaries
└── raw/
    ├── .manifest.json         <- Tracks what's been compiled
    ├── calls/                 <- Meeting transcripts, summaries
    ├── email/                 <- Email digests
    ├── docs/                  <- Specs, research, strategy docs
    └── slack/                 <- Channel summaries (future)
```

## Wiki Article Types

### Projects
Track initiatives with status, ownership, decisions, open questions, timeline, and source links.

### People
Cross-project profiles showing what each person owns, their recurring positions, and recent activity.

### Decisions
Date-stamped records of significant choices - what was decided, why, and what it affected.

### Concepts
Patterns and ideas that span multiple projects (e.g., "governed content creation", "feature flags").

### Timeline
Quarterly summaries that capture what happened, what was planned, and how reality diverged from the plan.

## Key Principles

1. **Raw stays raw.** Never modify source material.
2. **The LLM is the author.** You direct it, but don't hand-edit wiki articles.
3. **Incremental compilation.** New data updates existing articles - no full rewrites.
4. **Everything backlinks.** Articles reference each other with `[[slug]]` links.
5. **TLDRs save tokens.** Every article has a one-line TLDR so Claude can decide whether to read the full article.
6. **Index files are lightweight.** Top-level index is ~10 lines. Full listings live in section indexes.
7. **Log everything.** The changelog (`log.md`) tracks every compile and structural change.

## Optional: Static Site Generator

`build_wiki.py` converts the wiki into a single self-contained HTML file you can open in a browser or share on Slack. It handles markdown conversion, backlink resolution, search indexing, and privacy filtering.

```bash
pip install markdown
python build_wiki.py
open wiki-site.html
```

## Customization

### Adapt the sections
The five sections (projects, people, decisions, concepts, timeline) work for product/engineering teams. Adapt them to your domain:
- Research team: papers, authors, methods, findings, timeline
- Sales team: deals, contacts, competitors, playbooks, timeline
- Personal: goals, people, decisions, interests, journal

### Add data sources
The system handles any text-based source. Common additions:
- Slack channel summaries (daily digest -> `raw/slack/`)
- Jira/Linear exports
- CRM notes
- Interview transcripts

### Privacy filtering
The build script supports stripping sensitive content (e.g., 1:1 quotes) when generating the HTML site. Customize the filter patterns in `build_wiki.py`.

## Works With

- **Claude Code** (terminal) - best for compiling, linting, structural changes
- **Claude Cowork** (desktop) - best for ad-hoc queries, single-file ingests, daily briefings
- **Obsidian** - great for browsing the wiki visually (backlinks, graph view)
- **Any markdown viewer** - the wiki is just markdown files
