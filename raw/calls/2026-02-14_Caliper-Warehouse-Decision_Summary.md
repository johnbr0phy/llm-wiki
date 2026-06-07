# Caliper Data Warehouse Decision — Call Summary

**Date:** 2026-02-14  
**Attendees:** James Okafor, Dev Patel, John Brophy, Priya Shah (optional listener)  
**Type:** Architecture decision record (verbal)

## Context

Caliper's metric compiler needed a primary warehouse target for the warehouse-first pipeline. Team evaluated Snowflake vs BigQuery for greenfield enterprise customers.

## Decision

**Snowflake is the primary warehouse for all new customers.** BigQuery adapter stays in maintenance mode for 2 existing customers only — no new BigQuery sales.

## Reasoning (James)

- 9 of 12 enterprise prospects standardized on Snowflake
- Snowflake row access policies align better with planned Atlas RLS model
- BigQuery adapter costs 0.4 FTE to maintain for 2 logos

## Consequences

- Compiler team prioritizes Snowflake query plans (Dev Patel lead)
- Sales deck updated by Priya — removed BigQuery from "supported warehouses" slide
- Migration off legacy Postgres metric store becomes Snowflake-centric

## John Brophy input

- Asked for clearer deprecation timeline for Postgres store dual-write
- James committed to milestone plan by end of February (delivered in architecture spec update)