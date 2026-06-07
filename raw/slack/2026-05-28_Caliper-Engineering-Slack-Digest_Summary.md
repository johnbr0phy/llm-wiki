# #caliper-eng Slack Digest

**Date range:** 2026-05-26 to 2026-05-28  
**Summarized by:** Dev Patel

## Highlights

### RLS shipped to GA (2026-05-15) ✅
- John Brophy announced GA in #releases; Priya posted customer-facing changelog
- Feature flag removed 2026-05-16 after 24h bake time
- Northwind first customer using RLS in production on 2026-05-20

### Compiler migration milestone
- James posted: legacy Postgres metric store now **18%** of query traffic (down from 35% in April)
- Target **<5%** by 2026-06-30; cutover party planned if hit by 2026-06-15
- Dev Patel flagged edge case with windowed metrics — fix merged 2026-05-27

### Incidents
- **2026-05-22** — 14-min Atlas API degradation (Redis failover). Root cause: connection pool misconfig. John Brophy's team shipped patch same day.
- No customer data loss; Northwind status page update sent by Elena

## Thread snippets

**@priya** in #product: "Changelog UI is P0 for June — Sofia leading, John reviewing API contracts."

**@maya** in #general: "Q2 ARR target $5.5M — we're at $4.8M with 4 weeks left. Enterprise focus."

**@james** in #architecture: "Do not onboard new BigQuery customers — Snowflake only per Feb decision."

## Open engineering questions

1. When to delete legacy Postgres metric store tables? James suggests August if <5% traffic holds.
2. Beacon v2 — any eng allocation in June? Priya says "not before changelog ships."