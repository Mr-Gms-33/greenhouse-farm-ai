# Greenhouse Farm Management Platform

A bilingual English/Arabic full-stack application for a greenhouse farm in
Agadir, Morocco. The focused MVP connects greenhouses, crop cycles, and harvests
to sales, expenses, profitability, and traceable AI-assisted financial
forecasting.

## Current status

The approved product specification and public delivery process are complete.
Application implementation has not started.

## Documentation

- [Approved product specification](docs/product-spec.md)
- [Delivery process](docs/process.md)
- [Backlog order and acceptance coverage](docs/backlog.md)
- [Agent instructions](AGENTS.md)
- [Task template](docs/task-template.md)

## Agent team

- [Orchestrator](team/orchestrator.md)
- [Product Manager](team/product-manager.md)
- [Software Engineer](team/software-engineer.md)
- [QA Engineer](team/qa-engineer.md)

## Planned stack

- React and TypeScript frontend
- FastAPI and Python backend
- PostgreSQL database
- Docker Compose local environment

## Command contract

The repository scaffold issue will implement:

```powershell
docker compose up --build
docker compose run --rm test
docker compose down
```

These commands are a delivery contract and are not claimed to work before the
scaffold issue is closed.

## Public delivery

Implementation is managed through the
[public issues](https://github.com/Mr-Gms-33/greenhouse-farm-ai/issues) and
[MVP v1 milestone](https://github.com/Mr-Gms-33/greenhouse-farm-ai/milestone/1).
Each issue is groomed by the Product Manager, implemented by the Software
Engineer, independently checked by QA, and closed by the Orchestrator only after
evidence-backed PASS.

## License

No license has been selected yet. All rights are reserved unless a license is
added explicitly.
