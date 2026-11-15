# Submission evidence map

| Rubric / AC | Evidence |
|---|---|
| Problem description | [README.md](../README.md), [product-spec.md](product-spec.md) |
| Product specification + public tracker | [product-spec.md](product-spec.md), [milestone](https://github.com/Mr-Gms-33/greenhouse-farm-ai/milestone/1) |
| Agent team | [AGENTS.md](../AGENTS.md), [team/](../team/), [process.md](process.md) |
| Context management | [AGENTS.md](../AGENTS.md) links modular docs |
| Full-stack app | `apps/web`, `services/api`, PostgreSQL via `compose.yaml` |
| Tests | `services/api/tests` (16 passed), `apps/web` Vitest (4 passed), `docker compose run --rm test` |
| Containerization | `compose.yaml`, Dockerfiles |
| Deployment | [deployment.md](deployment.md), CI deploy jobs |
| CI/CD | `.github/workflows/ci.yml`, `promote-production.yml` |
| Observability | `infra/observability`, `/metrics`, Grafana dashboard |
| Alerting | `alerts.yml`, Alertmanager → responder |
| On-call agent | `services/responder`, [analysis-alert.md](runbooks/analysis-alert.md) |

## Local verification recorded

- API: `pytest` → 16 passed
- Web: `vitest` → 4 passed; `npm run build` succeeded
- Docker daemon was unavailable during the first packaging pass; Compose files and Dockerfiles are present for single-command startup once Docker Desktop is running
