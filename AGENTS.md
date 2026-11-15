# AGENTS.md

## Project

This repository builds a bilingual English/Arabic greenhouse management MVP for
a farm in Agadir, Morocco. The approved scope connects greenhouse crop and
harvest records to sales, expenses, deterministic financial reports, and
traceable AI financial forecasting.

The authoritative product requirements are in
[`docs/product-spec.md`](docs/product-spec.md). Do not implement behavior that
contradicts that specification. If a requirement must change, update the
specification and the public tracker issue before changing application code.

## Required reading

Read these documents before working on an issue:

1. [`docs/product-spec.md`](docs/product-spec.md) — approved behavior and
   acceptance criteria.
2. [`docs/process.md`](docs/process.md) — issue, branch, review, QA, and closure
   workflow.
3. [`docs/backlog.md`](docs/backlog.md) — dependency order and acceptance-criteria
   coverage.
4. The role instruction matching your assignment:
   - [`team/orchestrator.md`](team/orchestrator.md)
   - [`team/product-manager.md`](team/product-manager.md)
   - [`team/software-engineer.md`](team/software-engineer.md)
   - [`team/qa-engineer.md`](team/qa-engineer.md)

## Scope rules

- Work on one public GitHub issue at a time.
- The issue must contain Goal, Acceptance criteria, Out of scope, and
  Constraints before implementation starts.
- Treat every acceptance criterion as a release contract.
- Do not add the out-of-scope capabilities listed in the product specification.
- Backend authorization is mandatory; hidden frontend controls are not access
  control.
- Financial arithmetic uses decimal values and the rounding rules in the
  specification. A language model must never calculate authoritative totals.
- Store domain values language-neutrally. English is LTR and Arabic is RTL.
- Never put credentials, tokens, customer details, notes, references,
  transaction amounts, or model inputs in telemetry.
- Do not commit secrets, generated dependencies, local databases, or build
  output.

## Stable command contract

The scaffold issue must make these repository-level commands work. Until that
issue is closed, agents must state which commands are not yet available rather
than claiming successful verification.

```powershell
# Start the complete local system
docker compose up --build

# Run all required checks and tests
docker compose run --rm test

# Stop the system
docker compose down

# Stop and remove local persisted demo data
docker compose down --volumes
```

Component-level commands will be documented beside each component after the
scaffold issue creates it. The repository-level commands above remain the
authoritative fresh-clone interface.

## Issue lifecycle

1. Orchestrator selects the first unblocked issue in the documented order.
2. Product Manager grooms it and posts `## PM: READY`.
3. Software Engineer creates a branch from current `main`, implements only that
   issue, runs relevant checks, opens a pull request, and comments
   `## Engineer: READY FOR QA`.
4. QA fetches the current issue and PR, verifies every criterion, and comments
   `## QA: PASS` or `## QA: FAIL`.
5. A failure returns to Engineering without changing the acceptance criteria.
6. On QA PASS and green required checks, the Orchestrator merges the PR and
   closes the issue with evidence links.

Only the Orchestrator closes issues. QA never fixes code. Engineers never weaken
acceptance criteria to match an implementation.

## Definition of done for an issue

- Every issue acceptance criterion has direct evidence.
- New behavior has tests at the appropriate layer.
- Relevant repository-level and component checks pass.
- English and Arabic behavior is covered where the issue affects UI.
- Documentation and migrations are updated where required.
- The PR links the issue and contains no unrelated changes.
- QA has posted PASS against the current issue body.
- The working tree is clean after verification.
