# DNA_phase4

## RElational Schema using Mysql

**DBMS:** MariaDB 10.11 | **Database:** `wbmc_db`


## Changes still needed
- Add backend/trigger validation for category limits, registration windows, age limits, minimum host-bid representatives, Best in Show eligibility, cancelled-edition results, approval of completed-result changes, rescheduling and self-replacement.
- Use transactions for multi-step operations and protect concurrent category-limit checks.
- Verify FK mappings and ENUM values against Stage D; test invalid inserts and confirm the test row is absent.
- Confirm the design choice: Phase 1's `ENTRY` alternative or Stage D's ternary `COMPETES_IN`.

## Important
- `src/schema_fixed.sql` starts with `DROP DATABASE IF EXISTS wbmc_db;`; rerunning it deletes the database and data. Back up is needed first.
