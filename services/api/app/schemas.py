from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import (
    Crop,
    CropCycleStatus,
    ExpenseCategory,
    ExpenseScope,
    GreenhouseStatus,
    Role,
    SaleChannel,
)


class Msg(BaseModel):
    detail: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: Role
    locale: str = Field(default="en")


class UserUpdate(BaseModel):
    role: Role | None = None
    locale: str | None = None
    active: bool | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    role: Role
    locale: str
    active: bool


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class GreenhouseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    area_m2: Decimal = Field(gt=0)
    status: GreenhouseStatus = GreenhouseStatus.active
    notes: str | None = None


class GreenhouseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    area_m2: Decimal | None = Field(default=None, gt=0)
    status: GreenhouseStatus | None = None
    notes: str | None = None
    deleted: bool | None = None


class GreenhouseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    area_m2: Decimal
    status: GreenhouseStatus
    notes: str | None = None


class CropCycleCreate(BaseModel):
    greenhouse_id: str
    crop: Crop
    planting_date: date
    expected_end_date: date | None = None
    status: CropCycleStatus = CropCycleStatus.planned


class CropCycleUpdate(BaseModel):
    crop: Crop | None = None
    planting_date: date | None = None
    expected_end_date: date | None = None
    status: CropCycleStatus | None = None
    deleted: bool | None = None


class CropCycleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    greenhouse_id: str
    crop: Crop
    planting_date: date
    expected_end_date: date | None = None
    status: CropCycleStatus


class HarvestCreate(BaseModel):
    crop_cycle_id: str
    harvest_date: date
    quantity_kg: Decimal = Field(gt=0)
    quality_grade: str | None = None
    notes: str | None = None


class HarvestUpdate(BaseModel):
    harvest_date: date | None = None
    quantity_kg: Decimal | None = Field(default=None, gt=0)
    quality_grade: str | None = None
    notes: str | None = None
    deleted: bool | None = None


class HarvestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    crop_cycle_id: str
    harvest_date: date
    quantity_kg: Decimal
    quality_grade: str | None = None
    notes: str | None = None


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    contact_ref: str | None = None


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    contact_ref: str | None = None


class SaleCreate(BaseModel):
    sale_date: date
    customer_id: str
    crop_cycle_id: str
    quantity_kg: Decimal = Field(gt=0)
    unit_price_mad: Decimal = Field(ge=0)
    channel: SaleChannel | None = None
    external_reference: str | None = None
    notes: str | None = None


class SaleUpdate(BaseModel):
    sale_date: date | None = None
    customer_id: str | None = None
    crop_cycle_id: str | None = None
    quantity_kg: Decimal | None = Field(default=None, gt=0)
    unit_price_mad: Decimal | None = Field(default=None, ge=0)
    channel: SaleChannel | None = None
    external_reference: str | None = None
    notes: str | None = None
    deleted: bool | None = None


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    sale_date: date
    customer_id: str
    crop_cycle_id: str
    quantity_kg: Decimal
    unit_price_mad: Decimal
    total_mad: Decimal
    channel: SaleChannel | None = None


class ExpenseCreate(BaseModel):
    expense_date: date
    category: ExpenseCategory
    amount_mad: Decimal = Field(gt=0)
    scope: ExpenseScope
    greenhouse_id: str | None = None
    crop_cycle_id: str | None = None
    supplier_reference: str | None = None
    notes: str | None = None


class ExpenseUpdate(BaseModel):
    expense_date: date | None = None
    category: ExpenseCategory | None = None
    amount_mad: Decimal | None = Field(default=None, gt=0)
    scope: ExpenseScope | None = None
    greenhouse_id: str | None = None
    crop_cycle_id: str | None = None
    supplier_reference: str | None = None
    notes: str | None = None
    deleted: bool | None = None


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    expense_date: date
    category: ExpenseCategory
    amount_mad: Decimal
    scope: ExpenseScope
    greenhouse_id: str | None = None
    crop_cycle_id: str | None = None


class AnalysisCreate(BaseModel):
    end_month: str = Field(pattern=r"^\d{4}-\d{2}$")


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    cutoff_month: str
    facts: dict[str, Any]
    forecast: dict[str, Any]
    narrative_en: str
    narrative_ar: str
    source_hash: str
    model_version: str
    stale: bool
    created_at: datetime
