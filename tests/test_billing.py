"""
Tests: Billing Strategies

Verifica cada implementação de BillingStrategy e o BillingService.
"""

import pytest
from decimal import Decimal

from app.services.billing_strategy import HourlyBilling, FixedBilling, DailyBilling
from app.services.billing_service import BillingService


class TestHourlyBilling:
    def setup_method(self):
        self.strategy = HourlyBilling(price_per_hour=Decimal("10.00"))

    def test_zero_hours(self):
        assert self.strategy.calculate(0) == Decimal("0.00")

    def test_negative_hours(self):
        assert self.strategy.calculate(-1) == Decimal("0.00")

    def test_exactly_one_hour(self):
        assert self.strategy.calculate(1.0) == Decimal("10.00")

    def test_fraction_rounds_up(self):
        # 1.5 horas → 2 horas cobradas
        assert self.strategy.calculate(1.5) == Decimal("20.00")

    def test_three_hours(self):
        assert self.strategy.calculate(3.0) == Decimal("30.00")

    def test_name(self):
        assert self.strategy.name == "hourly"


class TestFixedBilling:
    def setup_method(self):
        self.strategy = FixedBilling(fixed_amount=Decimal("25.00"))

    def test_always_fixed(self):
        for hours in [0.1, 1.0, 5.0, 24.0]:
            assert self.strategy.calculate(hours) == Decimal("25.00")

    def test_name(self):
        assert self.strategy.name == "fixed"


class TestDailyBilling:
    def setup_method(self):
        self.strategy = DailyBilling(price_per_day=Decimal("50.00"))

    def test_zero_hours(self):
        assert self.strategy.calculate(0) == Decimal("0.00")

    def test_less_than_one_day(self):
        assert self.strategy.calculate(10) == Decimal("50.00")

    def test_exactly_one_day(self):
        assert self.strategy.calculate(24) == Decimal("50.00")

    def test_fraction_over_one_day(self):
        # 25 horas → 2 diárias
        assert self.strategy.calculate(25) == Decimal("100.00")

    def test_name(self):
        assert self.strategy.name == "daily"


class TestBillingService:
    def test_default_strategy_is_hourly(self):
        svc = BillingService()
        assert svc.strategy_name == "hourly"

    def test_switch_strategy(self):
        svc = BillingService()
        svc.set_strategy(FixedBilling(Decimal("30.00")))
        assert svc.strategy_name == "fixed"
        assert svc.calculate(1.0) == Decimal("30.00")

    def test_calculate_delegates(self):
        svc = BillingService(HourlyBilling(Decimal("15.00")))
        assert svc.calculate(2.0) == Decimal("30.00")
