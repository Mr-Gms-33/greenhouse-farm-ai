from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import configure_logging, new_trace_id, trace_id_var
from app.core.money import farm_today, kg, money, utc_now
from app.core.runtime_flags import force_analysis_failure_enabled, summary_only_mode_enabled
from app.core import runtime_flags
from app.core.security import create_access_token, hash_password, verify_password
from app.db.base import Base
from app.db.session import SessionLocal, engine, get_db
from app.deps import get_current_user, require_roles
from app.models import (
    CropCycle,
    CropCycleStatus,
    Customer,
    Expense,
    ExpenseScope,
    FinancialAnalysis,
    Greenhouse,
    GreenhouseStatus,
    HarvestEvent,
    Incident,
    Role,
    Sale,
    User,
)
from app.schemas import (
    AnalysisCreate,
    AnalysisOut,
    CropCycleCreate,
    CropCycleOut,
    CropCycleUpdate,
    CustomerCreate,
    CustomerOut,
    ExpenseCreate,
    ExpenseOut,
    ExpenseUpdate,
    GreenhouseCreate,
    GreenhouseOut,
    GreenhouseUpdate,
    HarvestCreate,
    HarvestOut,
    HarvestUpdate,
    LoginIn,
    Msg,
    SaleCreate,
    SaleOut,
    SaleUpdate,
    TokenOut,
    UserCreate,
    UserOut,
    UserUpdate,
)
from app.seed import seed_demo
from app.services import (
    MODEL_VERSION,
    check_harvest_oversold,
    create_audit,
    enforce_unsold,
    generate_analysis,
    mark_affected_analyses_stale,
    report_by_crop,
    report_by_greenhouse,
    report_by_month,
    report_summary,
    to_jsonable,
    total_harvested_kg,
)

configure_logging(settings.log_level)
logger = logging.getLogger("api")

JOURNEY = Counter(
    "financial_analysis_journey_total",
    "Financial analysis journey outcomes",
    ["result"],
)
JOURNEY_LATENCY = Histogram(
    "financial_analysis_journey_duration_seconds",
    "Financial analysis journey latency",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.seed_demo:
        db = SessionLocal()
        try:
            seed_demo(db)
            db.commit()
        finally:
            db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    incoming = request.headers.get("traceparent") or request.headers.get("x-trace-id")
    trace_id = incoming.split("-")[1] if incoming and "-" in incoming else (incoming or new_trace_id())
    token = trace_id_var.set(trace_id[:32])
    started = time.perf_counter()
    try:
        response = await call_next(request)
    finally:
        trace_id_var.reset(token)
    response.headers["X-Trace-Id"] = trace_id[:32]
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%s",
        request.method,
        request.url.path,
        getattr(response, "status_code", "-"),
        int((time.perf_counter() - started) * 1000),
    )
    return response


def _ops_guard(x_ops_token: str | None) -> None:
    expected = getattr(settings, "ops_token", None) or "dev-ops-token"
    # Allow env OPS_TOKEN via extra settings field if present
    import os

    expected = os.getenv("OPS_TOKEN", expected)
    if not x_ops_token or x_ops_token != expected:
        raise HTTPException(status_code=401, detail="invalid ops token")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ---------- Auth ----------
