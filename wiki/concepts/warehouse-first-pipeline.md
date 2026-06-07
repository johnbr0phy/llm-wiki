# Warehouse-First Pipeline

**Last updated:** 2026-06-06

**TLDR:** Metric compute runs against customer warehouses (Snowflake primary), replacing Caliper's legacy Postgres metric store.

## Summary

Caliper's architecture shift: the Metric Compiler generates SQL against customer-owned warehouses, Query Executor runs on Snowflake (primary), and Atlas API serves results. Customer data stays in their warehouse; Caliper stores definitions and audit logs only.

Migration off the legacy Postgres metric store is ongoing (18% traffic May 2026). Dual-write during migration caused April incidents. Target <5% legacy traffic by 2026-06-30.

## Related

- [[caliper-platform-migration]]
- [[james-okafor]]
- [[2026-02-14_snowflake-primary-warehouse]]

## Sources

- [Architecture spec](../../raw/docs/2026-02-01_Caliper-Platform-Architecture_Spec.md)
- [Warehouse decision](../../raw/calls/2026-02-14_Caliper-Warehouse-Decision_Summary.md)
- [Eng slack digest](../../raw/slack/2026-05-28_Caliper-Engineering-Slack-Digest_Summary.md)