---
name: Defect
about: Report behavior that contradicts an accepted requirement
title: "bug: "
labels: "type:bug,status:needs-triage"
assignees: ""
---

## Observed behavior

Describe what happened without including protected farm, customer, credential,
or financial data.

## Expected behavior

Link the specification criterion or previously accepted issue.

## Reproduction

1. Provide the smallest reproducible sequence.
2. Include role and locale when relevant.
3. Include environment and commit/deployment version.

## Evidence

- Trace ID or sanitized logs:
- Screenshot/video:
- Test failure:

## Impact

Describe the affected user journey and severity.

## Acceptance criteria

- [ ] The reproduction no longer fails.
- [ ] A regression test proves the fix.
- [ ] Related English/Arabic and authorization behavior remains correct.

## Out of scope

- List unrelated observations and link follow-up issues.

## Constraints

- Do not expose secrets or protected data.
- Preserve rollback compatibility.
