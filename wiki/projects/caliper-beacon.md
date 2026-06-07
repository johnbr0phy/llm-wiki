# Caliper Beacon

**Status:** Beta (v1.3 frozen); v2 delayed to H2 2026  
**Owner:** Priya Shah  
**Last updated:** 2026-06-06

**TLDR:** Lightweight SDK for embedding live metrics in customer apps; deprioritized behind Atlas enterprise work.

## Summary

Beacon is Caliper's secondary product — a TypeScript and Swift SDK that embeds pre-approved metrics in customer applications via the Atlas API (no direct warehouse access). As of early 2026 it remained in beta with four customers.

After the Q1 2026 kickoff, leadership delayed Beacon v2 from an April beta to H2 2026, reallocating two engineers to Atlas enterprise features. Beta customers were notified on 2026-04-29. One beta customer (Smallsoft) churned in April citing confusion with Atlas API overlap.

## Key Decisions

- 2026-03-10: Beacon v2 delayed to H2 — Source: [Q1 kickoff](../../raw/calls/2026-03-10_Caliper-Q1-Kickoff_Summary.md)
- 2026-04-29: Delay communicated to beta customers — Source: [weekly digest](../../raw/email/2026-05-01_Caliper-Weekly-Digest_Email.md)

## Open Questions

- Announce timing for any Beacon v2 eng allocation in June? (Slack: "not before changelog ships")
- Positioning vs Atlas API — pricing page confusion escalated to marketing

## People

- [[priya-shah]] — product owner
- [[maya-chen]] — approved delay and customer comms
- [[john-brophy]] — reviewing changelog API contracts (adjacent Atlas work)

## Timeline

| Date | Event | Source |
|------|-------|--------|
| 2026-03-10 | v2 beta pushed from April to H2 | [kickoff](../../raw/calls/2026-03-10_Caliper-Q1-Kickoff_Summary.md) |
| 2026-04-22 | Smallsoft churned from beta | [launch review](../../raw/calls/2026-04-22_Caliper-Atlas-Launch-Review_Summary.md) |
| 2026-04-29 | Delay email sent to beta customers | [weekly digest](../../raw/email/2026-05-01_Caliper-Weekly-Digest_Email.md) |

## Source Material

- [Company overview](../../raw/docs/2026-01-15_Caliper-Company-Overview_Strategy.md)
- [Architecture spec](../../raw/docs/2026-02-01_Caliper-Platform-Architecture_Spec.md)
- [Q1 kickoff](../../raw/calls/2026-03-10_Caliper-Q1-Kickoff_Summary.md)
- [Launch review](../../raw/calls/2026-04-22_Caliper-Atlas-Launch-Review_Summary.md)