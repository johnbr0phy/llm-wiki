# Caliper Inc. — Company Overview (Jan 2026)

**Type:** Strategy doc  
**Author:** Maya Chen (CEO)  
**Audience:** Leadership + new hires

## What Caliper is

Caliper is a B2B SaaS company that sells **governed business metrics** to mid-market and enterprise ops teams. Customers connect data sources (ERP, CRM, warehouse tables, spreadsheets) and Caliper turns them into versioned, auditable metric definitions that product, finance, and ops teams can trust.

Tagline internally: *"Measure twice, ship once."*

## Stage and traction

- **Founded:** 2022, San Francisco
- **Employees:** ~48 (32 eng/product, 16 GTM + ops)
- **ARR:** $4.2M (Jan 2026), up from $2.1M a year ago
- **Customers:** 34 paying accounts; 6 enterprise ($100k+ ACV)
- **Flagship product:** **Caliper Atlas** — web app + API for metric governance
- **Secondary product:** **Caliper Beacon** — lightweight SDK for embedding live metrics in customer apps (beta)

## 2026 company goals

1. **Atlas enterprise:** Close 10 new enterprise logos; ship SSO, row-level security, and audit exports by Q3.
2. **Beacon v2:** GA mobile + web components — **deprioritized to H2** after April planning (see kickoff notes).
3. **Warehouse-first pipeline:** Finish migration off the legacy Postgres metric store to Snowflake-backed compute (decision made Feb 2026).
4. **Profitability path:** Reach cash-flow neutral by Q4 without a new fundraise.

## Org structure

| Leader | Role | Owns |
|--------|------|------|
| Maya Chen | CEO | Company strategy, enterprise sales, board |
| James Okafor | CTO | Platform, data pipeline, security |
| Priya Shah | VP Product | Atlas roadmap, design, customer discovery |
| Elena Ruiz | VP Customer Success | Onboarding, expansions, support SLAs |
| John Brophy | Eng Lead (Atlas) | Atlas core team, delivery cadence |

## Competitive landscape

Primary competitors: Looker semantic layer workflows, Monte Carlo-style observability vendors (partial overlap), and internal "metrics spreadsheets." Caliper wins on **governed definitions + changelog audit trail**, not on charting.

## Risks called out in this doc

- Enterprise deals stalling on security review (need SOC 2 Type II — in progress, target July 2026).
- Legacy metric store still serving 40% of queries during Snowflake migration.
- Beacon beta customers confused about overlap with Atlas API — positioning work needed.