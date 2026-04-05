# Automating Slack Ingestion

This folder holds Slack channel summaries and thread exports. Slack is the highest-volume, lowest-signal source - start here last.

## Approaches (from simplest to most comprehensive)

### 1. Tagged capture (recommended starting point)
Use a Slack workflow or bot that lets you tag a message or thread for capture. When tagged, it exports the thread as markdown to this folder. You control exactly what gets captured.

### 2. Channel summaries
A daily scheduled task that reads key Slack channels and writes a digest. The LLM filters for signal during the summary step, so you don't need to pre-filter.

Example prompt for a scheduled task:
```
Read the last 24 hours of messages in these Slack channels:
- #product
- #engineering
- #customer-success

Write a summary of substantive discussions to raw/slack/YYYY-MM-DD_Slack-Summary.md.
Skip: emoji reactions, one-word replies, social chat, bot notifications.
Include: decisions, blockers, action items, customer feedback, technical discussions.
```

### 3. Full archive + filter
Export everything from key channels, let the compile skill filter for relevance. Most complete, most expensive in tokens. Only worth it once you've proven the value of the wiki with simpler sources.

## File Format

- Daily summaries: `YYYY-MM-DD_Slack-Summary.md`
- Individual threads: `YYYY-MM-DD_Channel-Name_Topic.md`

## Tips

- Start with 2-3 high-signal channels, not all of Slack
- The compile skill is good at extracting project-relevant items from noisy summaries
- Slack data goes stale fast - compile frequently or the context loses value

## After Ingestion

Run "compile the wiki" to fold Slack updates into wiki articles.
