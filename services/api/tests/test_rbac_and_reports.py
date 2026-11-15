from datetime import date
from decimal import Decimal

from tests.conftest import auth


def test_manager_cannot_read_finance(client):
    headers = auth(client, "manager@farm.ma", "Manager123!")
    res = client.get("/api/v1/reports/summary", params={"date_from": "2026-01-01", "date_to": "2026-12-31"}, headers=headers)
    assert res.status_code == 403


def test_accountant_cannot_create_greenhouse(client):
    headers = auth(client, "accountant@farm.ma", "Accountant123!")
    res = client.post(
        "/api/v1/greenhouses",
        headers=headers,
        json={"name": "X", "area_m2": "100", "status": "active"},
    )
    assert res.status_code == 403


def test_sale_total_and_report(client):
    owner = auth(client, "owner@farm.ma", "Owner123!")
    gh = client.post("/api/v1/greenhouses", headers=owner, json={"name": "GH-A", "area_m2": "500", "status": "active"})
    assert gh.status_code == 201
    cycle = client.post(
        "/api/v1/crop-cycles",
        headers=owner,
        json={
            "greenhouse_id": gh.json()["id"],
            "crop": "tomato",
            "planting_date": "2026-01-01",
            "status": "active",
        },
    )
    assert cycle.status_code == 201
    harvest = client.post(
        "/api/v1/harvests",
        headers=owner,
        json={"crop_cycle_id": cycle.json()["id"], "harvest_date": str(date.today()), "quantity_kg": "100"},
    )
    assert harvest.status_code == 201
    cust = client.post("/api/v1/customers", headers=owner, json={"name": "Buyer"})
    assert cust.status_code == 201
    sale = client.post(
        "/api/v1/sales",
        headers=owner,
        json={
            "sale_date": "2026-02-01",
            "customer_id": cust.json()["id"],
            "crop_cycle_id": cycle.json()["id"],
            "quantity_kg": "10",
            "unit_price_mad": "12.345",
        },
    )
    assert sale.status_code == 201
    assert Decimal(sale.json()["total_mad"]) == Decimal("123.45")
    summary = client.get(
        "/api/v1/reports/summary",
        headers=owner,
        params={"date_from": "2026-01-01", "date_to": "2026-12-31"},
    )
    assert summary.status_code == 200
    assert Decimal(str(summary.json()["revenue"])) == Decimal("123.45")


def test_analysis_insufficient_data(client):
    owner = auth(client, "owner@farm.ma", "Owner123!")
    res = client.post("/api/v1/analyses", headers=owner, json={"end_month": "2026-03"})
    assert res.status_code == 201
    assert res.json()["forecast"]["status"] == "insufficient_data"
