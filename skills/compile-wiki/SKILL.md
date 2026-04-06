---
name: compile-wiki
description: Incrementally compile and update the LLM-maintained wiki from raw source data. Use when new call transcripts, emails, or project docs need to be folded into the wiki.
---

# Compile Wiki

Incrementally update the wiki from raw source data. The wiki is an LLM-compiled knowledge base - Claude maintains it, you review it.

## Wiki Location

```
wiki/
├── INDEX.md              <- slim top-level (section pointers + counts only)
├── log.md                <- append-only changelog (update after every compile)
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

**Index strategy:** The top-level INDEX.md is intentionally slim (~10 lines). Full article listings live in each section's INDEX.md. When creating new articles, update the **section INDEX.md**, not the top-level one (unless the article count changed).

## Raw Source Locations

All raw data lives in `raw/`, organized by type. All folders are **flat** - no subdirectories.

```
raw/
├── calls/           <- call transcripts, summaries, and excerpts (flat)
├── email/           <- email digests (flat)
├── docs/            <- all other docs - specs, research, strategy, etc. (flat)
└── slack/           <- channel summaries (flat)
```

**File naming convention:** `YYYY-MM-DD_Description_Type.ext`
- ISO date first, hyphens in date, underscores between segments
- No spaces - use hyphens within segments
- If no date can be determined, prefix with `undated_`

**When new raw data arrives**, save to the correct folder:
- Call recording/transcript/summary/excerpt -> `raw/calls/`
- Email digest or summary -> `raw/email/`
- Slack thread or channel summary -> `raw/slack/`
- Everything else (docs, specs, research, strategy) -> `raw/docs/`

**Source links in wiki articles** use relative paths:
- From `wiki/projects/`: `../../raw/calls/filename.md` or `../../raw/docs/filename.ext`
- From `wiki/timeline/`: same pattern
- From `wiki/people/`, `wiki/decisions/`, `wiki/concepts/`: use `[[backlinks]]` to other wiki articles

## Manifest

The manifest at `raw/.manifest.json` tracks what has been processed:

```json
{
  "last_compile": "ISO timestamp",
  "processed": {
    "relative/path/to/file.md": {
      "processed_at": "ISO timestamp",
      "size": 12345,
      "affected_articles": ["projects/example.md", "people/alice.md"]
    }
  }
}
```

## Compile Workflow

### Step 1: Find New Data

1. Read `raw/.manifest.json`
2. Scan all raw source locations for files
3. Compare against manifest - find files that are:
   - Not in the manifest (new)
   - In the manifest but with a newer modification date or different size (changed)
4. Report what's new: "Found X new files, Y changed files"

If nothing is new, say so and stop.

### Step 2: Read and Classify New Data

For each new/changed file:
1. Read the file
2. Identify which projects it relates to
3. Identify which people are mentioned
4. Identify any decisions made
5. Identify any new concepts or patterns

### Step 3: Update Wiki Articles

**Project articles** (`projects/*.md`):
- If the project article exists, update it incrementally:
  - Add new events to the Timeline table
  - Update the Summary if status has changed
  - Add new items to Key Decisions, Open Questions
  - Update "Last updated" date
  - Add new source to Source Material
- If a new project is discussed that has no article, create one
- DO NOT rewrite sections that haven't changed

**People articles** (`people/*.md`):
- **This is not optional.** Every project article update should trigger a check: "did a person do something notable here?" If yes, update their people article too.
- Notable = provided a correction, made a decision, gave technical input, flagged a risk, delivered something, blocked something. If they contributed new information that changed the wiki, they get a Recent Activity entry.
- If a person appears in 2+ projects or plays a significant role in any project and has NO article, **create one**
- If they already have an article, update Recent Activity and Current Involvement
- Add new Key Positions / Recurring Themes if patterns emerge
- Don't create articles for one-off external contacts (e.g., a customer mentioned once in a call)
- DO NOT rewrite the entire article

**Decision articles** (`decisions/YYYY-MM-DD_description.md`):
- **Create a new article** if the decision is architecturally significant, affects multiple projects, or changes strategic direction
- Don't create articles for routine scoping calls or minor prioritization
- Use date-prefixed filenames for chronological sorting

**Concept articles** (`concepts/*.md`):
- **Create a new article** if a genuinely new cross-project pattern emerges that doesn't fit into an existing concept
- Update existing concepts if new data adds nuance

**Timeline articles** (`timeline/YYYY-QX.md`):
- Add new events to the Key Events table
- Update project status table if status changed

### Step 4: Update Section Indexes

If any new articles were created:
- Add them to the appropriate **section INDEX.md** (e.g., `projects/INDEX.md`, `people/INDEX.md`)
- Keep the same table format as existing entries
- Decisions should be in chronological order
- Update the article count in the **top-level INDEX.md** only if the total changed

### Step 5: Update log.md

Append an entry to `wiki/log.md`:
```
## [YYYY-MM-DD] compile | Processed X new sources
- Updated: [list of updated articles]
- Created: [list of new articles, if any]
```

### Step 6: Update Manifest

Update `raw/.manifest.json` with:
- New `last_compile` timestamp
- All newly processed files with their metadata

### Step 7: Report

Output a summary of what changed:
```
Wiki compiled: YYYY-MM-DDTHH:MM:SS

New sources processed: 3
- email/YYYY-MM-DD_Email-Summary.md
- calls/YYYY-MM-DD_Team-Standup_Summary.md
- docs/YYYY-MM-DD_Feature-Spec_Notes.md

Articles updated: 5
- projects/feature-x.md (added sprint review notes, updated timeline)
- projects/feature-y.md (updated status)
- people/alice.md (added recent activity)
- people/bob.md (added recent activity)
- timeline/YYYY-Q2.md (added 2 events)

Articles created: 0

Next compile: run again after new data lands
```

## Article Formats

### Project Article
```markdown
# [Project Name]

**Status:** [current status]
**Owner:** [who owns this]
**Last updated:** YYYY-MM-DD

**TLDR:** [One sentence, under 25 words. What it is, what stage, why it matters.]

## Summary
[2-3 paragraphs]

## Key Decisions
- YYYY-MM-DD: [What was decided]
  - Source: [link to raw source]

## Open Questions
- [Unresolved items]

## People
- [[person-name]] - [role in this project]

## Timeline
| Date | Event | Source |
|------|-------|--------|

## Source Material
- [Links to all raw sources]
```

### Person Article
```markdown
# [Full Name]

**Role:** [Title, Team]
**Last updated:** YYYY-MM-DD

**TLDR:** [One sentence, under 25 words. Role and primary relevance.]

## Current Involvement
- [[project-name]] - [role] (status)

## Key Positions / Recurring Themes
- [Patterns across projects]

## Recent Activity
- YYYY-MM-DD: [Notable action or statement]

## Sources
- [Links to project articles]
```

### Decision Article
```markdown
# [Decision Title] (YYYY-MM)

**Decision:** [What was decided]
**Made by:** [Who]
**Date:** YYYY-MM-DD

**TLDR:** [One sentence, under 25 words. What was decided and the key consequence.]

## Context
## Reasoning
## Consequences
## Related
## Sources
```

## Special Source Types

### Planning Documents (all hands, kickoffs, roadmap sessions)

Company-wide planning docs don't just add events - they define **what the plan was**. When processing these:

1. **Update timeline Summaries, not just event tables.** Split into "The Plan" (what was supposed to happen) and "What Actually Happened" (reality vs. plan).
2. **Capture the structure.** If organized by teams or themes, reflect that.
3. **Note what was explicitly out of scope.** What's NOT being done is just as important.
4. **Update project articles with their place in the plan.**
5. **Update people articles.** Who presented what reveals ownership.

### Email Digests

Email digests contain many small updates across projects. Process each item independently - don't batch them into a single timeline entry. Each email thread that affects a project gets its own timeline row.

## Important Rules

1. **Incremental, not full rewrite.** Only touch sections affected by new data.
2. **Obsidian backlinks everywhere.** Use `[[article-name]]` for all cross-references within wiki articles.
3. **Date-stamp everything.** Events, decisions, activity - always include the date.
4. **Cite sources.** Every claim in the wiki should trace back to a raw source.
5. **Don't invent.** If the data isn't in the raw sources, don't add it to the wiki.
6. **Every article gets a TLDR.** One sentence, under 25 words, after the metadata block. Update the TLDR when status changes significantly.
7. **Update section indexes, not the top-level INDEX.md.** Only update the top-level count if it changed.
8. **Always append to log.md.** Every compile writes an entry. Format: `## [YYYY-MM-DD] compile | Description`.
9. **Decisions get date prefixes.** `YYYY-MM-DD_description.md` for chronological sorting.
10. **Use agent teams** (TeamCreate) for compiles. When processing multiple new sources, create a team so teammates can coordinate - e.g., one teammate updating a project article can tell another teammate updating the related person article what changed. Use Sonnet for teammates doing mechanical work (appending timeline rows, updating dates, adding source links). Use Opus for teammates that need judgment (writing new articles, resolving contradictions, generating TLDRs). Teammates should claim tasks from a shared task list and communicate directly when their work overlaps (same person mentioned in two sources, same project updated by two teammates, etc.).
