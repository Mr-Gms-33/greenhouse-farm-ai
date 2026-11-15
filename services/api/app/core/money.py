from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from app.core.config import settings

FARM_TZ = ZoneInfo(settings.farm_timezone)
MONEY_QUANT = Decimal("0.01")
KG_QUANT = Decimal("0.001")


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def kg(value) -> Decimal:
    return Decimal(str(value)).quantize(KG_QUANT, rounding=ROUND_HALF_UP)


def farm_now() -> datetime:
    return datetime.now(FARM_TZ)


def farm_today():
    return farm_now().date()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
