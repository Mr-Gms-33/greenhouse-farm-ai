# Rollback runbook

## Goal

Restore the previous known-good application image without changing financial source records.

## Preconditions

- Production promotions use immutable image tags equal to git SHAs.
- Database migrations remain backward-compatible with the previous image, or a forward-fix migration is prepared first.

## Steps

1. Identify the last healthy production SHA from the deployment history or GitHub Actions.
2. Run **Promote to production** with that SHA (`workflow_dispatch`).
3. Verify `/health` and `/ready` on the public URL.
4. Sign in as seeded Owner and generate a financial analysis (or confirm summary-only mode if remediating an analysis outage).
5. Confirm Grafana still shows correlated journey signals.
6. Record the rollback in the incident issue with before/after SHAs.

## Database policy

- Prefer additive, expandable/contractable migrations.
- Never deploy a migration that the previous image cannot read.
- Soft-deleted business records are never physically removed in MVP.
