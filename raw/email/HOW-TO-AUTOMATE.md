# Automating Email Ingestion

This folder holds email digests and summaries. Here's how to get data flowing in automatically.

## Recommended Approach

Set up a daily scheduled task that:
1. Searches your email for messages received in the last 24 hours
2. Filters out noise (calendar notifications, marketing, HR, vendor outreach)
3. Reads the full body of substantive emails
4. Writes a single daily summary to this folder

### File Format

One file per day: `YYYY-MM-DD_Email-Summary.md`

Each file should include:
- A section per notable email thread (subject, participants, summary)
- An "Action Items" section listing things explicitly assigned to you
- A "Skipped" section listing what was filtered out

### Example Scheduled Task Prompt (for Claude Cowork)

```
Check email daily for emails received in the last 24 hours.

1. Search Gmail for emails after yesterday's date
2. Skip: calendar notifications, HR, marketing, vendor outreach, Asana digests
3. Read the full body of substantive emails
4. Write a summary to /path/to/raw/email/YYYY-MM-DD_Email-Summary.md
5. Include an "Action Items" section (only items someone explicitly asked you to do)
6. Include a "Skipped" section

One file per day, all emails in one file.
```

### Gmail Integration

If using Claude Cowork with Gmail connected, the scheduled task can search and read emails directly. Set it to run each morning.

## After Ingestion

Run "compile the wiki" to fold email updates into project articles, people articles, and timelines.
