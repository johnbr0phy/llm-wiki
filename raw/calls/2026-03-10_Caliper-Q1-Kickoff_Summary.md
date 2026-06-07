# Caliper Q1 2026 Kickoff — Call Summary

**Date:** 2026-03-10  
**Attendees:** Maya Chen, James Okafor, Priya Shah, Elena Ruiz, John Brophy, Dev Patel  
**Facilitator:** Maya Chen  
**Type:** All-hands planning session

## The plan (Q1)

Maya opened with Q1 theme: **"Earn enterprise trust."**

### Atlas
- Ship SAML SSO beta by end of March
- Row-level security (RLS) — design locked, eng starts April
- Close 3 enterprise pilots started in Q4 2025

### Beacon
- Original plan: Beacon v2 beta in April
- **Revised in this meeting:** Beacon v2 pushed to H2; team reallocates 2 engineers to Atlas enterprise

### GTM
- Elena to run onboarding playbook v2 for enterprise accounts
- Target: reduce time-to-first-metric from 21 days to 14 days

## Decisions made on the call

1. **Beacon v2 delay** — Priya proposed, Maya approved. Reason: enterprise pipeline needs RLS + audit exports first; only 4 Beacon beta customers vs 12 enterprise Atlas prospects.
2. **John Brophy** explicitly named delivery lead for Atlas enterprise bundle (SSO + RLS + audit export MVP).
3. **Weekly enterprise standup** — new 30-min meeting, Wednesdays, Maya + Elena + John.

## Notable quotes / inputs

- **James:** "Dual-write to the legacy metric store is our biggest reliability risk. I want cutover by June, not end of Q2."
- **Priya:** "Customers don't buy Beacon because it's cute — they buy Atlas because finance can audit the number."
- **John:** Committed Atlas API team to SAML beta by 2026-03-28; flagged risk if Auth0 sandbox keeps flaking.
- **Elena:** Reported Northwind Logistics stalled on security questionnaire — needs SOC 2 timeline for legal.

## Open questions

- Do we announce Beacon delay to beta customers this week or wait until April newsletter?
- Can Dev Patel split time 50/50 compiler migration vs RLS backend?

## Action items

| Owner | Action | Due |
|-------|--------|-----|
| John Brophy | SAML beta delivery | 2026-03-28 |
| James Okafor | SOC 2 timeline doc for sales | 2026-03-17 |
| Priya Shah | Beacon customer comms draft | 2026-03-14 |
| Elena Ruiz | Northwind security follow-up | 2026-03-12 |