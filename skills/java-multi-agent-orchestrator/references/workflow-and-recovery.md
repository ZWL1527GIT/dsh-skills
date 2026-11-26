# Workflow gates and recovery

## Gate 1: evidence

Do not build an implementation plan from unsupported summaries. Discovery results must identify the relevant files, symbols, and relationships. The root resolves contradictory findings before assigning edits.

## Gate 2: ownership

Maintain a simple root-owned ownership map:

```text
Worker A -> module-a/src/.../Controller.java, DTO.java
Worker B -> module-b/src/.../Service.java, Mapper.java, Mapper.xml
Root     -> shared configuration and final integration
```

If two workers need the same file, sequence them or give the complete file group to one worker. Do not ask workers to merge each other's changes.

## Gate 3: implementation waves

Dispatch only tasks whose inputs are stable. A later wave may depend on contracts produced by an earlier wave. Wait for the earlier wave, inspect its result, then update downstream contracts. Do not start dependent workers speculatively.

## Gate 4: combined inspection

Before review, the root inspects the combined diff and checks:

- Ownership was respected.
- No user or peer edits were reverted.
- Public API, DTO, entity, database, and mapper changes remain consistent.
- Imports, naming, and framework conventions match nearby code.
- No placeholder or unrelated cleanup entered the change.

## Gate 5: review closure

Send each actionable finding to the worker that owns the affected file. Allow at most two focused rework rounds for the same issue. The root then resolves it directly or reports the residual risk; do not loop indefinitely.

## Incomplete or failed children

1. Send one focused follow-up that names the missing evidence or deliverable.
2. If the child still fails, close or stop relying on it.
3. Reassign the bounded task when a slot is available, or let the root finish it.
4. Preserve completed useful findings; do not restart all discovery.

## Scope expansion

When a worker discovers required work outside ownership, it stops editing that area and reports:

- Why the extra change is necessary.
- Exact new files or modules.
- Whether the current implementation is safe to keep.
- What decision the root must make.

The root decides whether this is an in-scope replan or a material expansion requiring user direction.

## Conflict recovery

When edits overlap:

- Pause the affected workstream.
- Inspect the actual current files and diff.
- Identify user, peer, and worker changes without discarding any unknown edit.
- Reassign one owner and continue sequentially.
- Never use destructive reset or checkout commands to solve the conflict unless the user explicitly requests that operation.

## Completion report

The root's final answer includes the outcome, important changed files, validation performed, validation not performed because of instructions, and material remaining risks. Intermediate child chatter is not a substitute for a self-contained root answer.
