# Caliper Atlas

**Status:** Enterprise GA in progress — SAML SSO shipped, RLS GA 2026-05-15  
**Owner:** Priya Shah (product), John Brophy (eng delivery)  
**Last updated:** 2026-06-06

**TLDR:** Caliper's flagship governed-metrics web app and API; enterprise features (SSO, RLS, audit exports) are the 2026 focus.

## Summary

Caliper Atlas is the core B2B product: a web application and API where customers define, version, and audit business metrics against their own warehouses. Atlas is the primary revenue driver ($4.2M ARR company-wide as of Jan 2026) and the focus of the 2026 theme "earn enterprise trust."

Enterprise capabilities shipped or in flight include SAML SSO (beta shipped 2026-03-27), row-level security (GA 2026-05-15), and CSV audit log exports (shipped 2026-04-18). A metric definition changelog UI is queued as a fast follow after RLS.

## Key Decisions

- 2026-03-10: Beacon v2 delayed to H2; engineers reallocated to Atlas enterprise — Source: [Q1 kickoff](../../raw/calls/2026-03-10_Caliper-Q1-Kickoff_Summary.md)
- 2026-04-22: RLS GA target set to 2026-05-15 — Source: [launch review](../../raw/calls/2026-04-22_Caliper-Atlas-Launch-Review_Summary.md)
- 2026-04-22: Parquet audit export deferred to Q3; CSV sufficient for now — Source: [launch review](../../raw/calls/2026-04-22_Caliper-Atlas-Launch-Review_Summary.md)

## Open Questions

- When to ship metric definition changelog UI? (P0 for June per Slack digest)
- Automated plan diff checks after dual-write incidents — postmortem action item

## People

- [[priya-shah]] — VP Product, roadmap owner
- [[john-brophy]] — Eng lead, SAML + enterprise delivery
- [[james-okafor]] — Platform architecture, security controls
- [[elena-ruiz]] — Enterprise onboarding and customer outcomes
- [[sofia-nguyen]] — Senior PM, onboarding + changelog UX (from May 2026)
- [[dev-patel]] — Compiler migration support

## Timeline

| Date | Event | Source |
|------|-------|--------|
| 2026-03-10 | Q1 kickoff: John named Atlas enterprise delivery lead | [kickoff](../../raw/calls/2026-03-10_Caliper-Q1-Kickoff_Summary.md) |
| 2026-03-27 | SAML SSO beta shipped (1 day early) | [launch review](../../raw/calls/2026-04-22_Caliper-Atlas-Launch-Review_Summary.md) |
| 2026-04-18 | Audit log export (CSV) shipped to 3 pilots | [launch review](../../raw/calls/2026-04-22_Caliper-Atlas-Launch-Review_Summary.md) |
| 2026-04-20 | Northwind Logistics signed $140k ACV | [launch review](../../raw/calls/2026-04-22_Caliper-Atlas-Launch-Review_Summary.md) |
| 2026-05-15 | RLS GA | [slack digest](../../raw/slack/2026-05-28_Caliper-Engineering-Slack-Digest_Summary.md) |
| 2026-05-20 | Northwind first production RLS customer | [slack digest](../../raw/slack/2026-05-28_Caliper-Engineering-Slack-Digest_Summary.md) |

## Source Material

- [Company overview](../../raw/docs/2026-01-15_Caliper-Company-Overview_Strategy.md)
- [Platform architecture spec](../../raw/docs/2026-02-01_Caliper-Platform-Architecture_Spec.md)
- [Q1 kickoff](../../raw/calls/2026-03-10_Caliper-Q1-Kickoff_Summary.md)
- [Atlas launch review](../../raw/calls/2026-04-22_Caliper-Atlas-Launch-Review_Summary.md)
- [Weekly digest 2026-05-01](../../raw/email/2026-05-01_Caliper-Weekly-Digest_Email.md)
- [Eng slack digest](../../raw/slack/2026-05-28_Caliper-Engineering-Slack-Digest_Summary.md)