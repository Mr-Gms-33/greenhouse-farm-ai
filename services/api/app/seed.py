from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.money import utc_now
from app.core.security import hash_password
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
    SaleChannel,
    User,
)


def seed_demo(db: Session) -> None:
    if db.scalar(select(User.id).limit(1)):
        return

    now = utc_now()
    owner = User(
        email="owner@farm.ma",
        password_hash=hash_password("Owner123!"),
        role=Role.owner,
        locale="en",
        active=True,
        created_at=now,
        updated_at=now,
    )
    manager = User(
        email="manager@farm.ma",
        password_hash=hash_password("Manager123!"),
        role=Role.manager,
        locale="en",
        active=True,
        created_at=now,
        updated_at=now,
    )
    accountant = User(
        email="accountant@farm.ma",
        password_hash=hash_password("Accountant123!"),
        role=Role.accountant,
        locale="en",
        active=True,
        created_at=now,
        updated_at=now,
    )
    db.add_all([owner, manager, accountant])

    gh = Greenhouse(name="GH-1", area_m2=Decimal("1000"), status=GreenhouseStatus.active, notes=None, deleted_at=None, created_at=now, updated_at=now)
    db.add(gh)
    db.flush()
    cycle = CropCycle(
        greenhouse_id=gh.id,
        crop=Crop.tomato,
        planting_date=date(2026, 1, 5),
        expected_end_date=None,
        status=CropCycleStatus.completed,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )
    db.add(cycle)
    db.flush()

    cust = Customer(name="Demo Buyer", contact_ref="demo", deleted_at=None, created_at=now, updated_at=now)
    db.add(cust)
    db.flush()

    months = [
        (2026, 1),
        (2026, 2),
        (2026, 3),
        (2026, 4),
        (2026, 5),
        (2026, 6),
        (2026, 7),
        (2026, 8),
        (2026, 9),
    ]
    for i, (y, m) in enumerate(months, start=1):
        h = HarvestEvent(
            crop_cycle_id=cycle.id,
            harvest_date=date(y, m, 20),
            quantity_kg=Decimal("1000"),
            quality_grade="A",
            notes=None,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        )
        sale_qty = Decimal("800")
        unit_price = Decimal("4.50") + Decimal(i) * Decimal("0.10")
        s = Sale(
            sale_date=date(y, m, 21),
            customer_id=cust.id,
            crop_cycle_id=cycle.id,
            quantity_kg=sale_qty,
            unit_price_mad=unit_price,
            total_mad=(sale_qty * unit_price).quantize(Decimal("0.01")),
            channel=SaleChannel.wholesaler,
            external_reference=f"INV-{i}",
            notes=None,
            idempotency_key=None,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        )
        e1 = Expense(
            expense_date=date(y, m, 15),
            category=ExpenseCategory.energy,
            amount_mad=Decimal("900.00") + Decimal(i) * Decimal("10.00"),
            scope=ExpenseScope.greenhouse,
            greenhouse_id=gh.id,
            crop_cycle_id=None,
            supplier_reference=None,
            notes=None,
            idempotency_key=None,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        )
        e2 = Expense(
            expense_date=date(y, m, 16),
            category=ExpenseCategory.transport,
            amount_mad=Decimal("200.00") + Decimal(i) * Decimal("5.00"),
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
        db.add_all([h, s, e1, e2])

    db.commit()