@app.post("/api/v1/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.active:
        raise HTTPException(status_code=403, detail="User deactivated")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@app.post("/api/v1/auth/logout", response_model=Msg)
def logout(_: User = Depends(get_current_user)) -> Msg:
    return Msg(detail="logged_out")


@app.get("/api/v1/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@app.get("/api/v1/users", response_model=list[UserOut])
def list_users(_: User = Depends(require_roles(Role.owner)), db: Session = Depends(get_db)) -> list[User]:
    return list(db.scalars(select(User).order_by(User.email)).all())


@app.post("/api/v1/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, actor: User = Depends(require_roles(Role.owner)), db: Session = Depends(get_db)) -> User:
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=400, detail="Email already exists")
    now = utc_now()
    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        locale=payload.locale,
        active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    db.flush()
    create_audit(db, actor_id=actor.id, action="create", entity_type="user", entity_id=user.id, field_names=["email", "role"])
    db.commit()
    db.refresh(user)
    return user


@app.patch("/api/v1/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    payload: UserUpdate,
    actor: User = Depends(require_roles(Role.owner)),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    if payload.active is False and user.role == Role.owner:
        active_owners = db.scalars(select(User).where(User.role == Role.owner, User.active.is_(True))).all()
        if len(active_owners) <= 1 and user.active:
            raise HTTPException(status_code=400, detail="Cannot deactivate the last active owner")
    fields = []
    for field in ("role", "locale", "active"):
        value = getattr(payload, field)
        if value is not None:
            setattr(user, field, value)
            fields.append(field)
    user.updated_at = utc_now()
    create_audit(db, actor_id=actor.id, action="update", entity_type="user", entity_id=user.id, field_names=fields)
    db.commit()
    db.refresh(user)
    return user


# ---------- Operations ----------
@app.get("/api/v1/greenhouses", response_model=list[GreenhouseOut])
def list_greenhouses(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Greenhouse]:
    return list(db.scalars(select(Greenhouse).where(Greenhouse.deleted_at.is_(None)).order_by(Greenhouse.name)).all())


@app.post("/api/v1/greenhouses", response_model=GreenhouseOut, status_code=201)
def create_greenhouse(
    payload: GreenhouseCreate,
    actor: User = Depends(require_roles(Role.owner, Role.manager)),
    db: Session = Depends(get_db),
) -> Greenhouse:
    if db.scalar(select(Greenhouse).where(Greenhouse.name == payload.name, Greenhouse.deleted_at.is_(None))):
        raise HTTPException(status_code=400, detail="Greenhouse name already exists")
    now = utc_now()
    gh = Greenhouse(
        name=payload.name,
        area_m2=money(payload.area_m2),
        status=payload.status,
        notes=payload.notes,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )
    db.add(gh)
    db.flush()
    create_audit(db, actor_id=actor.id, action="create", entity_type="greenhouse", entity_id=gh.id, field_names=["name", "area_m2"])
    db.commit()
    db.refresh(gh)
    return gh


@app.patch("/api/v1/greenhouses/{greenhouse_id}", response_model=GreenhouseOut)
def update_greenhouse(
    greenhouse_id: str,
    payload: GreenhouseUpdate,
    actor: User = Depends(require_roles(Role.owner, Role.manager)),
    db: Session = Depends(get_db),
) -> Greenhouse:
    gh = db.get(Greenhouse, greenhouse_id)
    if not gh or gh.deleted_at:
        raise HTTPException(status_code=404, detail="Not found")
    fields = []
    if payload.name is not None:
        gh.name = payload.name
        fields.append("name")
    if payload.area_m2 is not None:
        gh.area_m2 = money(payload.area_m2)
        fields.append("area_m2")
    if payload.status is not None:
        gh.status = payload.status
        fields.append("status")
    if payload.notes is not None:
        gh.notes = payload.notes
        fields.append("notes")
    if payload.deleted:
        gh.deleted_at = utc_now()
        fields.append("deleted_at")
    gh.updated_at = utc_now()
    create_audit(db, actor_id=actor.id, action="update", entity_type="greenhouse", entity_id=gh.id, field_names=fields)
    db.commit()
    db.refresh(gh)
    return gh


@app.get("/api/v1/crop-cycles", response_model=list[CropCycleOut])
def list_cycles(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[CropCycle]:
    return list(db.scalars(select(CropCycle).where(CropCycle.deleted_at.is_(None))).all())


@app.post("/api/v1/crop-cycles", response_model=CropCycleOut, status_code=201)
def create_cycle(
    payload: CropCycleCreate,
    actor: User = Depends(require_roles(Role.owner, Role.manager)),
    db: Session = Depends(get_db),
) -> CropCycle:
    gh = db.get(Greenhouse, payload.greenhouse_id)
    if not gh or gh.deleted_at or gh.status != GreenhouseStatus.active:
        raise HTTPException(status_code=400, detail="Greenhouse unavailable for new cycle")
    if payload.expected_end_date and payload.expected_end_date < payload.planting_date:
        raise HTTPException(status_code=400, detail="expected_end_date before planting_date")
    if payload.status == CropCycleStatus.active:
        existing = db.scalar(
            select(CropCycle).where(
                CropCycle.greenhouse_id == payload.greenhouse_id,
                CropCycle.status == CropCycleStatus.active,
                CropCycle.deleted_at.is_(None),
            )
        )
        if existing:
            raise HTTPException(status_code=400, detail="Greenhouse already has an active crop cycle")
    now = utc_now()
    cycle = CropCycle(
        greenhouse_id=payload.greenhouse_id,
        crop=payload.crop,
        planting_date=payload.planting_date,
        expected_end_date=payload.expected_end_date,
        status=payload.status,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )
    db.add(cycle)
    db.flush()
    create_audit(db, actor_id=actor.id, action="create", entity_type="crop_cycle", entity_id=cycle.id, field_names=["crop", "status"])
    db.commit()
    db.refresh(cycle)
    return cycle


@app.patch("/api/v1/crop-cycles/{cycle_id}", response_model=CropCycleOut)
def update_cycle(
    cycle_id: str,
    payload: CropCycleUpdate,
    actor: User = Depends(require_roles(Role.owner, Role.manager)),
    db: Session = Depends(get_db),
) -> CropCycle:
    cycle = db.get(CropCycle, cycle_id)
    if not cycle or cycle.deleted_at:
        raise HTTPException(status_code=404, detail="Not found")
    fields = []
    new_status = payload.status or cycle.status
    if new_status == CropCycleStatus.active:
        other = db.scalar(
            select(CropCycle).where(
                CropCycle.greenhouse_id == cycle.greenhouse_id,
                CropCycle.status == CropCycleStatus.active,
                CropCycle.deleted_at.is_(None),
                CropCycle.id != cycle.id,
            )
        )
        if other:
            raise HTTPException(status_code=400, detail="Greenhouse already has an active crop cycle")
    for field in ("crop", "planting_date", "expected_end_date", "status"):
        value = getattr(payload, field)
        if value is not None:
            setattr(cycle, field, value)
            fields.append(field)
    if payload.deleted:
        cycle.deleted_at = utc_now()
        fields.append("deleted_at")
    cycle.updated_at = utc_now()
    create_audit(db, actor_id=actor.id, action="update", entity_type="crop_cycle", entity_id=cycle.id, field_names=fields)
    db.commit()
    db.refresh(cycle)
    return cycle


@app.get("/api/v1/harvests", response_model=list[HarvestOut])
def list_harvests(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[HarvestEvent]:
    return list(db.scalars(select(HarvestEvent).where(HarvestEvent.deleted_at.is_(None))).all())


@app.post("/api/v1/harvests", response_model=HarvestOut, status_code=201)
def create_harvest(
    payload: HarvestCreate,
    actor: User = Depends(require_roles(Role.owner, Role.manager)),
    db: Session = Depends(get_db),
) -> HarvestEvent:
    cycle = db.get(CropCycle, payload.crop_cycle_id)
    if not cycle or cycle.deleted_at or cycle.status != CropCycleStatus.active:
        raise HTTPException(status_code=400, detail="Harvest requires an active crop cycle")
    if payload.harvest_date < cycle.planting_date or payload.harvest_date > farm_today():
        raise HTTPException(status_code=400, detail="Invalid harvest date")
    now = utc_now()
    harvest = HarvestEvent(
        crop_cycle_id=payload.crop_cycle_id,
        harvest_date=payload.harvest_date,
        quantity_kg=kg(payload.quantity_kg),
        quality_grade=payload.quality_grade,
        notes=payload.notes,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )
    db.add(harvest)
    db.flush()
    create_audit(db, actor_id=actor.id, action="create", entity_type="harvest", entity_id=harvest.id, field_names=["quantity_kg"])
    db.commit()
    db.refresh(harvest)
    return harvest


@app.patch("/api/v1/harvests/{harvest_id}", response_model=HarvestOut)
def update_harvest(
    harvest_id: str,
    payload: HarvestUpdate,
    actor: User = Depends(require_roles(Role.owner, Role.manager)),
    db: Session = Depends(get_db),
) -> HarvestEvent:
    harvest = db.get(HarvestEvent, harvest_id)
    if not harvest or harvest.deleted_at:
        raise HTTPException(status_code=404, detail="Not found")
    fields = []
    if payload.quantity_kg is not None:
        harvest.quantity_kg = kg(payload.quantity_kg)
        fields.append("quantity_kg")
    if payload.harvest_date is not None:
        harvest.harvest_date = payload.harvest_date
        fields.append("harvest_date")
    if payload.quality_grade is not None:
        harvest.quality_grade = payload.quality_grade
        fields.append("quality_grade")
    if payload.notes is not None:
        harvest.notes = payload.notes
        fields.append("notes")
    if payload.deleted:
        harvest.deleted_at = utc_now()
        fields.append("deleted_at")
    harvest.updated_at = utc_now()
    try:
        check_harvest_oversold(db, harvest.crop_cycle_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    create_audit(db, actor_id=actor.id, action="update", entity_type="harvest", entity_id=harvest.id, field_names=fields)
    db.commit()
    db.refresh(harvest)
    return harvest


# ---------- Finance ----------
def _finance_read(user: User) -> None:
    if user.role == Role.manager:
        raise HTTPException(status_code=403, detail="Forbidden")


@app.get("/api/v1/customers", response_model=list[CustomerOut])
def list_customers(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Customer]:
    _finance_read(user)
    return list(db.scalars(select(Customer).where(Customer.deleted_at.is_(None))).all())


@app.post("/api/v1/customers", response_model=CustomerOut, status_code=201)
def create_customer(
    payload: CustomerCreate,
    actor: User = Depends(require_roles(Role.owner, Role.accountant)),
    db: Session = Depends(get_db),
) -> Customer:
    now = utc_now()
    customer = Customer(name=payload.name, contact_ref=payload.contact_ref, deleted_at=None, created_at=now, updated_at=now)
    db.add(customer)
    db.flush()
    create_audit(db, actor_id=actor.id, action="create", entity_type="customer", entity_id=customer.id, field_names=["name"])
    db.commit()
    db.refresh(customer)
    return customer


@app.get("/api/v1/sales", response_model=list[SaleOut])
def list_sales(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Sale]:
    _finance_read(user)
    return list(db.scalars(select(Sale).where(Sale.deleted_at.is_(None))).all())


@app.post("/api/v1/sales", response_model=SaleOut, status_code=201)
def create_sale(
    payload: SaleCreate,
    actor: User = Depends(require_roles(Role.owner, Role.accountant)),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Sale:
    if idempotency_key:
        existing = db.scalar(select(Sale).where(Sale.idempotency_key == idempotency_key))
        if existing:
            return existing
    try:
        enforce_unsold(db, payload.crop_cycle_id, payload.quantity_kg)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    qty = kg(payload.quantity_kg)
    price = money(payload.unit_price_mad)
    total = money(Decimal(str(payload.quantity_kg)) * Decimal(str(payload.unit_price_mad)))
    now = utc_now()
    sale = Sale(
        sale_date=payload.sale_date,
        customer_id=payload.customer_id,
        crop_cycle_id=payload.crop_cycle_id,
        quantity_kg=qty,
        unit_price_mad=price,
        total_mad=total,
        channel=payload.channel,
        external_reference=payload.external_reference,
        notes=payload.notes,
        idempotency_key=idempotency_key,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )
    db.add(sale)
    db.flush()
    mark_affected_analyses_stale(db)
    create_audit(db, actor_id=actor.id, action="create", entity_type="sale", entity_id=sale.id, field_names=["quantity_kg", "unit_price_mad"])
    db.commit()
    db.refresh(sale)
    return sale


@app.patch("/api/v1/sales/{sale_id}", response_model=SaleOut)
def update_sale(
    sale_id: str,
    payload: SaleUpdate,
    actor: User = Depends(require_roles(Role.owner, Role.accountant)),
    db: Session = Depends(get_db),
) -> Sale:
    sale = db.get(Sale, sale_id)
    if not sale or sale.deleted_at:
        raise HTTPException(status_code=404, detail="Not found")
    fields = []
    qty = payload.quantity_kg if payload.quantity_kg is not None else sale.quantity_kg
    price = payload.unit_price_mad if payload.unit_price_mad is not None else sale.unit_price_mad
    cycle_id = payload.crop_cycle_id or sale.crop_cycle_id
    try:
        enforce_unsold(db, cycle_id, qty, exclude_sale_id=sale.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    for field in ("sale_date", "customer_id", "crop_cycle_id", "channel", "external_reference", "notes"):
        value = getattr(payload, field)
        if value is not None:
            setattr(sale, field, value)
            fields.append(field)
    sale.quantity_kg = kg(qty)
    sale.unit_price_mad = money(price)
    sale.total_mad = money(Decimal(str(qty)) * Decimal(str(price)))
    fields.extend(["quantity_kg", "unit_price_mad", "total_mad"])
    if payload.deleted:
        sale.deleted_at = utc_now()
        fields.append("deleted_at")
    sale.updated_at = utc_now()
    mark_affected_analyses_stale(db)
    create_audit(db, actor_id=actor.id, action="update", entity_type="sale", entity_id=sale.id, field_names=fields)
    db.commit()
    db.refresh(sale)
    return sale


@app.get("/api/v1/expenses", response_model=list[ExpenseOut])
def list_expenses(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Expense]:
    _finance_read(user)
    return list(db.scalars(select(Expense).where(Expense.deleted_at.is_(None))).all())


@app.post("/api/v1/expenses", response_model=ExpenseOut, status_code=201)
def create_expense(
    payload: ExpenseCreate,
    actor: User = Depends(require_roles(Role.owner, Role.accountant)),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Expense:
    if idempotency_key:
        existing = db.scalar(select(Expense).where(Expense.idempotency_key == idempotency_key))
        if existing:
            return existing
    if payload.scope == ExpenseScope.greenhouse and not payload.greenhouse_id:
        raise HTTPException(status_code=400, detail="greenhouse_id required")
    if payload.scope == ExpenseScope.crop_cycle and not payload.crop_cycle_id:
        raise HTTPException(status_code=400, detail="crop_cycle_id required")
    if payload.scope == ExpenseScope.whole_farm and (payload.greenhouse_id or payload.crop_cycle_id):
        raise HTTPException(status_code=400, detail="whole_farm expenses must not reference scopes")
    now = utc_now()
    expense = Expense(
        expense_date=payload.expense_date,
        category=payload.category,
        amount_mad=money(payload.amount_mad),
        scope=payload.scope,
        greenhouse_id=payload.greenhouse_id,
        crop_cycle_id=payload.crop_cycle_id,
        supplier_reference=payload.supplier_reference,
        notes=payload.notes,
        idempotency_key=idempotency_key,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )
    db.add(expense)
    db.flush()
    mark_affected_analyses_stale(db)
    create_audit(db, actor_id=actor.id, action="create", entity_type="expense", entity_id=expense.id, field_names=["amount_mad", "scope"])
    db.commit()
    db.refresh(expense)
    return expense


@app.patch("/api/v1/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: str,
    payload: ExpenseUpdate,
    actor: User = Depends(require_roles(Role.owner, Role.accountant)),
    db: Session = Depends(get_db),
) -> Expense:
    expense = db.get(Expense, expense_id)
    if not expense or expense.deleted_at:
        raise HTTPException(status_code=404, detail="Not found")
    fields = []
    for field in (
        "expense_date",
        "category",
        "scope",
        "greenhouse_id",
        "crop_cycle_id",
        "supplier_reference",
        "notes",
    ):
        value = getattr(payload, field)
        if value is not None:
            setattr(expense, field, value)
            fields.append(field)
    if payload.amount_mad is not None:
        expense.amount_mad = money(payload.amount_mad)
        fields.append("amount_mad")
    if payload.deleted:
        expense.deleted_at = utc_now()
        fields.append("deleted_at")
    expense.updated_at = utc_now()
    mark_affected_analyses_stale(db)
    create_audit(db, actor_id=actor.id, action="update", entity_type="expense", entity_id=expense.id, field_names=fields)
    db.commit()
    db.refresh(expense)
    return expense


@app.get("/api/v1/reports/summary")
def get_summary(date_from: date, date_to: date, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _finance_read(user)
    return report_summary(db, date_from, date_to)


@app.get("/api/v1/reports/by-month")
def get_by_month(date_from: date, date_to: date, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _finance_read(user)
    return report_by_month(db, date_from, date_to)


@app.get("/api/v1/reports/by-greenhouse")
def get_by_gh(date_from: date, date_to: date, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _finance_read(user)
    return report_by_greenhouse(db, date_from, date_to)


@app.get("/api/v1/reports/by-crop")
def get_by_crop(date_from: date, date_to: date, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _finance_read(user)
    return report_by_crop(db, date_from, date_to)


@app.get("/api/v1/analyses", response_model=list[AnalysisOut])
def list_analyses(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[FinancialAnalysis]:
    _finance_read(user)
    return list(db.scalars(select(FinancialAnalysis).order_by(FinancialAnalysis.created_at.desc())).all())


@app.get("/api/v1/analyses/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> FinancialAnalysis:
    _finance_read(user)
    analysis = db.get(FinancialAnalysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Not found")
    return analysis


@app.post("/api/v1/analyses", response_model=AnalysisOut, status_code=201)
def create_analysis(
    payload: AnalysisCreate,
    actor: User = Depends(require_roles(Role.owner, Role.accountant)),
    db: Session = Depends(get_db),
) -> FinancialAnalysis:
    started = time.perf_counter()
    result_label = "success"
    try:
        if runtime_flags.summary_only_mode_enabled:
            summary = report_summary(db, date(2000, 1, 1), farm_today())
            analysis = FinancialAnalysis(
                cutoff_month=payload.end_month,
                facts=to_jsonable({"totals": summary, "coverage": {"complete_month_count": 0}, "source_counts": {}}),
                forecast={"status": "summary_only", "model_version": MODEL_VERSION},
                narrative_en="Deterministic summary-only mode. Forecast engine temporarily unavailable.",
                narrative_ar="وضع الملخص الحتمي فقط. محرك التوقع غير متاح مؤقتاً.",
                source_hash="summary-only",
                model_version=MODEL_VERSION,
                stale=False,
                created_at=utc_now(),
            )
            result_label = "summary_only"
        else:
            generated = generate_analysis(db, payload.end_month)
            if generated.forecast.get("status") == "insufficient_data":
                result_label = "insufficient_data"
            if runtime_flags.force_analysis_failure_enabled:
                generated.narrative_en = "Fallback narrative: structured analysis is available."
                generated.narrative_ar = "سرد احتياطي: التحليل البنيوي متاح."
            analysis = FinancialAnalysis(
                cutoff_month=payload.end_month,
                facts=to_jsonable(generated.facts),
                forecast=to_jsonable(generated.forecast),
                narrative_en=generated.narrative_en,
                narrative_ar=generated.narrative_ar,
                source_hash=generated.source_hash,
                model_version=MODEL_VERSION,
                stale=False,
                created_at=utc_now(),
            )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    finally:
        JOURNEY.labels(result=result_label).inc()
        JOURNEY_LATENCY.observe(time.perf_counter() - started)


@app.post("/api/v1/analyses/demo-fail")
def demo_fail(actor: User = Depends(require_roles(Role.owner))) -> dict[str, bool]:
    runtime_flags.force_analysis_failure_enabled = True
    return {"force_analysis_failure": True}


@app.post("/api/v1/ops/summary-only")
def ops_summary_only(payload: dict, x_ops_token: str | None = Header(default=None)) -> dict:
    _ops_guard(x_ops_token)
    runtime_flags.summary_only_mode_enabled = bool(payload.get("enabled"))
    return {"summary_only_mode": runtime_flags.summary_only_mode_enabled}


@app.post("/api/v1/ops/force-failure")
def ops_force_failure(payload: dict, x_ops_token: str | None = Header(default=None)) -> dict:
    _ops_guard(x_ops_token)
    runtime_flags.force_analysis_failure_enabled = bool(payload.get("enabled"))
    return {"force_analysis_failure": runtime_flags.force_analysis_failure_enabled}


@app.get("/api/v1/ops/journey-health")
def journey_health(x_ops_token: str | None = Header(default=None)) -> dict:
    _ops_guard(x_ops_token)
    ok = not runtime_flags.force_analysis_failure_enabled
    mode = "summary_only" if runtime_flags.summary_only_mode_enabled else "normal"
    return {"ok": ok, "mode": mode}


@app.post("/api/v1/incidents")
def create_incident(payload: dict, x_ops_token: str | None = Header(default=None), db: Session = Depends(get_db)) -> dict:
    _ops_guard(x_ops_token)
    incident = Incident(
        alert_name=payload.get("alert_name", "unknown"),
        status="resolved" if payload.get("recovered") else "open",
        actions={"action": payload.get("action"), "at": payload.get("at")},
        evidence=payload.get("evidence") or {},
        created_at=utc_now(),
    )
    db.add(incident)
    db.commit()
    return {"id": incident.id}


@app.get("/api/v1/dashboard")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    greenhouses = list(db.scalars(select(Greenhouse).where(Greenhouse.deleted_at.is_(None))).all())
    cycles = list(db.scalars(select(CropCycle).where(CropCycle.deleted_at.is_(None))).all())
    harvests = list(db.scalars(select(HarvestEvent).where(HarvestEvent.deleted_at.is_(None))).all())
    payload: dict = {
        "role": user.role.value,
        "greenhouses": [{"id": g.id, "name": g.name, "status": g.status.value} for g in greenhouses],
        "crop_cycles": [{"id": c.id, "crop": c.crop.value, "status": c.status.value, "greenhouse_id": c.greenhouse_id} for c in cycles],
        "harvest_total_kg": str(sum((h.quantity_kg for h in harvests), Decimal("0"))),
        "recent_harvests": [
            {"id": h.id, "quantity_kg": h.quantity_kg, "harvest_date": h.harvest_date.isoformat()} for h in harvests[-5:]
        ],
    }
    if user.role in (Role.owner, Role.accountant):
        summary = report_summary(db, date(2000, 1, 1), farm_today())
        analyses = list(db.scalars(select(FinancialAnalysis).order_by(FinancialAnalysis.created_at.desc()).limit(1)).all())
        payload["finance"] = summary
        payload["latest_analysis"] = AnalysisOut.model_validate(analyses[0]).model_dump() if analyses else None
        payload["recent_sales"] = [
            {"id": s.id, "total_mad": s.total_mad, "sale_date": s.sale_date.isoformat()}
            for s in db.scalars(select(Sale).where(Sale.deleted_at.is_(None)).order_by(Sale.sale_date.desc()).limit(5))
        ]
        payload["recent_expenses"] = [
            {"id": e.id, "amount_mad": e.amount_mad, "expense_date": e.expense_date.isoformat()}
            for e in db.scalars(select(Expense).where(Expense.deleted_at.is_(None)).order_by(Expense.expense_date.desc()).limit(5))
        ]
    return payload
