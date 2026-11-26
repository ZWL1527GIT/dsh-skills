# Subagent task contracts

Every delegation must be concrete, bounded, and independently useful. Include only the context needed for that assignment.

## Explorer contract

```text
Role: read-only Java explorer
Objective: <one specific codebase question>
Scope: <module, package, symbols, or paths>
Do not: edit files, run mutating commands, or investigate unrelated areas
Required evidence: file paths, symbols, relevant line numbers, and call relationships
Return:
1. Conclusion
2. Evidence
3. Call chain or data flow
4. Affected modules/files
5. Uncertainties and risks
6. Suggested worker boundary
```

Use separate explorers only for complementary questions. Never ask two agents to perform the same broad repository scan.

## Worker contract

```text
Role: Java implementation worker
Objective: <one implementation outcome>
Ownership: <exclusive files, package, or module>
Inputs: <root-approved findings and decisions>
Acceptance criteria: <observable behavior and compatibility requirements>
Forbidden scope: <files/modules/actions outside ownership>
Validation authorization: <what may be run, if anything>

You are not alone in the repository. Preserve user and peer edits, do not revert
unknown changes, and stop to report if required work crosses your ownership.

Return:
1. Files changed
2. Behavior implemented
3. Important decisions
4. Validation performed or explicitly not performed
5. Risks, assumptions, and needed follow-up
```

Assign tightly coupled Java interfaces, implementations, mapper declarations, mapper XML, DTO conversions, and migration pieces to one owner unless a stable contract cleanly separates them.

## Reviewer contract

```text
Role: read-only reviewer
Objective: find actionable correctness, compatibility, security, persistence, and regression issues
Scope: <combined diff or specified files>
Do not: edit files or restate style preferences as defects
Required format for every finding:
- Priority: P0, P1, P2, or P3
- File and tight line location
- Concrete failure mode or triggering scenario
- Why the current code is wrong or risky
- Specific remediation

Return "No actionable findings" when appropriate.
```

Review priorities:

- P0: data loss, severe security issue, or unusable system.
- P1: likely production failure, broken contract, or serious regression.
- P2: ordinary correctness or maintainability defect worth fixing now.
- P3: optional improvement that should not block delivery.

## Specialist contract

Use a specialist only for a narrow high-risk question such as transaction boundaries, concurrency, SQL/indexing, security, or API compatibility. Keep the specialist read-only unless exclusive implementation ownership is explicitly assigned.
