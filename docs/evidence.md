# Submission evidence map

| Rubric / AC | Evidence |
|---|---|
| Problem description | [README.md](../README.md), [product-spec.md](product-spec.md) |
| Product specification + public tracker | [product-spec.md](product-spec.md), [milestone](https://github.com/Mr-Gms-33/greenhouse-farm-ai/milestone/1) |
| Agent team | [AGENTS.md](../AGENTS.md), [team/](../team/), [process.md](process.md) |
| Context management | [AGENTS.md](../AGENTS.md) links modular docs |
| Full-stack app | `apps/web`, `services/api`, PostgreSQL via `compose.yaml` |
| Tests | API pytest 16 passed; web Vitest 4 passed; CI green on main |
| Containerization | `docker compose up --build` verified locally (web/api/db/responder healthy) |
| Deployment | [deployment.md](deployment.md); configure `RENDER_DEPLOY_HOOK_*` for public URL |
| CI/CD | `.github/workflows/ci.yml` (green), `promote-production.yml` |
| Observability | `infra/observability`, `/metrics`, Grafana dashboard JSON |
| Alerting | `alerts.yml`, Alertmanager → responder |
| On-call agent | Demo drill returned `recovered: true` via `/demo/trigger` |

## Local verification recorded (2026-11-15)

- `GET /health` and `/ready` → ok
- Owner login + dashboard + financial analysis (9 months, validated forecast) succeeded
- Responder demo trigger recovered summary-only path
- Web UI `http://localhost:3000` → HTTP 200
- GitHub Actions CI on merged PR #17 → success
