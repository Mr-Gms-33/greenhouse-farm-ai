# MVP Backlog Order and Coverage

The [public GitHub issues](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues)
and [MVP v1 milestone](https://github.com/Mr-Gms-33/greenhouse-farm-ai/milestone/1)
are the live tracker. This document fixes dependency order and maps the approved
product acceptance criteria to implementation work.

| Order | Work item | Depends on | Product criteria |
|---:|---|---|---|
| 0 | [#1 Delivery process baseline](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/1) | None | Process rubric |
| 1 | [#2 Repository and application scaffold](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/2) | #1 | AC-032 |
| 2 | [#3 Authentication and user RBAC](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/3) | #2 | AC-001–AC-006 |
| 3 | [#4 Greenhouses and crop cycles](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/4) | #3 | AC-007, AC-008, AC-010 |
| 4 | [#5 Harvest records](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/5) | #4 | AC-009, AC-010, AC-012 |
| 5 | [#6 Sales, customers, and expenses](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/6) | #5 | AC-011–AC-013, AC-017 |
| 6 | [#7 Deterministic financial reporting](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/7) | #6 | AC-014–AC-017 |
| 7 | [#8 AI financial analysis and forecasting](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/8) | #7 | AC-018–AC-026 |
| 8 | [#9 Role dashboards and English/Arabic UI](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/9) | #3–#8 | AC-027–AC-031 |
| 9 | [#10 Complete automated test gates](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/10) | #3–#9 | AC-033 |
| 10 | [#11 Containers and one-command local operation](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/11) | #2–#10 | AC-032, AC-033 |
| 11 | [#12 Correlated observability and user-impact alert](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/12) | #8, #11 | AC-034 |
| 12 | [#13 Responder agent and recovery drill](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/13) | #12 | AC-035 |
| 13 | [#14 CI/CD, production deployment, and rollback](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/14) | #10–#13 | AC-036 |
| 14 | [#15 Submission evidence and fresh-clone audit](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/15) | #2–#14 | All ACs |

Deferred capabilities remain visible in the
[#16 post-MVP roadmap](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues/16)
and are intentionally outside the MVP milestone.

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
