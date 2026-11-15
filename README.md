# Greenhouse Farm Management Platform

Bilingual English/Arabic full-stack MVP for a greenhouse farm in Agadir,
Morocco. The application connects greenhouses, crop cycles, and harvests to
sales, expenses, deterministic profitability, and traceable AI-assisted
financial forecasting.

## Status

Roadmap phases 1–11 are implemented in this repository:

1. Approved product specification
2. Public delivery process and tracker
3. Domain and API design
4. Vertical application slices (auth, ops, finance, dashboards, i18n)
5. Traceable AI financial analysis
6. Automated tests
7. Docker Compose local system
8. Correlated observability
9. User-impact alert and bounded responder
10. CI/CD with manual production promotion and rollback runbook
11. Submission packaging (this README and docs)

## Quick start

```powershell
copy .env.example .env
docker compose up --build
```

- Web: http://localhost:3000
- API docs: http://localhost:8000/docs
- Grafana: http://localhost:3001 (anonymous viewer)
- Prometheus: http://localhost:9090
- Responder health: http://localhost:8089/health

### Demo users

| Email | Password | Role |
|---|---|---|
| owner@farm.ma | Owner123! | Owner |
| manager@farm.ma | Manager123! | Farm Manager |
| accountant@farm.ma | Accountant123! | Accountant |

## Tests

```powershell
docker compose run --rm test
```

Locally without Compose:

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m pytest -q

cd ..\..\apps\web
npm install
npm test -- --run
npm run build
```

## Architecture

See [docs/architecture.md](docs/architecture.md) and [docs/api.md](docs/api.md).

- `apps/web` — React + TypeScript + i18next (EN/AR, LTR/RTL)
- `services/api` — FastAPI + PostgreSQL + Decimal finance + forecast engine
- `services/responder` — allowlisted alert remediation agent
- `infra/observability` — OTel, Prometheus, Alertmanager, Loki, Tempo, Grafana

## AI financial analysis

Authoritative totals are never calculated by a language model. The API uses
Decimal arithmetic for facts and an interpretable chronological time-trend
regression for a three-month forecast. Narratives are deterministic English and
Arabic templates grounded only in structured results.

## Observability and on-call

Key journey: `generate traceable financial analysis successfully`.

Demo alert drill:

```powershell
curl -X POST http://localhost:8089/demo/trigger -H "X-Webhook-Secret: dev-responder-secret"
```

See [docs/runbooks/analysis-alert.md](docs/runbooks/analysis-alert.md).

## CI/CD and rollback

- Pull requests and `main` pushes run [.github/workflows/ci.yml](.github/workflows/ci.yml)
- Merge to `main` triggers the development deploy job (configure `RENDER_DEPLOY_HOOK_DEV`)
- Production promotion is manual via [Promote to production](.github/workflows/promote-production.yml)
- Rollback: [docs/runbooks/rollback.md](docs/runbooks/rollback.md)

## Public tracker

- Repository: https://github.com/Mr-Gms-33/greenhouse-farm-ai
- Milestone: https://github.com/Mr-Gms-33/greenhouse-farm-ai/milestone/1
- Process: [docs/process.md](docs/process.md)
- Agents: [AGENTS.md](AGENTS.md)

## Specification

[docs/product-spec.md](docs/product-spec.md) is the release contract (AC-001–AC-036).
