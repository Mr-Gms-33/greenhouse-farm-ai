from conftest import seed_monthly_finance
from sqlalchemy import select

from app.models import CropCycle, Customer


def test_ac018_insufficient_data(client, db, headers_owner):
    cycle = db.scalar(select(CropCycle))
    customer = db.scalar(select(Customer))
    seed_monthly_finance(db, cycle.id, customer.id, months=5)
    headers = headers_owner
    r = client.post("/api/v1/analyses", json={"end_month": "2026-05"}, headers=headers)
    assert r.status_code == 201
    body = r.json()
    assert body["forecast"]["status"] == "insufficient_data"
    assert "points" not in body["forecast"] or not body["forecast"].get("points")


def test_ac020_validation_window_and_mae(client, db, headers_accountant):
    cycle = db.scalar(select(CropCycle))
    customer = db.scalar(select(Customer))
    seed_monthly_finance(db, cycle.id, customer.id, months=8)
    headers = headers_accountant
    r = client.post("/api/v1/analyses", json={"end_month": "2026-08"}, headers=headers)
    assert r.status_code == 201
    body = r.json()
    assert body["forecast"]["status"] == "ok"
    assert body["forecast"]["validation"]["training_months_excluded_validation"] is True
    assert body["forecast"]["validation"]["mae_revenue"] is not None
    assert len(body["forecast"]["points"]) == 3


def test_ac024_fallback_narrative_on_demo_fail(client, db, headers_owner):
    cycle = db.scalar(select(CropCycle))
    customer = db.scalar(select(Customer))
    seed_monthly_finance(db, cycle.id, customer.id, months=6)
    owner_headers = headers_owner
    demo = client.post("/api/v1/analyses/demo-fail", headers=owner_headers)
    assert demo.status_code == 200
    r = client.post("/api/v1/analyses", json={"end_month": "2026-06"}, headers=owner_headers)
    assert r.status_code == 201
    body = r.json()
    assert "Fallback narrative" in body["narrative_en"]
    assert body["facts"]["totals"]["revenue"] is not None
