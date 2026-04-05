---
name: lint-wiki
description: Run a health check on the wiki. Auto-fixes what it can, reports contradictions and decisions that need human input.
---

# Lint Wiki

Run a quality check across the wiki. Fix what you can automatically, then report anything that needs human input.

## When to Use

- Periodically (weekly or after a large compile)
- After structural changes (renames, merges, project breakups)
- When the user says "lint the wiki", "check the wiki", or "wiki health check"

## Lint Passes

Run these checks in order. Use parallel agents for passes that are independent of each other.

### Pass 1: Structural Integrity (auto-fix)

**Broken backlinks:**
- Grep all `[[backlink]]` references across wiki articles
- Check that each target article exists as a .md file
- **Auto-fix:** If a close match exists (e.g., typo, old name), update the link. If no match, flag for review.

**Broken source links:**
- Check `../../raw/` relative paths in Source Material and Timeline sections
- Verify the target file exists
- **Auto-fix:** If the file was renamed and a close match exists, update. Otherwise flag.

**Orphan pages:**
- Find articles with zero inbound backlinks from other articles
- **Auto-fix:** None - report these. An orphan might be fine (new article) or might indicate it was disconnected during a rename.

**Missing inbound links:**
- For each project, check that at least the people listed in it link back to the project
- **Auto-fix:** Add missing backlinks to people's Sources/Current Involvement sections.

**Duplicate backlinks within articles:**
- Check each article for the same `[[backlink]]` appearing multiple times in Current Involvement or Sources sections
- Common after project merges/renames where sed replaces two different slugs with the same new slug
- **Auto-fix:** Merge duplicate entries - combine the descriptions into one line, remove the duplicate.

### Pass 2: Metadata & Conventions (auto-fix)

**Missing TLDRs:**
- Every article (excluding INDEX.md files) must have a `**TLDR:**` line after the metadata block
- **Auto-fix:** Read the article and generate a TLDR. Place it after the last metadata line, before the first `##` heading.

**Stale "Last updated" dates:**
- If an article has content referencing events newer than its "Last updated" date, the date is stale
- **Auto-fix:** Update to today's date.

**Missing metadata fields:**
- Projects need: Status, Owner, Last updated, TLDR
- People need: Role, Last updated, TLDR
- Decisions need: Decision, Made by, Date, TLDR
- **Auto-fix:** Add missing fields where the data is available in the article body.

**Section index out of sync:**
- Compare articles on disk vs entries in section INDEX.md files
- **Auto-fix:** Add missing entries, remove entries for deleted articles, update article counts in top-level INDEX.md.

### Pass 3: Content Quality (auto-fix where possible, flag where not)

**Contradictions:**
- Compare Status fields across related articles (e.g., a project's status vs how it's described in the timeline or decision articles)
- Compare dates: if an event appears in multiple articles, do the dates match?
- Compare ownership: if a project says "Owner: Team A" but a decision article says "Team B is building this", flag it
- **Cannot auto-fix.** Report each contradiction with the specific conflicting statements and file paths.

**Stale open questions:**
- Read each article's Open Questions section
- Check if any have been answered by newer content elsewhere in the wiki
- **Auto-fix:** If the answer is clearly in the wiki, remove the question. If uncertain, flag for review.

**Status drift:**
- Check if a project's Status field matches its most recent timeline entry
- **Auto-fix** if the timeline is clearly newer. **Flag** if ambiguous.

**Duplicate content:**
- Flag articles that cover substantially the same ground
- **Cannot auto-fix.** Report for the user to decide which to merge or delete.

### Pass 4: Completeness (report only)

**Thin articles:**
- Flag project articles with no Timeline section or fewer than 3 timeline entries
- Flag people articles with no Recent Activity
- Flag decision articles with no Consequences section

**Mentioned but missing:**
- Find `[[backlinks]]` that point to articles that don't exist yet
- Report the missing article name and which articles reference it

**Data gaps:**
- Projects with no customer/revenue context
- People with no Current Involvement entries
- Report these as suggestions, not errors.

## Output Format

After running all passes, produce a report:

```markdown
# Wiki Lint Report - YYYY-MM-DD

## Auto-Fixed (X items)
- [what was fixed] in [file] - [why]

## Needs Your Input (X items)

### Contradictions
- **[Topic]:** [Article A](path) says "[claim]" but [Article B](path) says "[claim]". Which is current?

### Decisions Needed
- [Question that only the user can answer]

## Health Summary
- Total articles: X
- Articles with TLDRs: X/X
- Orphan pages: X
- Broken links fixed: X
- Open contradictions: X
- Thin articles: X
```

## After Linting

1. **Append to log.md:**
   ```
   ## [YYYY-MM-DD] lint | Health check completed
   Auto-fixed X items. Y items flagged for review.
   ```

2. **Commit changes** if running in a git repo:
   ```
   git add -A && git commit -m "lint: auto-fix X items, flag Y for review"
   ```

## Important Rules

1. **Fix confidently, flag honestly.** If you're 90%+ sure of a fix, make it. If there's real ambiguity, flag it.
2. **Don't rewrite articles.** Lint fixes are surgical - update a link, add a TLDR, fix a date.
3. **Preserve voice.** When generating TLDRs or fixing metadata, match the style of existing articles.
4. **Report concisely.** Group issues by type, lead with the count, only include detail where a decision is needed.
5. **Use parallel agents.** Passes 1-4 can run concurrently since they read different things.
