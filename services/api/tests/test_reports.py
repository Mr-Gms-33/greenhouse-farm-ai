from decimal import Decimal

from conftest import seed_monthly_finance
from sqlalchemy import select

from app.models import CropCycle, Customer


def test_money_round_half_up():
    from app.core.money import money

    assert money("1.005") == Decimal("1.01")
    assert money("1.004") == Decimal("1.00")


def test_ac014_ac015_ac016_reports(client, db, headers_owner):
    cycle = db.scalar(select(CropCycle))
    customer = db.scalar(select(Customer))
    seed_monthly_finance(db, cycle.id, customer.id, months=3)
    headers = headers_owner

    summary = client.get("/api/v1/reports/summary", params={"date_from": "2026-01-01", "date_to": "2026-03-31"}, headers=headers)
    assert summary.status_code == 200
    body = summary.json()
    assert Decimal(str(body["revenue"])) == Decimal("1530.00")
    assert Decimal(str(body["expenses"])) == Decimal("630.00")
    assert Decimal(str(body["profit"])) == Decimal("900.00")
    assert Decimal(str(body["margin_percent"])) == Decimal("58.82")

    by_gh = client.get("/api/v1/reports/by-greenhouse", params={"date_from": "2026-01-01", "date_to": "2026-03-31"}, headers=headers).json()
    assert Decimal(str(by_gh[0]["scoped_expenses"])) == Decimal("0.00")

    # Margin N/A when no revenue.
    no_rev = client.get("/api/v1/reports/summary", params={"date_from": "2027-01-01", "date_to": "2027-01-31"}, headers=headers).json()
    assert Decimal(str(no_rev["revenue"])) == Decimal("0.00")
    assert no_rev["margin_percent"] is None
