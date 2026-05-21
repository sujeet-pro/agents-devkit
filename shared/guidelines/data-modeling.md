# guideline: data modeling

> Loaded when the task involves a database schema, migration, ORM change, data lake table, or warehouse model.

## Hard rules

1. **Migrations are forward-only** with a documented rollback. No "down migration" that destroys data.
2. **No schema change without a deploy plan** if the column is used by running code. Ship in two steps: (1) add nullable + dual-write, (2) backfill + flip read, (3) drop old.
3. **Indexes after queries, not before**. Profile actual query patterns before adding an index. Indexes cost on writes.
4. **PII columns are explicit**: tagged in the column comment and in ``connectors/<source>.md` frontmatter `pii_columns``. Never query without the user naming the column.
5. **No SELECT \***  in production code. Name columns.
6. **Foreign keys with ON DELETE behavior** specified. Default to `RESTRICT` unless you mean otherwise.

## Decision: when to denormalize

- **Read-heavy + stable shape + skewed read/write ratio** > 100:1 → consider denorm.
- **Computed aggregates accessed often** → materialized view OR a write-time-maintained column.
- **Lookup that's 95% the same across rows** → keep the FK, don't inline.

## Decision: JSON column vs row column

- Use JSON when the schema genuinely varies per row (event payloads, integration responses).
- Don't use JSON to dodge a schema migration. The migration is cheaper than the technical debt.
- Index JSON path queries explicitly (`USING GIN` for Postgres) if you'll filter.

## Warehouse modeling (Snowflake / BigQuery)

- **Star schema** for analytics: fact table joins to dimensions. Wide fact, narrow dimensions.
- **Slowly-changing dimensions**: type-2 (versioned with valid_from/valid_to) when historical context matters; type-1 (overwrite) when only current matters.
- **Partitioning**: by date for time-series. Cluster on high-cardinality join keys.
- **Don't model OLTP shapes in the warehouse**. Flatten + denormalize for query speed.

## Anti-patterns

- Adding a column "just in case". Add when you have the use case.
- Making a column NULL when business logic says it's required. Constraint it.
- Using a string for a small enum. Use an enum type / lookup table.
- Storing JSON arrays of FK ids instead of a join table. Use the join table.
- Re-purposing a column for a new meaning. Add a new column.

## Cite when reviewing

- The migration file path.
- The repo's migration tooling (Alembic / Flyway / Liquibase / Knex / sqlx).
- `security.md` for any PII-touching migration.
- ``connectors/<source>.md` frontmatter` for table descriptions.
