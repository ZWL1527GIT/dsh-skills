# Behavioral evaluation cases

Use representative disposable tasks or read-only repository questions. Evaluate behavior and artifacts, not exact wording.

## Case 1: exact-file small fix

Request: change one known validation annotation in one known Java file.

Expected:

- The root keeps the task single-agent.
- No explorer or reviewer is spawned without a specific risk reason.
- The change remains limited to the requested file.

## Case 2: unknown endpoint call chain

Request: locate an endpoint and explain Controller-to-SQL behavior without editing.

Expected:

- One read-only explorer is sufficient unless distinct evidence lanes exist.
- The result cites files, symbols, line locations, and the data flow.
- No implementation worker is spawned.

## Case 3: bounded module feature

Request: add one field through Entity, DTO/VO, Service, Mapper, and Mapper XML in one module.

Expected:

- One worker owns the tightly coupled file group.
- The root avoids splitting Mapper Java and XML across concurrent workers.
- A reviewer checks serialization, mapping, nullability, and compatibility.

## Case 4: cross-module refactor

Request: change an API contract used by two modules.

Expected:

- Complementary explorers identify the producer and consumer impact.
- The root builds a dependency-ordered task DAG.
- Workers have disjoint ownership or run in sequential waves.
- The reviewer reports only actionable findings with locations and scenarios.

## Case 5: transaction or logical-delete defect

Request: diagnose and fix a defect that may cause partial writes or expose deleted records.

Expected:

- The task is classified high-risk.
- Discovery covers transaction boundaries, every write/query path, and tenant/data permissions where relevant.
- A specialist or high-capability reviewer is used only for the narrow risk question.
- P0/P1 findings block completion until resolved or explicitly reported.

## Case 6: overlapping worker proposal

Request: two apparent workstreams both require the same shared DTO.

Expected:

- The root detects overlapping ownership before parallel edits.
- The shared DTO is assigned to one owner or handled in an earlier wave.
- No destructive conflict recovery is used.

## Scorecard

Record for each case:

- Correct single-agent vs. multi-agent routing.
- Evidence completeness.
- Number of overlapping file assignments.
- Unnecessary agents or duplicated work.
- Actionable reviewer findings and escaped defects.
- Rework rounds and root interventions.
- Validation honesty.
- Wall-clock time and usage when available.

Change the skill only when an observed failure supports a focused rule. Avoid accumulating speculative instructions.
