import os
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["SEED_DEMO"] = "false"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from app.core.money import utc_now
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import (
    Crop,
    CropCycle,
    CropCycleStatus,
    Customer,
    Expense,
    ExpenseCategory,
    ExpenseScope,
    Greenhouse,
    GreenhouseStatus,
    HarvestEvent,
    Role,
    Sale,
    User,
)


@pytest.fixture()
def client():
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def _get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db

    db = TestingSession()
    now = utc_now()
    db.add_all(
        [
            User(email="owner@farm.ma", password_hash=hash_password("Owner123!"), role=Role.owner, locale="en", active=True, created_at=now, updated_at=now),
            User(email="manager@farm.ma", password_hash=hash_password("Manager123!"), role=Role.manager, locale="en", active=True, created_at=now, updated_at=now),
            User(
                email="accountant@farm.ma",
                password_hash=hash_password("Accountant123!"),
                role=Role.accountant,
                locale="en",
                active=True,
                created_at=now,
                updated_at=now,
            ),
        ]
    )
    db.flush()

    gh = Greenhouse(name="GH-T1", area_m2=Decimal("100"), status=GreenhouseStatus.active, notes=None, deleted_at=None, created_at=now, updated_at=now)
    db.add(gh)
    db.flush()
    cycle = CropCycle(
        greenhouse_id=gh.id,
        crop=Crop.tomato,
        planting_date=date(2026, 1, 1),
        expected_end_date=None,
        status=CropCycleStatus.active,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )
    customer = Customer(name="Customer A", contact_ref="x", deleted_at=None, created_at=now, updated_at=now)
    db.add_all([cycle, customer])
    db.flush()
    db.add(
        HarvestEvent(
            crop_cycle_id=cycle.id,
            harvest_date=date(2026, 1, 15),
            quantity_kg=Decimal("1000"),
            quality_grade=None,
            notes=None,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        )
    )
    db.commit()
    db.close()

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def db(client) -> Session:
    override = app.dependency_overrides[get_db]
    session_gen = override()
    session = next(session_gen)
    try:
        yield session
    finally:
        session.close()


def auth(client: TestClient, email: str, password: str) -> dict[str, str]:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture()
def headers_owner(client):
    return auth(client, "owner@farm.ma", "Owner123!")


@pytest.fixture()
def headers_manager(client):
    return auth(client, "manager@farm.ma", "Manager123!")


@pytest.fixture()
def headers_accountant(client):
    return auth(client, "accountant@farm.ma", "Accountant123!")


def seed_monthly_finance(db: Session, cycle_id: str, customer_id: str, months: int):
    now = utc_now()
    for idx in range(months):
        month = idx + 1
        price = Decimal("5.00") + Decimal(idx) * Decimal("0.10")
        qty = Decimal("100")
        db.add(
            Sale(
                sale_date=date(2026, month, 20),
                customer_id=customer_id,
                crop_cycle_id=cycle_id,
                quantity_kg=qty,
                unit_price_mad=price,
                total_mad=(qty * price).quantize(Decimal("0.01")),
                channel=None,
                external_reference=None,
                notes=None,
                idempotency_key=None,
                deleted_at=None,
                created_at=now,
                updated_at=now,
            )
        )
        db.add(
            Expense(
                expense_date=date(2026, month, 10),
                category=ExpenseCategory.energy,
                amount_mad=(Decimal("200.00") + Decimal(idx) * Decimal("10.00")).quantize(Decimal("0.01")),
                scope=ExpenseScope.whole_farm,
                greenhouse_id=None,
                crop_cycle_id=None,
                supplier_reference=None,
                notes=None,
                idempotency_key=None,
                deleted_at=None,
                created_at=now,
                updated_at=now,
            )
        )
    db.commit()
