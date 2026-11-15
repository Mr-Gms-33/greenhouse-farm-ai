from sqlalchemy import select

from app.models import CropCycle, Greenhouse


def test_ac005_manager_blocked_from_finance_endpoints(client, headers_manager):
    headers = headers_manager
    assert client.get("/api/v1/reports/summary", params={"date_from": "2026-01-01", "date_to": "2026-01-31"}, headers=headers).status_code == 403
    assert client.get("/api/v1/sales", headers=headers).status_code == 403
    assert client.get("/api/v1/expenses", headers=headers).status_code == 403
    assert client.post("/api/v1/analyses", json={"end_month": "2026-06"}, headers=headers).status_code == 403


def test_ac006_accountant_blocked_from_operations_write(client, db, headers_accountant):
    headers = headers_accountant
    greenhouse = db.scalar(select(Greenhouse))
    cycle = db.scalar(select(CropCycle))
    gh_payload = {"name": "GH-NEW", "area_m2": "200", "status": "active"}
    assert client.post("/api/v1/greenhouses", json=gh_payload, headers=headers).status_code == 403
    cycle_payload = {
        "greenhouse_id": greenhouse.id,
        "crop": "tomato",
        "planting_date": "2026-02-01",
        "status": "active",
    }
    assert client.post("/api/v1/crop-cycles", json=cycle_payload, headers=headers).status_code == 403
    harvest_payload = {"crop_cycle_id": cycle.id, "harvest_date": "2026-02-10", "quantity_kg": "10"}
    assert client.post("/api/v1/harvests", json=harvest_payload, headers=headers).status_code == 403
