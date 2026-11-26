# Optional Sol, Terra, and Luna routing

Read this file only when the user explicitly authorizes model assignment or asks for a Sol/Terra/Luna multi-agent workflow. Preserve any exact model or reasoning choices in the request.

## Workload heuristic

| Role or task shape | Suggested tier |
| --- | --- |
| Read-only file discovery, bounded call-chain tracing, configuration lookup, mechanical evidence collection | Luna |
| Ordinary Java implementation, scoped bug fixes, DTO/Service/Mapper work, routine review | Terra |
| Root orchestration for high-risk work, architecture, difficult debugging, security/transaction reasoning, final arbitration | Sol |

Start with the configured reasoning effort. Use `high` across tiers only when the user requested it. Otherwise inherit the parent configuration or choose a balanced supported effort. Treat model names as optional routing metadata; if the collaboration surface cannot honor per-child models, continue with inherited models and preserve the same role boundaries.

## Escalation

Escalate work from Luna to Terra when it requires implementation judgment, ambiguous framework behavior, or reconciliation of conflicting evidence. Escalate from Terra to Sol when the decision is high-impact, cross-module, security-sensitive, transaction-sensitive, or repeatedly unresolved.

Do not escalate merely because a task is long. First narrow the question, reduce context, and give the agent a clearer contract.

## Budget discipline

- Use no agent for trivial work.
- Use one explorer when one question determines the plan.
- Add a second explorer only for a genuinely independent evidence lane.
- Avoid sending the full conversation and repository overview when a smaller contract is sufficient.
- Stop an agent after its bounded deliverable is complete.
- Compare quality, latency, and usage on representative tasks before hard-coding model or effort defaults.
