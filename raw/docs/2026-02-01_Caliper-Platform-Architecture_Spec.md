# Caliper Platform Architecture Spec

**Version:** 0.9  
**Date:** 2026-02-01  
**Author:** James Okafor (CTO)  
**Status:** Approved for implementation

## Summary

Caliper Atlas runs on AWS (us-west-2). User-facing services are in EKS. Metric compilation and query execution are moving to a **warehouse-first** design backed by Snowflake.

## Core components

### Atlas API (Go)
- REST + GraphQL for metric CRUD, permissions, and query plans
- Auth via Auth0 (OIDC); enterprise SSO via SAML add-on (roadmap Q2)

### Metric Compiler (Python)
- Turns YAML metric definitions into SQL against customer warehouses
- Caches compiled plans in Redis (ElastiCache)
- **Migration note:** Compiler still dual-writes to legacy Postgres metric store until Q2 cutover

### Query Executor
- Snowflake primary (decided 2026-02-14)
- BigQuery adapter maintained for 2 existing customers only — no new sales

### Beacon SDK (TypeScript + Swift)
- Embeds pre-approved metrics in customer apps
- Reads from Atlas API; no direct warehouse access
- v2 delayed — current beta frozen at v1.3

## Data flow

```
Customer warehouse (Snowflake) 
    → Metric Compiler (plans) 
    → Query Executor 
    → Atlas API 
    → Web app / Beacon SDK
```

## Security

- All customer data stays in their warehouse; Caliper stores definitions + audit logs only
- SOC 2 Type II audit started Jan 2026; James owns technical controls
- Row-level security for Atlas enterprise: design complete, implementation starts March 2026

## Open technical questions

1. How long to keep dual-write to legacy Postgres store? James proposed end of Q2.
2. Should Beacon share the compiler cache or use a separate edge cache? Priya wants shared cache for consistency.
3. Audit export format — Parquet vs CSV for enterprise compliance team?

## People mentioned

- James Okafor — architecture owner
- Priya Shah — product requirements for RLS and audit exports
- John Brophy — leading Atlas API team delivery for enterprise features
- Dev Patel — staff engineer, compiler migration