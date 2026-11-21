# Submission evidence map

| Rubric / AC | Evidence |
|---|---|
| Problem description | [README.md](../README.md), [product-spec.md](product-spec.md) |
| Product specification + public tracker | [product-spec.md](product-spec.md), [milestone](https://github.com/Mr-Gms-33/greenhouse-farm-ai/milestone/1) |
| Agent team | [AGENTS.md](../AGENTS.md), [team/](../team/), [process.md](process.md) |
| Context management | [AGENTS.md](../AGENTS.md) links modular docs |
| Full-stack app | `apps/alfilaha` (AlFilaha Pro UI) + `services/api` + PostgreSQL (Compose/Render) |
| Tests | API pytest 16 passed; web Vitest; CI green on `main` |
| Containerization | `docker compose up --build` verified (web/api/db/responder healthy) |
| Deployment | **Public Render deployment** (see URLs below) |
| CI/CD | [.github/workflows/ci.yml](../.github/workflows/ci.yml) (green), [promote-production.yml](../.github/workflows/promote-production.yml) |
| Observability | `infra/observability`, `/metrics`, Grafana dashboard JSON |
| Alerting | `infra/observability/alerts.yml`, Alertmanager → responder |
| On-call agent | Demo drill returned `recovered=true` via `/demo/trigger` |

## Public deployment (2026-11-16)

| Service | Public URL |
|---|---|
| Web UI | https://agri-web-uff8.onrender.com |
| API | https://agri-api-j045.onrender.com |
| API health | https://agri-api-j045.onrender.com/health |
| API ready | https://agri-api-j045.onrender.com/ready |
| API docs | https://agri-api-j045.onrender.com/docs |
| Login | https://agri-web-uff8.onrender.com/login |

### Verified on Render

- `GET /health` → `{"status":"ok"}`
- `GET /ready` → `{"status":"ready"}`
- Farm manager login: `manager@farm.ma` / `Manager123!` → Dashboard loads
- Web build uses `VITE_API_URL=https://agri-api-j045.onrender.com/api/v1`
- Managed Postgres: Render service `agri-db` (free tier)
- GitHub repo: https://github.com/Mr-Gms-33/greenhouse-farm-ai

## Local verification recorded (2026-11-15)

- `GET /health` and `/ready` ok
- Owner login, dashboard, and financial analysis (9 months, validated forecast) succeeded
- Responder demo trigger recovered
- Web UI http://localhost:3000 returned HTTP 200
- GitHub Actions CI on merged PR #17 / #18 succeeded
- MVP tracker issues #2–#15 closed; #16 remains post-MVP
