# MVP Backlog Order and Coverage

The public GitHub issues are the live tracker. This document fixes dependency
order and maps the approved product acceptance criteria to implementation work.
Issue numbers and public links are added after tracker creation.

| Order | Work item | Depends on | Product criteria |
|---:|---|---|---|
| 0 | Delivery process baseline | None | Process rubric |
| 1 | Repository and application scaffold | 0 | AC-032 |
| 2 | Authentication and user RBAC | 1 | AC-001–AC-006 |
| 3 | Greenhouses and crop cycles | 2 | AC-007, AC-008, AC-010 |
| 4 | Harvest records | 3 | AC-009, AC-010, AC-012 |
| 5 | Sales, customers, and expenses | 4 | AC-011–AC-013, AC-017 |
| 6 | Deterministic financial reporting | 5 | AC-014–AC-017 |
| 7 | AI financial analysis and forecasting | 6 | AC-018–AC-026 |
| 8 | Role dashboards and English/Arabic UI | 2–7 | AC-027–AC-031 |
| 9 | Complete automated test gates | 2–8 | AC-033 |
| 10 | Containers and one-command local operation | 1–9 | AC-032, AC-033 |
| 11 | Correlated observability and user-impact alert | 7–10 | AC-034 |
| 12 | Responder agent and recovery drill | 11 | AC-035 |
| 13 | CI/CD, production deployment, and rollback | 9–12 | AC-036 |
| 14 | Submission evidence and fresh-clone audit | 1–13 | All ACs |

## Scheduling rules

- Work proceeds in order unless dependencies allow clearly independent work.
- Issues 3–7 are vertical domain slices and remain sequential to protect data
  invariants.
- UI localization is not postponed entirely to item 8: every earlier frontend
  slice must add English and Arabic strings. Item 8 completes cross-role
  dashboards and the full localization audit.
- Tests are written in every issue. Item 9 closes cross-cutting gaps and creates
  the complete single-command gate.
- Publicly documented post-MVP ideas are separate issues and are not added to
  the MVP milestone.

## Traceability rule

Every product acceptance criterion AC-001 through AC-036 must appear in at least
one public issue. A criterion may appear in more than one issue when one issue
implements it and another verifies the complete integrated behavior.
