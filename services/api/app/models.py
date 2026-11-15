from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Role(str, enum.Enum):
    owner = "owner"
    manager = "manager"
    accountant = "accountant"


class GreenhouseStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Crop(str, enum.Enum):
    tomato = "tomato"
    pepper = "pepper"
    zucchini = "zucchini"
    cucumber = "cucumber"


class CropCycleStatus(str, enum.Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class SaleChannel(str, enum.Enum):
    wholesaler = "wholesaler"
    market = "market"
    distributor = "distributor"
    other = "other"


class ExpenseCategory(str, enum.Enum):
    seeds_plants = "seeds_plants"
    fertilizer = "fertilizer"
    water = "water"
    energy = "energy"
    labor = "labor"
    equipment = "equipment"
    maintenance = "maintenance"
    transport = "transport"
    packaging = "packaging"
    other = "other"


class ExpenseScope(str, enum.Enum):
    whole_farm = "whole_farm"
    greenhouse = "greenhouse"
    crop_cycle = "crop_cycle"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), index=True)
    locale: Mapped[str] = mapped_column(String(5), default="en")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Greenhouse(Base):
    __tablename__ = "greenhouses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    area_m2: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[GreenhouseStatus] = mapped_column(Enum(GreenhouseStatus), default=GreenhouseStatus.active)
    notes: Mapped[str | None] = mapped_column(Text)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    crop_cycles: Mapped[list[CropCycle]] = relationship(back_populates="greenhouse")


class CropCycle(Base):
    __tablename__ = "crop_cycles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    greenhouse_id: Mapped[str] = mapped_column(ForeignKey("greenhouses.id"), index=True)
    crop: Mapped[Crop] = mapped_column(Enum(Crop), index=True)
    planting_date: Mapped[date] = mapped_column(Date)
    expected_end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[CropCycleStatus] = mapped_column(Enum(CropCycleStatus), default=CropCycleStatus.planned, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    greenhouse: Mapped[Greenhouse] = relationship(back_populates="crop_cycles")


class HarvestEvent(Base):
    __tablename__ = "harvest_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    crop_cycle_id: Mapped[str] = mapped_column(ForeignKey("crop_cycles.id"), index=True)
    harvest_date: Mapped[date] = mapped_column(Date, index=True)
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    quality_grade: Mapped[str | None] = mapped_column(String(30))
    notes: Mapped[str | None] = mapped_column(Text)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(180), index=True)
    contact_ref: Mapped[str | None] = mapped_column(String(180))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_sales_idempotency_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    sale_date: Mapped[date] = mapped_column(Date, index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    crop_cycle_id: Mapped[str] = mapped_column(ForeignKey("crop_cycles.id"), index=True)
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    unit_price_mad: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total_mad: Mapped[Decimal] = mapped_column(Numeric(14, 2), index=True)
    channel: Mapped[SaleChannel | None] = mapped_column(Enum(SaleChannel))
    external_reference: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_expenses_idempotency_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    expense_date: Mapped[date] = mapped_column(Date, index=True)
    category: Mapped[ExpenseCategory] = mapped_column(Enum(ExpenseCategory), index=True)
    amount_mad: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    scope: Mapped[ExpenseScope] = mapped_column(Enum(ExpenseScope), index=True)
    greenhouse_id: Mapped[str | None] = mapped_column(ForeignKey("greenhouses.id"), index=True)
    crop_cycle_id: Mapped[str | None] = mapped_column(ForeignKey("crop_cycles.id"), index=True)
    supplier_reference: Mapped[str | None] = mapped_column(String(160))
    notes: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class FinancialAnalysis(Base):
    __tablename__ = "financial_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    cutoff_month: Mapped[str] = mapped_column(String(7), index=True)
    facts: Mapped[dict] = mapped_column(JSON)
    forecast: Mapped[dict] = mapped_column(JSON)
    narrative_en: Mapped[str] = mapped_column(Text)
    narrative_ar: Mapped[str] = mapped_column(Text)
    source_hash: Mapped[str] = mapped_column(String(128), index=True)
    model_version: Mapped[str] = mapped_column(String(32))
    stale: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    actor_id: Mapped[str | None] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(32))
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    field_names: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    alert_name: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), default="open")
    actions: Mapped[dict] = mapped_column(JSON)
    evidence: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
