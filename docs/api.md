# API Contract

Base path: `/api/v1`
Auth: `Authorization: Bearer <jwt>`
Errors: `{ "detail": string | object, "code"?: string }`
Idempotency: `Idempotency-Key` header on sale/expense create.

## Health

- `GET /health` — liveness
- `GET /ready` — readiness (database)

## Auth

- `POST /auth/login` `{ email, password }` → `{ access_token, token_type, user }`
- `POST /auth/logout`
- `GET /auth/me`
- `GET /users` / `POST /users` / `PATCH /users/{id}` — owner only

## Operations

- `GET|POST /greenhouses`
- `GET|PATCH /greenhouses/{id}`
- `GET|POST /crop-cycles`
- `GET|PATCH /crop-cycles/{id}`
- `GET|POST /harvests`
- `PATCH /harvests/{id}`

## Finance

- `GET|POST /customers`
- `GET|POST /sales` / `PATCH /sales/{id}`
- `GET|POST /expenses` / `PATCH /expenses/{id}`
- `GET /reports/summary?from=&to=`
- `GET /reports/by-month?from=&to=`
- `GET /reports/by-greenhouse?from=&to=`
- `GET /reports/by-crop?from=&to=`

## Analysis

- `POST /analyses` `{ end_month: "YYYY-MM" }`
- `GET /analyses` / `GET /analyses/{id}`
- `POST /analyses/demo-fail` — owner-only demo trigger
- `POST /ops/summary-only` `{ enabled: bool }` — responder remediation

## Dashboard

- `GET /dashboard` — role-filtered payload

## Trace context

Clients may send `traceparent`. API propagates W3C trace context into logs and spans.
