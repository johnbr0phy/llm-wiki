# Automating Call Transcript Ingestion

This folder holds call transcripts, meeting summaries, and excerpts. Here's how to get data flowing in automatically.

## Sources

- **Gong** - API export or browser extraction of call transcripts
- **Fathom** - Auto-generated meeting summaries via email
- **Granola** - Local call notes (macOS)
- **Fireflies.ai** - Transcription service with API access
- **Otter.ai** - Meeting transcripts via email or API
- **Google Meet / Zoom** - Native meeting notes (usually arrive via email)

## Automation Approaches

### Manual (start here)
After each important call, save the transcript or summary to this folder. Name it `YYYY-MM-DD_Call-Name_Type.md` (e.g., `2025-06-15_Sprint-Review_Summary.md`).

### Email-based
Many transcription tools email summaries after calls. Set up a scheduled task that checks your email for these and saves them here. Filter by sender (e.g., `from:notifications@fathom.video`).

### API-based
If your transcription tool has an API (Gong, Fireflies, Otter), write a script that pulls recent transcripts on a schedule and saves them here.

### File watcher
If your tool saves files locally (Granola), set up a file watcher or cron job that copies new files to this folder when they appear.

## After Ingestion

Once files land here, run "compile the wiki" to fold them into wiki articles. The compile skill reads new files, identifies projects and people, and updates the relevant articles.
