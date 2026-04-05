# Automating Document Ingestion

This folder holds everything that isn't a call transcript or email: specs, research docs, strategy papers, briefs, presentations, and any other project documents.

## Sources

- **Google Docs / Slides** - Export as markdown or PDF
- **Confluence / Notion** - Export pages as markdown
- **Jira** - Export ticket details or sprint reports
- **Design tools** - Figma specs, Miro board exports
- **Research outputs** - Competitive analysis, customer research, data reports
- **Presentations** - Slide decks (.pptx), exported as markdown summaries

## Automation Approaches

### Manual (start here)
When you create or receive a significant document, save it here. This is the most common source type and the hardest to fully automate because documents come from everywhere.

Name files: `YYYY-MM-DD_Description_Type.ext` (e.g., `2025-06-15_Feature-X_Product-Brief.md`)

### Confluence/Notion watcher
If your team uses Confluence or Notion, set up a periodic export of recently updated pages in your project spaces. Many have APIs that support filtering by last-modified date.

### Google Drive sync
For teams that work heavily in Google Docs, a script that watches a shared folder and exports new/updated docs as markdown can keep this folder current.

### Jira export
A scheduled script that pulls recently updated tickets (sprint reports, completed stories, new epics) and saves summaries here. Useful for tracking what was actually built vs. planned.

## Tips

- Don't overthink the automation. Most teams start manual and only automate the highest-volume sources.
- One file per topic, not one file per day. A product brief is its own file, not bundled with other docs from the same day.
- Binary files (.docx, .pptx, .pdf) are fine here. The compile skill can read most formats.

## After Ingestion

Run "compile the wiki" to fold new documents into wiki articles.
