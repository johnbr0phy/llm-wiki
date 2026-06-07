# Caliper Atlas Enterprise Launch Review — Call Summary

**Date:** 2026-04-22  
**Attendees:** Maya Chen, Priya Shah, John Brophy, Elena Ruiz, James Okafor (joined last 15 min)  
**Type:** Sprint review / launch retro

## What shipped (April sprint)

- **SAML SSO beta** — shipped 2026-03-27 (1 day early). John Brophy's team delivered.
- **Audit log export (CSV)** — shipped 2026-04-18 for 3 pilot enterprises
- **RLS** — backend complete, UI behind feature flag; Priya wants 1 more design review before GA

## Customer outcomes

- **Northwind Logistics** — signed $140k ACV enterprise deal on 2026-04-20 after SOC 2 timeline letter from James
- **Helios Manufacturing** — expanded seats (+$32k) after audit export demo
- **Beacon beta** — 1 of 4 customers churned (Smallsoft); cited confusion with Atlas API overlap

## Decisions

1. **RLS GA target:** 2026-05-15 — Priya set date; John agreed if UI review closes by May 2
2. **Audit export Parquet format** — deferred to Q3; CSV enough for current compliance asks
3. **Marketing message:** Maya wants external copy to say "governed metrics platform" not "analytics dashboard"

## John Brophy — notable contributions

- Led SAML delivery; credited by Maya on the call
- Raised concern that compiler dual-write caused 2 incidents in April (incorrect ARR metric for internal demo tenant)
- Proposed **metric definition changelog** UI as fast follow after RLS — Priya added to Q2 backlog

## Risks

- Legacy Postgres metric store still on critical path for 35% of queries (down from 40% in January)
- James absent first 45 min — team noted need clearer migration milestone dates

## Next sprint focus

- RLS UI + GA
- Compiler dual-write incident postmortem (James + Dev Patel)
- Enterprise onboarding playbook v2 rollout with Elena