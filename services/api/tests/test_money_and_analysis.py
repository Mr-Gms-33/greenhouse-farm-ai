from decimal import Decimal

from app.core.money import money
from app.services import month_seq


def test_money_round_half_up():
    assert money("1.005") == Decimal("1.01")
    assert money("1.004") == Decimal("1.00")


def test_month_seq_inclusive():
    assert month_seq("2025-01", "2025-03") == ["2025-01", "2025-02", "2025-03"]
