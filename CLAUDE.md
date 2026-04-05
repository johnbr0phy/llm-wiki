# Knowledge Base

This is an LLM-compiled knowledge base. It has two layers:

- **`wiki/`** - Compiled articles maintained by Claude. This is the primary source for answering questions.
- **`raw/`** - Source material (call transcripts, emails, docs). Only read these when wiki articles need more detail or verification.

## Answering Questions

When asked a question about any project, person, decision, or concept:

1. **Read `wiki/INDEX.md` first** - it lists sections and article counts (lightweight, ~10 lines)
2. **Read only the section index you need** - e.g., `wiki/projects/INDEX.md` for project questions, `wiki/people/INDEX.md` for people questions. Do NOT read all section indexes.
3. **Read TLDRs first** - every article has a `**TLDR:**` line near the top. Read TLDRs to decide which articles need full reading. This saves significant tokens.
4. **Read the relevant wiki article(s)** - only read full articles when the TLDR indicates relevance
5. **Only go to `raw/` if** the wiki doesn't have enough detail or the user asks for a direct quote / source verification

Do NOT scan raw files by default. The wiki exists so you don't have to.

## Compiling / Updating the Wiki

When the user says "compile the wiki", "update the wiki", or asks you to process new data:

1. Read `skills/compile-wiki/SKILL.md` for the full workflow
2. Check `raw/.manifest.json` to find what's new
3. Update wiki articles incrementally
4. Update the manifest

## Wiki Structure

```
wiki/
├── INDEX.md              <- start here (lightweight, just section pointers)
├── log.md                <- append-only changelog
├── projects/
│   ├── INDEX.md          <- full project listing
│   └── *.md
├── people/
│   ├── INDEX.md          <- full people listing
│   └── *.md
├── decisions/
│   ├── INDEX.md          <- full decisions listing
│   └── *.md
├── concepts/
│   ├── INDEX.md          <- full concepts listing
│   └── *.md
└── timeline/
    ├── INDEX.md          <- full timeline listing
    └── *.md
```

**Index strategy:** The top-level INDEX.md is intentionally slim (~10 lines) to minimize context usage. Full article listings live in each section's INDEX.md. Claude reads only the section index it needs per query.

**TLDR strategy:** Every wiki article has a `**TLDR:**` line after the metadata block. TLDRs are under 25 words and capture the essential what-and-where-it-stands. When compiling new articles, always include a TLDR.

**log.md:** `wiki/log.md` is an append-only chronological record of wiki changes (ingests, restructures, lint passes). Format: `## [YYYY-MM-DD] type | Description`. Update this on every compile or structural change.

## Raw Structure

```
raw/
├── calls/                <- transcripts, summaries, excerpts (flat)
├── email/                <- email digests (flat)
├── docs/                 <- all other docs - specs, research, strategy (flat)
└── slack/                <- channel summaries (future)
```

All folders are flat - no subdirectories. Files are named `YYYY-MM-DD_Description_Type.ext`.

## Cross-References

Wiki articles use Obsidian-style `[[backlinks]]`. When answering questions, follow these links to pull in related context from other articles.

## Saving New Files

When creating any new file, save it to the correct `raw/` folder by type:

| File type | Save to |
|-----------|---------|
| Call transcript or summary | `raw/calls/` |
| Call excerpt | `raw/calls/` |
| Email digest | `raw/email/` |
| Project doc (spec, research, discovery, brief) | `raw/docs/` |
| Strategy doc | `raw/docs/` |
| General doc | `raw/docs/` |

**Never save files to the repo root or to `wiki/`.** Everything goes into `raw/` - the wiki gets updated through the compile workflow.

**Naming convention:** `YYYY-MM-DD_Description_Type.ext` - no spaces, hyphens within segments, underscores between segments.

## Rules

- **Never edit raw files.** They are source material.
- **Wiki is Claude's domain.** Update articles through the compile workflow, not by hand.
- **Before updating ANY wiki article, read `skills/compile-wiki/SKILL.md` first.** This applies to full compiles AND ad-hoc updates. The compile skill has rules about updating people articles, TLDRs, log.md, and indexes that must be followed every time.
- **Before running a wiki health check or lint, read `skills/lint-wiki/SKILL.md` first.** Triggers: "lint the wiki", "check the wiki", "wiki health check", or any request to find contradictions/broken links/stale content.
- **Only state what the wiki says.** Do not generalize, round up, or add aspirational framing. If the wiki says "emails and landing pages," say that - not "emails, landing pages, and other content." If something is in discovery, say it's in discovery.
- **Cite sources.** At the end of every answer, list the wiki articles you drew from. Put each source on its own line using markdown links with full relative paths from the wiki root. Format:
  ```
  Sources:
  - [Project Name](wiki/projects/project-name.md)
  - [Person Name](wiki/people/person-name.md)
  ```
- **All new files go to `raw/`.** Nothing gets saved to the root or to `wiki/` directly.
