# Deployment

## Environments

| Environment | Trigger | Notes |
|---|---|---|
| Local | `docker compose up --build` | Full stack including observability |
| Development | Push/merge to `main` | CI deploy job + optional Render hook |
| Production | Manual workflow approval | Same immutable git SHA/image tag |

## Secrets

Configure GitHub Actions secrets:

- `RENDER_DEPLOY_HOOK_DEV`
- `RENDER_DEPLOY_HOOK_PROD`
- Production `SECRET_KEY`, database URL, and ops/responder secrets in the host platform

Never commit `.env`.

## Health checks

- `GET /health`
- `GET /ready`
- Web root returns the SPA
- Grafana and Prometheus reachable for telemetry evidence

## Rollback

Use the previous known-good SHA with the promote workflow. See
[runbooks/rollback.md](runbooks/rollback.md).
