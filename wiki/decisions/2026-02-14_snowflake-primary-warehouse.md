# Snowflake as Primary Warehouse (2026-02)

**Decision:** Snowflake is the primary warehouse for all new Caliper customers; BigQuery adapter is maintenance-only for 2 existing logos.  
**Made by:** James Okafor (with Dev Patel, John Brophy)  
**Date:** 2026-02-14

**TLDR:** New sales and compiler work target Snowflake only; BigQuery frozen for two legacy customers.

## Context

Caliper needed a primary warehouse target for the warehouse-first metric pipeline. Nine of twelve enterprise prospects used Snowflake.

## Reasoning

- Snowflake row access policies align with planned Atlas RLS
- BigQuery adapter cost ~0.4 FTE for only 2 customers
- Compiler team can prioritize Snowflake query plans

## Consequences

- Sales deck updated — BigQuery removed from supported warehouses slide ([[priya-shah]])
- [[caliper-platform-migration]] becomes Snowflake-centric
- James committed Postgres dual-write milestone plan by end of February

## Related

- [[caliper-platform-migration]]
- [[james-okafor]]

## Sources

- [Warehouse decision call](../../raw/calls/2026-02-14_Caliper-Warehouse-Decision_Summary.md)
- [Architecture spec](../../raw/docs/2026-02-01_Caliper-Platform-Architecture_Spec.md)