# Java repository rules

Apply these rules together with the repository's own `AGENTS.md`; repository-specific instructions win.

## Discovery

- If the exact file path is known, read that file directly.
- For a known string, endpoint, configuration key, or filename in a bounded scope, use targeted `rg` or `rg --files`.
- When the location is unknown or the task requires symbol lookup, call-chain analysis, dynamic dispatch, dependency tracing, or impact analysis, prefer CodeGraph when a repository `.codegraph/` index exists.
- If an existing CodeGraph index appears stale, follow the repository instruction for a single sync-and-retry before using the narrowest practical fallback.
- Avoid broad recursive scans on Windows-mounted or otherwise high-latency repositories.

## Java/Spring boundaries

Trace behavior across the actual layers in use rather than assuming a fixed architecture:

```text
Controller/API -> request/query/form object -> Service -> Manager/domain layer
-> Mapper/repository -> Mapper XML or annotations -> database
-> DTO/VO conversion -> response wrapper
```

Check neighboring code for framework conventions before introducing new patterns.

## Change ownership

Keep tightly coupled artifacts with one worker when practical:

- Entity plus field mapping and logical-delete annotations.
- Mapper interface plus Mapper XML statement/result mapping.
- DTO/VO plus the conversion code that populates it.
- Transactional method plus every directly controlled write path.
- API signature plus request validation and response compatibility changes.

Separate ownership by module only when contracts are stable and shared files are excluded.

## Risk checks

Review relevant risks for the requested change:

- Nullability, validation, dictionary values, and enum compatibility.
- Pagination totals, sorting, filters, tenant/data permissions, and logical deletion.
- Transaction rollback boundaries, partial writes, idempotency, and concurrency.
- SQL injection, dynamic column/order clauses, N+1 queries, and missing indexes.
- Backward compatibility of endpoints, JSON fields, DTO constructors, and mapper results.
- Java version and framework version compatibility.

## Validation

Follow active repository instructions. If builds, tests, compilation, or static analysis require explicit user authorization, do not run them automatically. Perform safe read-only inspection and report precise suggested commands instead. Never claim a command passed when it was not executed.
