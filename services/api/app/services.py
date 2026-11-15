from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import numpy as np
from sklearn.linear_model import LinearRegression
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.money import farm_today, kg, money, utc_now
from app.models import (
    AuditEvent,
    CropCycle,
    CropCycleStatus,
    Expense,
    ExpenseScope,
    FinancialAnalysis,
    Greenhouse,
    HarvestEvent,
    Sale,
)

MODEL_VERSION = "time-trend-v1"


def to_jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    if isinstance(value, dict):
        return {k: to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    return value


def create_audit(
    db: Session,
    *,
    actor_id: str | None,
    action: str,
    entity_type: str,
    entity_id: str,
    field_names: list[str],
) -> None:
    db.add(
        AuditEvent(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            field_names=field_names,
            created_at=utc_now(),
        )
    )


def total_harvested_kg(db: Session, crop_cycle_id: str) -> Decimal:
    q = select(func.coalesce(func.sum(HarvestEvent.quantity_kg), 0)).where(
        HarvestEvent.crop_cycle_id == crop_cycle_id, HarvestEvent.deleted_at.is_(None)
    )
    return kg(db.scalar(q) or 0)


def total_sold_kg(db: Session, crop_cycle_id: str, exclude_sale_id: str | None = None) -> Decimal:
    q = select(func.coalesce(func.sum(Sale.quantity_kg), 0)).where(Sale.crop_cycle_id == crop_cycle_id, Sale.deleted_at.is_(None))
    if exclude_sale_id:
        q = q.where(Sale.id != exclude_sale_id)
    return kg(db.scalar(q) or 0)


def enforce_unsold(db: Session, crop_cycle_id: str, new_sale_qty: Decimal, exclude_sale_id: str | None = None) -> None:
    harvested = total_harvested_kg(db, crop_cycle_id)
    sold_other = total_sold_kg(db, crop_cycle_id, exclude_sale_id=exclude_sale_id)
    if sold_other + kg(new_sale_qty) > harvested:
        raise ValueError("Sale quantity exceeds unsold harvested quantity")


def check_harvest_oversold(db: Session, crop_cycle_id: str, updated_harvest_id: str | None = None) -> None:
    harvested = total_harvested_kg(db, crop_cycle_id)
    sold = total_sold_kg(db, crop_cycle_id)
    if sold > harvested:
        raise ValueError("Harvest update would create oversold state")


def mark_affected_analyses_stale(db: Session) -> None:
    analyses = db.scalars(select(FinancialAnalysis).where(FinancialAnalysis.stale.is_(False))).all()
    for a in analyses:
        a.stale = True


def month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def month_seq(start_ym: str, end_ym: str) -> list[str]:
    sy, sm = [int(x) for x in start_ym.split("-")]
    ey, em = [int(x) for x in end_ym.split("-")]
    out: list[str] = []
    y, m = sy, sm
    while (y < ey) or (y == ey and m <= em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y += 1
            m = 1
    return out


def report_summary(db: Session, date_from: date, date_to: date) -> dict:
    revenue = money(
        db.scalar(select(func.coalesce(func.sum(Sale.total_mad), 0)).where(Sale.deleted_at.is_(None), Sale.sale_date >= date_from, Sale.sale_date <= date_to))
        or 0
    )
    expenses = money(
        db.scalar(
            select(func.coalesce(func.sum(Expense.amount_mad), 0)).where(
                Expense.deleted_at.is_(None), Expense.expense_date >= date_from, Expense.expense_date <= date_to
            )
        )
        or 0
    )
    profit = money(revenue - expenses)
    margin = None if revenue == 0 else money((profit / revenue) * 100)
    return {"revenue": revenue, "expenses": expenses, "profit": profit, "margin_percent": margin}


def report_by_month(db: Session, date_from: date, date_to: date) -> list[dict]:
    months = month_seq(month_key(date_from), month_key(date_to))
    out = []
    for ym in months:
        y, m = [int(x) for x in ym.split("-")]
        rev = money(
            db.scalar(
                select(func.coalesce(func.sum(Sale.total_mad), 0)).where(
                    Sale.deleted_at.is_(None), func.extract("year", Sale.sale_date) == y, func.extract("month", Sale.sale_date) == m
                )
            )
            or 0
        )
        exp = money(
            db.scalar(
                select(func.coalesce(func.sum(Expense.amount_mad), 0)).where(
                    Expense.deleted_at.is_(None),
                    func.extract("year", Expense.expense_date) == y,
                    func.extract("month", Expense.expense_date) == m,
                )
            )
            or 0
        )
        prof = money(rev - exp)
        out.append({"month": ym, "revenue": rev, "expenses": exp, "profit": prof, "margin_percent": None if rev == 0 else money((prof / rev) * 100)})
    return out


def report_by_greenhouse(db: Session, date_from: date, date_to: date) -> list[dict]:
    greenhouses = db.scalars(select(Greenhouse).where(Greenhouse.deleted_at.is_(None))).all()
    out = []
    for gh in greenhouses:
        rev = money(
            db.scalar(
                select(func.coalesce(func.sum(Sale.total_mad), 0))
                .join(CropCycle, CropCycle.id == Sale.crop_cycle_id)
                .where(
                    Sale.deleted_at.is_(None),
                    Sale.sale_date >= date_from,
                    Sale.sale_date <= date_to,
                    CropCycle.greenhouse_id == gh.id,
                )
            )
            or 0
        )
        exp = money(
            db.scalar(
                select(func.coalesce(func.sum(Expense.amount_mad), 0)).where(
                    Expense.deleted_at.is_(None),
                    Expense.expense_date >= date_from,
                    Expense.expense_date <= date_to,
                    Expense.scope == ExpenseScope.greenhouse,
                    Expense.greenhouse_id == gh.id,
                )
            )
            or 0
        )
        out.append({"greenhouse_id": gh.id, "greenhouse_name": gh.name, "revenue": rev, "scoped_expenses": exp, "profit_scoped": money(rev - exp)})
    return out


def report_by_crop(db: Session, date_from: date, date_to: date) -> list[dict]:
    out = []
    for crop in ["tomato", "pepper", "zucchini", "cucumber"]:
        rev = money(
            db.scalar(
                select(func.coalesce(func.sum(Sale.total_mad), 0))
                .join(CropCycle, CropCycle.id == Sale.crop_cycle_id)
                .where(
                    Sale.deleted_at.is_(None),
                    Sale.sale_date >= date_from,
                    Sale.sale_date <= date_to,
                    CropCycle.crop == crop,
                )
            )
            or 0
        )
        exp = money(
            db.scalar(
                select(func.coalesce(func.sum(Expense.amount_mad), 0))
                .join(CropCycle, CropCycle.id == Expense.crop_cycle_id, isouter=True)
                .where(
                    Expense.deleted_at.is_(None),
                    Expense.expense_date >= date_from,
                    Expense.expense_date <= date_to,
                    Expense.scope == ExpenseScope.crop_cycle,
                    CropCycle.crop == crop,
                )
            )
            or 0
        )
        out.append({"crop": crop, "revenue": rev, "scoped_expenses": exp, "profit_scoped": money(rev - exp)})
    return out


@dataclass
class AnalysisResult:
    facts: dict
    forecast: dict
    narrative_en: str
    narrative_ar: str
    source_hash: str


def _source_hash(sales: list[Sale], expenses: list[Expense]) -> str:
    payload = "|".join(
        sorted([f"s:{s.id}:{s.updated_at.isoformat()}" for s in sales] + [f"e:{e.id}:{e.updated_at.isoformat()}" for e in expenses])
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _facts_narrative(facts: dict, forecast_state: str) -> tuple[str, str]:
    summary_en = (
        f"Recorded facts from {facts['coverage']['first_month']} to {facts['coverage']['last_month']}: "
        f"revenue {facts['totals']['revenue']} MAD, expenses {facts['totals']['expenses']} MAD, "
        f"profit {facts['totals']['profit']} MAD. Forecast state: {forecast_state}."
    )
    summary_ar = (
        f"الحقائق المسجلة من {facts['coverage']['first_month']} إلى {facts['coverage']['last_month']}: "
        f"الإيرادات {facts['totals']['revenue']} درهم، المصاريف {facts['totals']['expenses']} درهم، "
        f"الربح {facts['totals']['profit']} درهم. حالة التوقع: {forecast_state}."
    )
    return summary_en, summary_ar


def generate_analysis(db: Session, end_month: str) -> AnalysisResult:
    sales = db.scalars(select(Sale).where(Sale.deleted_at.is_(None))).all()
    expenses = db.scalars(select(Expense).where(Expense.deleted_at.is_(None))).all()
    cutoff_year, cutoff_month = [int(x) for x in end_month.split("-")]
    sales = [s for s in sales if (s.sale_date.year, s.sale_date.month) <= (cutoff_year, cutoff_month)]
    expenses = [e for e in expenses if (e.expense_date.year, e.expense_date.month) <= (cutoff_year, cutoff_month)]

    all_months = [month_key(x.sale_date) for x in sales] + [month_key(x.expense_date) for x in expenses]
    if not all_months:
        months = [end_month]
    else:
        months = month_seq(min(all_months), end_month)

    monthly = []
    for ym in months:
        rev = money(sum(s.total_mad for s in sales if month_key(s.sale_date) == ym))
        exp = money(sum(e.amount_mad for e in expenses if month_key(e.expense_date) == ym))
        prof = money(rev - exp)
        monthly.append({"month": ym, "revenue": rev, "expenses": exp, "profit": prof})

    totals = {
        "revenue": money(sum(m["revenue"] for m in monthly)),
        "expenses": money(sum(m["expenses"] for m in monthly)),
        "profit": money(sum(m["profit"] for m in monthly)),
    }
    totals["margin_percent"] = None if totals["revenue"] == 0 else money((totals["profit"] / totals["revenue"]) * 100)

    facts = {
        "totals": totals,
        "coverage": {"first_month": months[0], "last_month": months[-1], "complete_month_count": len(months)},
        "source_counts": {"sales": len(sales), "expenses": len(expenses)},
        "monthly": monthly,
        "estimate_label": "estimate, not recorded fact",
    }

    source_hash = _source_hash(sales, expenses)

    if len(months) < 6:
        forecast = {"status": "insufficient_data", "model_version": MODEL_VERSION, "horizon_months": 3}
        en, ar = _facts_narrative(facts, "insufficient_data")
        return AnalysisResult(facts=facts, forecast=forecast, narrative_en=en, narrative_ar=ar, source_hash=source_hash)

    y_rev = np.array([float(m["revenue"]) for m in monthly])
    y_exp = np.array([float(m["expenses"]) for m in monthly])
    x = np.array(list(range(len(monthly)))).reshape(-1, 1)

    validation = None
    quality = "low_confidence" if len(months) < 8 else "validated"
    if len(months) >= 8:
        train_end = len(monthly) - 2
        x_train, x_val = x[:train_end], x[train_end:]
        rev_model = LinearRegression().fit(x_train, y_rev[:train_end])
        exp_model = LinearRegression().fit(x_train, y_exp[:train_end])
        rev_pred = rev_model.predict(x_val)
        exp_pred = exp_model.predict(x_val)
        prof_pred = rev_pred - exp_pred
        validation = {
            "window_months": [monthly[-2]["month"], monthly[-1]["month"]],
            "mae_revenue": money(np.mean(np.abs(rev_pred - y_rev[train_end:]))),
            "mae_expenses": money(np.mean(np.abs(exp_pred - y_exp[train_end:]))),
            "mae_profit": money(np.mean(np.abs(prof_pred - (y_rev[train_end:] - y_exp[train_end:])))),
            "training_months_excluded_validation": True,
        }

    rev_model = LinearRegression().fit(x, y_rev)
    exp_model = LinearRegression().fit(x, y_exp)
    future_x = np.array(list(range(len(monthly), len(monthly) + 3))).reshape(-1, 1)
    rev_fc = rev_model.predict(future_x)
    exp_fc = exp_model.predict(future_x)
    y0, m0 = [int(xp) for xp in months[-1].split("-")]
    next_months: list[str] = []
    yy, mm = y0, m0
    for _ in range(3):
        mm += 1
        if mm == 13:
            yy += 1
            mm = 1
        next_months.append(f"{yy:04d}-{mm:02d}")

    points = []
    for i, mo in enumerate(next_months):
        rv = money(max(0.0, float(rev_fc[i])))
        ex = money(max(0.0, float(exp_fc[i])))
        points.append({"month": mo, "revenue": rv, "expenses": ex, "profit": money(rv - ex), "estimate": True})

    forecast = {
        "status": "ok",
        "model_version": MODEL_VERSION,
        "horizon_months": 3,
        "data_quality": quality,
        "generated_at": utc_now().isoformat(),
        "validation": validation,
        "points": points,
    }
    en, ar = _facts_narrative(facts, quality)
    return AnalysisResult(facts=facts, forecast=forecast, narrative_en=en, narrative_ar=ar, source_hash=source_hash)
