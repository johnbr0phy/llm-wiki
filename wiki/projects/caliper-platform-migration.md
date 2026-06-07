# Caliper Platform Migration (Warehouse-First)

**Status:** In progress — legacy Postgres store at 18% query traffic (May 2026)  
**Owner:** James Okafor  
**Last updated:** 2026-06-06

**TLDR:** Migrating metric compute from a legacy Postgres store to Snowflake-backed warehouse-first pipeline; cutover target June 2026.

## Summary

Caliper is executing a warehouse-first architecture: metric definitions compile to SQL against customer warehouses (Snowflake primary), with query execution replacing the legacy internal Postgres metric store. The compiler still dual-writes during migration, which caused incidents in April 2026 (incorrect ARR metric on an internal demo tenant).

Traffic on the legacy store dropped from 40% (Jan) → 35% (Apr) → 18% (May). James targets <5% by 2026-06-30 with a "cutover party" if <5% is hit by 2026-06-15. Table deletion proposed for August 2026 if traffic stays low.

## Key Decisions

- 2026-02-14: Snowflake primary for new customers; BigQuery maintenance-only — Source: [warehouse decision](../../raw/calls/2026-02-14_Caliper-Warehouse-Decision_Summary.md)

## Open Questions

- Exact date to stop dual-write? James wanted June vs end-of-Q2 tension noted on kickoff
- Edge cases in windowed metrics — fix merged 2026-05-27 (Dev Patel)

## People

- [[james-okafor]] — architecture owner
- [[dev-patel]] — compiler migration lead (~70% allocation May 2026)
- [[john-brophy]] — raised dual-write incident risk; Atlas API reliability

## Timeline

| Date | Event | Source |
|------|-------|--------|
| 2026-02-14 | Snowflake chosen as primary warehouse | [decision call](../../raw/calls/2026-02-14_Caliper-Warehouse-Decision_Summary.md) |
| 2026-04-22 | Dual-write caused 2 compiler incidents | [launch review](../../raw/calls/2026-04-22_Caliper-Atlas-Launch-Review_Summary.md) |
| 2026-04-30 | Dual-write postmortem published | [weekly digest](../../raw/email/2026-05-01_Caliper-Weekly-Digest_Email.md) |
| 2026-05-27 | Windowed metrics edge-case fix merged | [slack digest](../../raw/slack/2026-05-28_Caliper-Engineering-Slack-Digest_Summary.md) |

## Source Material

- [Architecture spec](../../raw/docs/2026-02-01_Caliper-Platform-Architecture_Spec.md)
- [Warehouse decision](../../raw/calls/2026-02-14_Caliper-Warehouse-Decision_Summary.md)
- [Q1 kickoff](../../raw/calls/2026-03-10_Caliper-Q1-Kickoff_Summary.md)
- [Launch review](../../raw/calls/2026-04-22_Caliper-Atlas-Launch-Review_Summary.md)
- [Eng slack digest](../../raw/slack/2026-05-28_Caliper-Engineering-Slack-Digest_Summary.md)