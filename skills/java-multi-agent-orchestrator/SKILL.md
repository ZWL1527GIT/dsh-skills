---
name: java-multi-agent-orchestrator
description: Orchestrate bounded subagent work for complex Java repository analysis, implementation, and review. Use only when the user explicitly asks for multiple agents, parallel analysis, delegation, or a main-agent/subagent workflow; keep ordinary small Java tasks single-agent.
---

# Java Multi-Agent Orchestrator

Coordinate Java repository work through a root agent that owns decisions, integration, and the final answer. Delegate only when the current user request explicitly authorizes subagents or parallel agent work. If collaboration tools are unavailable, state that limitation and complete the task with one agent where practical.

## Essential rules

- Preserve the user's requested outcome, scope, model, reasoning effort, and authorization boundaries.
- Follow repository `AGENTS.md` instructions before this skill. This skill never grants permission to build, test, publish, delete, or modify external systems.
- Delegate only independent, bounded work that can proceed concurrently. Keep tightly coupled reasoning or edits with one owner.
- The root agent remains responsible for task classification, task contracts, file ownership, synthesis, conflicts, review closure, and delivery.
- Parallelize read-only discovery freely within the available slot limit. Parallelize edits only when writable file sets are disjoint.
- Tell every editing worker that it is not alone in the repository, list its owned files or module, and prohibit reverting user or peer changes.
- Children must not create further children unless the root explicitly delegates orchestration responsibility and spare slots exist.
- Reuse existing findings and paths. Do not dispatch multiple agents to answer the same question.

## Route the task

Classify the request before spawning any child. Read [task classification](references/task-classification.md) when the task size or appropriate topology is not obvious.

- Small, exact-location work: keep it single-agent.
- Medium work: use one explorer, then one worker; add a reviewer only when risk warrants it.
- Large or cross-module work: use up to two complementary explorers, synthesize a task DAG, then dispatch workers in conflict-free waves and finish with a reviewer.
- Extra-large, migration, data-loss, security, or compatibility-sensitive work: start with evidence gathering and an explicit risk-aware implementation plan. Continue implementation only when already authorized by the user's request.

Respect the live collaboration limit. In a four-slot environment, keep the root plus at most three children active. Prefer fewer high-value agents over filling every slot.

## Execute the workflow

1. Restate the concrete outcome, constraints, acceptance criteria, and authorization boundary.
2. Inspect enough repository context to avoid blind delegation. Use existing code-index results when available.
3. Assign complementary discovery questions with read-only contracts.
4. Wait for discovery results, reconcile contradictions, and form one root-owned implementation plan.
5. Create a file-ownership map. Keep related Java, Mapper XML, DTO, and migration changes with one worker when splitting them would create coordination risk.
6. Dispatch editing workers in conflict-free waves using the contracts in [task contracts](references/task-contracts.md).
7. Inspect the combined changes before review. Resolve overlap centrally; never discard unknown edits.
8. Assign a read-only reviewer for high-risk or multi-worker changes. Route concrete findings back to the owning worker.
9. Close review after at most two targeted rework rounds, or let the root arbitrate and report any residual risk.
10. Perform only the validation authorized by the user and repository instructions. Deliver the outcome, changed files, validation status, and remaining risks.

Read [workflow and recovery](references/workflow-and-recovery.md) for multi-wave implementation, conflicts, incomplete agents, or reviewer rework. Read [Java repository rules](references/java-project-rules.md) for call-chain discovery, Spring/JeecgBoot/MyBatis boundaries, transactions, and data changes.

## Model routing

Do not override an agent model or reasoning effort unless the user explicitly requested that assignment and the current surface supports it. Otherwise inherit the configured model.

When the user explicitly authorizes Sol/Terra/Luna routing, read [model routing](references/model-routing.md). Treat the mapping as a workload heuristic, not a quality guarantee.

## Evaluation

For a substantial revision of this skill, use [evaluation cases](references/evaluation-cases.md) to check routing, ownership, evidence, review closure, and restraint. Do not run repository builds or tests merely to evaluate the skill when active instructions prohibit them.
