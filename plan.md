LLM-Compiled Knowledge Bases: Implementation Plan

Inspired by [Andrej Karpathy's approach](https://x.com/karpathy/status/1908244578702254571) to using LLMs as knowledge compilers - turning raw data into self-maintaining wikis.

## The Core Idea

Most knowledge workers already have the raw material scattered across their tools - call transcripts, meeting notes, email threads, Slack messages, project docs, tickets. The problem isn't generating information, it's synthesizing it. You end up context-switching between six tools to answer "what's the current state of Project X?"

Karpathy's insight: point an LLM at your raw sources and have it **compile** a wiki - a structured collection of interlinked markdown articles that the LLM maintains, not you. You rarely touch the wiki directly. It's the LLM's domain.

The result: instead of searching across tools, you query a knowledge base that already has the synthesis done. And every new piece of data makes the whole thing smarter.

## Architecture

```
knowledge-base/
├── wiki/                          <- LLM-compiled, LLM-maintained
│   ├── INDEX.md                   <- master index with brief summaries
│   ├── projects/
│   │   ├── project-alpha.md
│   │   ├── project-beta.md
│   │   └── ...
│   ├── people/
│   │   ├── alice-chen.md          <- spans every project they touch
│   │   ├── bob-martinez.md
│   │   └── ...
│   ├── decisions/
│   │   ├── 2026-03-buy-vs-build-image-editor.md
│   │   └── ...
│   ├── concepts/
│   │   ├── integration-patterns.md
│   │   └── ...
│   └── timeline/
│       ├── 2026-Q1.md
│       └── 2026-Q2.md
│
├── raw/                           <- source material, organized by origin
│   ├── calls/                     <- meeting transcripts
│   ├── email/                     <- digests, threads
│   ├── slack/                     <- exported threads, channel summaries
│   ├── tickets/                   <- Jira/Linear exports
│   └── docs/                      <- design docs, specs, research
│
└── scripts/                       <- automation for ingest + compile
```

### Key Principles

1. **Raw stays raw.** Never modify source material. The wiki is a compiled artifact.
2. **The LLM is the author.** You direct it, but you don't hand-edit wiki articles. If something is wrong, you feed it better data or correct its instructions.
3. **Incremental compilation.** New data updates existing articles - it doesn't trigger a full rewrite.
4. **Everything backlinks.** A project article links to relevant people, decisions, and source material. A person article links to every project they've touched.
5. **Index files are critical.** The LLM can't read everything on every query. It reads the index first, then dives into specific articles. Keep indexes concise - one line per article with a short summary.

## What a Wiki Article Looks Like

### Project Article

```markdown
# Project Alpha

**Status:** In progress - targeting Q2 launch
**Owner:** Alice Chen (engineering), Bob Martinez (product)
**Last updated:** 2026-03-28

## Summary
[2-3 paragraph synthesis of what this project is, why it matters, current state]

## Key Decisions
- 2026-02-14: Chose to buy off-the-shelf rather than build in-house
  - Source: [Sprint review call](../raw/calls/2026-02-14-sprint-review.md)
- 2026-03-01: Descoped mobile support to hit Q2 deadline
  - Source: [Planning meeting](../raw/calls/2026-03-01-planning.md)

## Open Questions
- How does this interact with the Platform team's API redesign?
- Still waiting on legal review of the vendor contract

## People
- [[alice-chen]] - Technical lead, raised concerns about component reuse
- [[bob-martinez]] - Product owner, driving the Q2 deadline

## Timeline
| Date | Event | Source |
|------|-------|--------|
| 2026-01-15 | Project kicked off | [Kickoff notes](../raw/calls/...) |
| 2026-02-14 | Buy vs build decided | [Sprint review](../raw/calls/...) |
| 2026-03-01 | Mobile descoped | [Planning](../raw/calls/...) |

## Source Material
- [Call excerpts tagged to this project]
- [Related Jira tickets]
- [Design docs]
```

### Person Article

```markdown
# Alice Chen

**Role:** Senior Engineer, Platform Team
**Last updated:** 2026-03-28

## Current Involvement
- [[project-alpha]] - Technical lead (active)
- [[project-beta]] - Reviewer (advisory)

## Key Positions / Recurring Themes
- Consistently advocates for component reuse across projects
- Raised concerns about API backward compatibility in Q1 planning
- Prefers incremental rollouts over big-bang launches

## Recent Activity
- 2026-03-17: Flagged risk in Alpha's timeline during leads meeting
- 2026-03-01: Proposed alternative architecture for Beta's data layer

## Sources
- [Leads meeting 2026-03-17](../raw/calls/...)
- [Architecture review 2026-02-20](../raw/calls/...)
```

### Decision Article

```markdown
# Buy vs Build: Image Editor (2026-02)

**Decision:** Buy off-the-shelf solution
**Made by:** Bob Martinez, Alice Chen
**Date:** 2026-02-14

## Context
[What problem we were solving, what options we considered]

## Reasoning
[Why we chose this path - cost, timeline, team capacity]

## Consequences
- Vendor dependency for a core feature
- Saved ~6 weeks of engineering time
- Need to maintain integration layer

## Related
- [[project-alpha]] - This decision directly affects Alpha's architecture
- [[alice-chen]] - Led the technical evaluation

## Sources
- [Sprint review transcript](../raw/calls/...)
- [Cost analysis doc](../raw/docs/...)
```

## Implementation Phases

### Phase 1: Structure + First Compile (Day 1)

**Goal:** Prove the format works on one project before automating anything.

**Steps:**
1. Create the `wiki/` directory structure
2. Pick one project with good data density (lots of call notes, docs, decisions)
3. Build a "compile" prompt/skill that:
   - Reads all raw sources for that project
   - Generates the project article
   - Generates people articles for key participants
   - Generates decision articles for any major calls
   - Creates the INDEX.md
4. Review the output in Obsidian (or any markdown viewer)
5. Iterate on the format - what's useful, what's noise?

**The compile skill needs clear instructions:**
- Read the current INDEX.md to understand what already exists
- Read new/changed source material
- Update or create articles (don't rewrite from scratch)
- Update the INDEX.md
- Add backlinks between articles
- Flag any contradictions or stale information

**Success criteria:** You ask a question about the project and the wiki gives you a better answer than searching through raw files would.

### Phase 2: Full Compile (Week 1)

**Goal:** Compile the full wiki across all active projects.

**Steps:**
1. Run the compile skill across every project that has source material
2. Let it generate cross-project articles (people, concepts, decisions)
3. Build out the timeline articles (Q1, Q2 summaries)
4. Review and tune - some articles will be too thin, others too verbose

**At this point you have a queryable knowledge base.** You can ask:
- "What's the current state of every active project?"
- "What open questions do we have across all projects?"
- "What has Alice been involved in this quarter?"
- "What decisions have we made about integrations?"

### Phase 3: Auto-Ingest (Week 2-3)

**Goal:** New data automatically flows into the wiki without manual intervention.

This is where it gets interesting. The specific tooling depends on your setup, but the pattern is the same:

**Call Transcripts:**
- Watch the `raw/calls/` folder for new files
- When a new transcript lands, run the compile skill
- It reads the transcript, identifies which projects/people are discussed, updates the relevant articles

**Email:**
- Daily pull of email digests into `raw/email/`
- Compile skill extracts project-relevant items, updates articles

**Tickets (Jira/Linear/etc):**
- Periodic export of recent ticket updates to `raw/tickets/`
- Compile skill syncs status changes into project articles

**Implementation options (from most to least automated):**
- **Scheduled LLM agents** - cron jobs that run a compile pass (Claude Code's `/schedule`, or any agent framework with cron support)
- **File watcher + hook** - a script that watches `raw/` for changes and triggers compilation
- **Manual with a shortcut** - a single command/skill that runs the full compile (lowest setup, still saves significant time)

### Phase 4: Linting + Health Checks (Week 3-4)

**Goal:** The wiki maintains its own quality.

Run periodic "health check" passes that:
- Find articles that haven't been updated in X weeks (stale?)
- Find open questions with no follow-up
- Find contradictions between articles (Project A says "launching Q2" but the timeline says "descoped")
- Find people who appear in raw data but don't have articles yet
- Suggest new articles based on recurring themes in raw data
- Check for broken backlinks

This is Karpathy's "linting" concept. The LLM audits its own knowledge base and flags problems.

### Phase 5: Slack Integration (Week 4+)

**Goal:** Capture the most ephemeral and highest-volume data source.

Slack is the hardest to pipe in because:
- Volume is high, signal-to-noise is low
- Conversations span channels and threads
- Context is often implicit

**Approaches:**
- **Channel summaries** - a daily agent that reads key channels and writes a digest to `raw/slack/`. The compile step then folds relevant items into the wiki.
- **Tagged capture** - a Slack bot or workflow that lets you tag a message/thread for inclusion. It dumps the thread to `raw/slack/` for processing.
- **Full archive + filter** - export everything, use the LLM to filter for signal during compilation. Most complete, most expensive in tokens.

Start with tagged capture or channel summaries. Full archive is overkill until you've proven the value.

## Tooling

### What You Need

| Component | Purpose | Options |
|-----------|---------|---------|
| LLM agent | The compiler | Claude Code, Cursor, Aider, any coding agent with file read/write |
| Markdown viewer | The frontend | Obsidian (best - has backlinks, graph view, plugins), VS Code, any markdown editor |
| Cron/scheduler | Auto-ingest triggers | Claude Code `/schedule`, cron jobs, GitHub Actions, n8n |
| Data connectors | Pull from external tools | MCP servers, APIs, Zapier/n8n, manual export |

### Obsidian as the IDE

Karpathy uses Obsidian as the "frontend" and it's a good fit:
- Native backlink support (`[[article-name]]` syntax)
- Graph view shows connections between articles visually
- Local-first, just reads from the file system
- Plugins for slides (Marp), charts, kanban, etc.
- Community plugin ecosystem for additional renderers

The key mental model: **Obsidian is the viewer, the LLM is the editor.** You browse and query through Obsidian, but you don't maintain the content by hand.

## Cost and Token Considerations

The main cost driver is compilation - the LLM reading source material and generating/updating articles.

**Rough math:**
- A typical call transcript: ~5-15K tokens to read
- Generating/updating a wiki article: ~2-5K tokens output
- A full compile across 10 projects with ~50 source docs: ~500K-1M tokens
- Daily incremental updates (2-3 new sources): ~50-100K tokens

This is very manageable. The compile step is the expensive part, but it only needs to run incrementally after the initial build.

**To keep costs down:**
- Always compile incrementally (update, don't rewrite)
- Keep INDEX.md summaries tight so the LLM can navigate without reading everything
- Use cheaper/faster models for routine compilation, save the expensive model for complex queries
- Batch daily sources into one compile pass rather than per-file

## What Success Looks Like

**Week 1:** You have a wiki for your most active project. You ask a question and get a better answer than you would from searching raw files.

**Week 4:** You have a wiki across all projects. When someone asks you "what's the status?" on anything, you query the wiki instead of digging through transcripts and email.

**Week 8:** The wiki updates itself daily. New call transcripts and emails automatically flow in. You notice things surfaced in the wiki that you would have missed - connections across projects, follow-ups that fell through the cracks.

**Week 12:** You can't imagine working without it. The wiki has become your single source of truth - not because it replaced your other tools, but because it synthesizes all of them.

## Open Questions

- **Granularity:** How deep should articles go? A project article could be 500 words or 5,000. Start lean and let it grow.
- **Staleness policy:** When is an article "stale"? 2 weeks without an update? Project-dependent?
- **Multi-user:** If teammates also want to query the wiki, does it stay local or get shared? Shared wikis need access controls and conflict resolution.
- **Source of truth conflicts:** When the wiki says one thing and a ticket says another, which wins? The wiki should always cite sources so you can verify.
- **Privacy boundaries:** Some raw sources (1:1 notes, HR discussions) shouldn't compile into shared wiki articles. Need clear rules about what gets compiled and what stays raw-only.