# Delivery Process

## Purpose

This process makes the public GitHub tracker the durable source of delivery
state. Chat history is not evidence. Issues, pull requests, commits, checks, and
QA comments are evidence.

## Sources of truth

In conflict order:

1. Approved [`product-spec.md`](product-spec.md).
2. Current groomed GitHub issue.
3. Architecture decision records and component documentation.
4. Implementation and tests.
5. Chat or agent memory.

If two higher-priority sources conflict, stop implementation and ask the Product
Manager and Owner to resolve the conflict publicly.

## Tracker structure

- One MVP milestone contains the ordered implementation issues.
- Labels identify `type`, `area`, `priority`, and `status`.
- [`backlog.md`](backlog.md) maps issue order and specification acceptance
  criteria.
- An issue is blocked until all listed dependencies are closed.
- Follow-up work receives its own issue; scope is never silently dropped.

## Required issue shape

Every implementation issue must contain:

```markdown
## Goal

The user or system outcome.

## Acceptance criteria

- [ ] Observable, binary result with a test or inspection method.

## Out of scope

- Explicit exclusions, linking follow-up issues where applicable.

## Constraints

- Specification IDs, dependencies, files/components, security and quality rules.
```

The reusable template is in [`task-template.md`](task-template.md).

## Role handoffs

### 1. Orchestrator selects

- Pick the lowest ordered unblocked issue.
- Confirm its dependencies are closed and no other engineer owns it.
- Assign the Product Manager to groom it.

### 2. Product Manager grooms

- Re-read the approved specification.
- Make each criterion independently verifiable.
- Cover relevant empty, invalid, unauthorized, duplicate, boundary, Arabic/RTL,
  persistence, and failure states.
- Move unrelated work to a linked follow-up issue.
- Post `## PM: READY` with a short summary and the specification IDs covered.

Implementation cannot begin without `## PM: READY`.

### 3. Software Engineer implements

- Branch from updated `main` as `<issue-number>-<short-slug>`.
- Implement only the groomed issue.
- Add or update tests and documentation.
- Run the relevant checks and retain concise results.
- Open a pull request using the repository template and link it with
  `Closes #<issue-number>`.
- Post `## Engineer: READY FOR QA` on the issue with PR, commit, and test links.

The engineer does not close the issue or self-declare QA PASS.

### 4. QA verifies

- Fetch the current issue and PR; do not rely on earlier copies.
- Verify every acceptance criterion against running behavior, code where
  relevant, and test output.
- Run the repository command plus focused checks needed to prove the scope.
- Check authorization, failure states, persistence, and English/Arabic behavior
  whenever relevant.
- Do not fix defects.
- Post one checklist verdict:

```markdown
## QA: PASS

- [x] Criterion text — PASS: evidence

Tests: `command` — result
Commit: `<sha>`
```

or:

```markdown
## QA: FAIL

- [ ] Criterion text — FAIL: reproduction and observed result

Tests: `command` — result
Commit: `<sha>`
```

Any failed criterion means the complete verdict is FAIL.

### 5. Orchestrator closes

- On FAIL, return the unchanged issue to Engineering with the QA comment.
- On PASS, confirm required checks are green and the verified commit is still the
  PR head.
- Merge according to repository protection rules.
- Re-fetch the issue and QA comment.
- Close with links to the merged PR, QA PASS, and relevant checks.

## Pull request rules

- One issue per pull request unless a dependency makes separation impossible and
  the issue documents why.
- Keep the diff inside the issue constraints.
- Use small commits that explain why.
- Do not merge with unresolved QA findings or failing required checks.
- A behavioral scope change requires specification and issue updates before code.
- Database changes must be backward-compatible with the documented rollback
  strategy.

## Branch rules

- `main` is the deployable integration branch.
- Feature branches start from current `main`, not from another open feature
  branch.
- Branch names use `<issue-number>-<short-slug>`.
- Delete merged feature branches.
- Do not force-push `main`.

## Evidence rules

Every closed implementation issue must expose:

- PM READY comment.
- Linked branch/PR and implementation summary.
- Test/check results for the verified commit.
- QA verdict covering each current criterion.
- Orchestrator closure comment linking the merged evidence.

Screenshots and videos can supplement evidence but cannot replace automated tests
for deterministic behavior.

## Defects and incidents

- A defect discovered before merge is reported in the active issue/PR.
- A regression found after merge gets a new bug issue linked to the originating
  issue.
- Production incidents use the incident template and link telemetry evidence,
  mitigation, root cause, and follow-up work.
- Never paste secrets or protected financial/customer data into public issues.

## Initial documentation phase

Before application code exists, documentation work may be committed directly as
the repository baseline. The first public process issue records the files,
review evidence, and acceptance audit. All subsequent application work follows
the full branch/PR lifecycle above.
