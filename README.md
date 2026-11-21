<div align="center">

# Greenhouse Farm AI

**Bilingual farm operations platform**

Full-stack MVP connecting greenhouse operations, finance and traceable AI-assisted forecasting — English and Arabic.

[![Live Web](https://img.shields.io/badge/Live%20Web-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://agri-web-uff8.onrender.com/login)
[![API](https://img.shields.io/badge/API-Docs-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://agri-api-j045.onrender.com/docs)
[![Portfolio](https://img.shields.io/badge/Portfolio-mounir--gmamsi-1b3550?style=for-the-badge&logo=netlify&logoColor=white)](https://mounir-gmamsi.netlify.app/)

</div>

---

## Overview

Greenhouse Farm AI is a bilingual English/Arabic platform for greenhouse operations. It links crop cycles and harvests to sales, expenses, deterministic profitability and interpretable financial forecasting. Authoritative totals are calculated with Decimal arithmetic — not invented by a language model.

**Web:** [agri-web-uff8.onrender.com](https://agri-web-uff8.onrender.com/login) · **API docs:** [agri-api-j045.onrender.com/docs](https://agri-api-j045.onrender.com/docs)

---

## What the product delivers

| Capability | Description |
|------------|-------------|
| Operations | Greenhouses, crop cycles and harvest tracking |
| Finance | Sales, expenses and deterministic profitability |
| Traceable AI analysis | Interpretable forecast plus grounded bilingual narrative |
| Bilingual UX | English and Arabic (RTL) interface |
| Observability | Metrics, traces and alert responder path |
| Delivery | Docker Compose local stack and cloud deploy |

---

## Technology stack

### Backend and data

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

### Frontend and delivery

![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)

### Observability

![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white)
![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-000000?style=flat-square&logo=opentelemetry&logoColor=white)

| Layer | Technologies |
|-------|----------------|
| API | FastAPI, PostgreSQL, Decimal finance engine |
| Web | SPA (AlFilaha), legacy React client retained |
| Platform | Docker Compose, Render, GitHub Actions |
| Observability | Prometheus, Grafana, OpenTelemetry, responder service |

---

## Solution flow

| Step | Stage | Technologies |
|:----:|-------|--------------|
| 1 | Capture farm operations data | Web + API |
| 2 | Persist domain model | PostgreSQL, FastAPI |
| 3 | Compute finance facts | Decimal arithmetic |
| 4 | Produce traceable forecast | Interpretable trend model + templates |
| 5 | Monitor and alert | Observability stack + responder |

```mermaid
flowchart TD
  A[1. Operations and finance inputs] --> B[2. API and database]
  B --> C[3. Deterministic finance totals]
  C --> D[4. Traceable forecast and narrative]
  D --> E[5. Dashboards and alerts]
```

---

## Repository structure

| Path | Purpose |
|------|---------|
| `apps/` | Web clients |
| `services/api` | FastAPI backend |
| `services/responder` | Alert remediation agent |
| `infra/` | Observability stack |
| `docs/` | Architecture, API, runbooks |
| `compose.yaml` | Local full-stack system |

---

## Run locally

```powershell
copy .env.example .env
docker compose up --build
```

- Web: http://localhost:3000  
- API docs: http://localhost:8000/docs  

More detail: [docs/architecture.md](docs/architecture.md) · [docs/deployment.md](docs/deployment.md)

---

## Author

**Mounir Gmamsi**  
[Portfolio](https://mounir-gmamsi.netlify.app/) · [GitHub](https://github.com/Mr-Gms-33) · [LinkedIn](https://www.linkedin.com/in/mounir-gmamsi-1595951b3)
