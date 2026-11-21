# Deployment

## Public URLs (Render)

| Service | URL |
|---|---|
| Web | https://agri-web-uff8.onrender.com |
| API | https://agri-api-j045.onrender.com |
| Login | https://agri-web-uff8.onrender.com/login |
| Health | https://agri-api-j045.onrender.com/health |
| Ready | https://agri-api-j045.onrender.com/ready |
| OpenAPI | https://agri-api-j045.onrender.com/docs |

Demo login (seeded):

| Email | Password | Role |
|---|---|---|
| manager@farm.ma | Manager123! | Farm Manager |
| owner@farm.ma | Owner123! | Owner |
| accountant@farm.ma | Accountant123! | Accountant |

## Environments

| Environment | Trigger | Notes |
|---|---|---|
| Local | `docker compose up --build` | Full stack including observability |
| Development | Push/merge to `main` | CI deploy job + optional Render hook |
| Production | Manual workflow approval | Same immutable git SHA/image tag |
| Public demo | Render free web + API + Postgres | Live URLs above |

## Render services

- `agri-web` — Docker build from `apps/alfilaha` (AlFilaha Pro static SPA)
- `agri-api` — Docker build from `services/api`
- `agri-db` — Render managed PostgreSQL

Required API env on Render:

- `DATABASE_URL` — use `postgresql+psycopg://...` (psycopg driver)
- `SECRET_KEY`
- `CORS_ORIGINS=https://agri-web-uff8.onrender.com`
- `SEED_DEMO=true`

Web login (AlFilaha SPA): `manager@farm.ma` / `Manager123!`

Blueprint reference: [render.yaml](../render.yaml).

## Secrets

Configure GitHub Actions secrets:

- `RENDER_DEPLOY_HOOK_DEV`
- `RENDER_DEPLOY_HOOK_PROD`

Never commit `.env` or API keys.

## Health checks

- `GET /health`
- `GET /ready`
- Web `/login` returns the SPA
- Grafana and Prometheus reachable locally for telemetry evidence

## Rollback

Use the previous known-good SHA with the promote workflow. See
[runbooks/rollback.md](runbooks/rollback.md).
