"""Bounded on-call responder: observe -> decide -> act on allowlisted runbooks only."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("responder")

API_INTERNAL_URL = os.getenv("API_INTERNAL_URL", "http://api:8000").rstrip("/")
OPS_TOKEN = os.getenv("OPS_TOKEN", "dev-ops-token")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "dev-responder-secret")

ALLOWLIST = {
    "FinancialAnalysisJourneyFailing": "enable_summary_only",
    "FinancialAnalysisHighLatency": "enable_summary_only",
}

app = FastAPI(title="Greenhouse Farm Responder", version="1.0.0")


class Alert(BaseModel):
    status: str = "firing"
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)


class AlertmanagerPayload(BaseModel):
    status: str = "firing"
    alerts: list[Alert] = Field(default_factory=list)
    commonLabels: dict[str, str] = Field(default_factory=dict)


class IncidentRecord(BaseModel):
    alert_name: str
    action: str
    evidence: dict[str, Any]
    recovered: bool
    at: str


incidents: list[IncidentRecord] = []


def _auth_headers() -> dict[str, str]:
    return {"X-Ops-Token": OPS_TOKEN, "Content-Type": "application/json"}


def enable_summary_only() -> dict[str, Any]:
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            f"{API_INTERNAL_URL}/api/v1/ops/summary-only",
            headers=_auth_headers(),
            json={"enabled": True},
        )
        response.raise_for_status()
        return response.json()


def clear_force_failure() -> dict[str, Any]:
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            f"{API_INTERNAL_URL}/api/v1/ops/force-failure",
            headers=_auth_headers(),
            json={"enabled": False},
        )
        response.raise_for_status()
        return response.json()


def verify_journey() -> dict[str, Any]:
    with httpx.Client(timeout=15.0) as client:
        response = client.get(
            f"{API_INTERNAL_URL}/api/v1/ops/journey-health",
            headers=_auth_headers(),
        )
        response.raise_for_status()
        return response.json()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/incidents")
def list_incidents() -> list[IncidentRecord]:
    return incidents


@app.post("/webhook")
def webhook(
    payload: AlertmanagerPayload,
    x_webhook_secret: str | None = Header(default=None),
) -> dict[str, Any]:
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="invalid webhook secret")

    results = []
    for alert in payload.alerts:
        alert_name = alert.labels.get("alertname") or payload.commonLabels.get("alertname", "unknown")
        runbook = ALLOWLIST.get(alert_name)
        evidence = {
            "alert_name": alert_name,
            "status": alert.status,
            "annotations_keys": sorted(alert.annotations.keys()),
        }
        if not runbook:
            logger.info('{"event":"ignored_alert","alert":"%s"}', alert_name)
            results.append({"alert": alert_name, "action": "ignored"})
            continue

        actions = []
        recovered = False
        try:
            if runbook == "enable_summary_only":
                clear_force_failure()
                actions.append("clear_force_failure")
                enable_summary_only()
                actions.append("enable_summary_only")
                health = verify_journey()
                actions.append("verify_journey")
                recovered = bool(health.get("ok"))
                evidence["journey"] = {"ok": recovered, "mode": health.get("mode")}
            record = IncidentRecord(
                alert_name=alert_name,
                action=runbook,
                evidence=evidence,
                recovered=recovered,
                at=datetime.now(timezone.utc).isoformat(),
            )
            incidents.append(record)
            # Persist via API if available
            try:
                with httpx.Client(timeout=10.0) as client:
                    client.post(
                        f"{API_INTERNAL_URL}/api/v1/incidents",
                        headers=_auth_headers(),
                        json=record.model_dump(),
                    )
            except Exception:
                logger.info('{"event":"incident_persist_skipped"}')
            results.append({"alert": alert_name, "action": runbook, "recovered": recovered})
        except Exception as exc:
            logger.info('{"event":"remediation_failed","alert":"%s","error":"%s"}', alert_name, type(exc).__name__)
            results.append({"alert": alert_name, "action": runbook, "error": type(exc).__name__})

    return {"handled": results}


@app.post("/demo/trigger")
def demo_trigger(x_webhook_secret: str | None = Header(default=None)) -> dict[str, Any]:
    """Safe local drill: simulate firing alert without changing source finance records."""
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="invalid webhook secret")
    with httpx.Client(timeout=10.0) as client:
        client.post(
            f"{API_INTERNAL_URL}/api/v1/ops/force-failure",
            headers=_auth_headers(),
            json={"enabled": True},
        )
    payload = AlertmanagerPayload(
        status="firing",
        alerts=[
            Alert(
                status="firing",
                labels={"alertname": "FinancialAnalysisJourneyFailing"},
                annotations={"summary": "demo failure for responder drill"},
            )
        ],
        commonLabels={"alertname": "FinancialAnalysisJourneyFailing"},
    )
    return webhook(payload, x_webhook_secret)
