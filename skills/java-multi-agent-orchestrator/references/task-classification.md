# Task classification and topology

Use the smallest topology that materially improves the result. File counts are signals, not rigid thresholds.

## Small

Typical signals:

- The exact file or method is known.
- The change is local to one or two tightly related files.
- No call-chain, schema, transaction, or compatibility uncertainty exists.

Action: keep the task with the root agent. Do not spawn children merely because tools are available.

## Medium

Typical signals:

- The location is partly unknown or one bounded module needs investigation.
- The change spans roughly three to eight related files.
- One implementation path is likely after a focused discovery pass.

Topology: root -> one read-only explorer -> one worker. Add one read-only reviewer for public API, persistence, authorization, or transaction changes.

## Large

Typical signals:

- Multiple modules or layers are affected.
- Call-chain or impact analysis is required.
- Independent workstreams exist, such as API contract analysis and persistence analysis.
- Several workers can own disjoint files or modules.

Topology: root -> up to two complementary explorers -> root synthesis and task DAG -> workers in conflict-free waves -> reviewer -> targeted rework.

## Extra-large or high risk

Typical signals:

- Database migration, data-loss potential, authorization, concurrency, money, or backward compatibility is involved.
- The request implies an architectural migration or many modules with unclear boundaries.
- A wrong assumption would materially change the implementation.

Topology: evidence-first discovery with specialists as needed. Produce a risk-aware implementation plan before writing. If the user's request already authorizes implementation and the plan remains in scope, continue; otherwise stop when a material scope decision requires user direction.

## Useful decomposition axes

Split by complementary evidence or exclusive ownership:

- HTTP/API contract vs. service/business logic vs. persistence/schema.
- Current behavior vs. impact surface vs. test/verification impact.
- Separate modules with no overlapping files.
- Implementation vs. read-only review.

Do not split one tightly coupled method, one shared migration, or the same file across concurrent workers.
