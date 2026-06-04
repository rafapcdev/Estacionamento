"""
Tests: MonthlyCustomerService
"""

import pytest
from app.application.services.monthly_customer_service import MonthlyCustomerService


class TestMonthlyCustomerService:
    def test_register_customer(self, monthly_service):
        c = monthly_service.register("João Silva", "abc-1234")
        assert c.name == "João Silva"
        assert c.plate == "ABC-1234"
        assert c.active

    def test_register_duplicate_active_plate_raises(self, monthly_service):
        monthly_service.register("João", "ABC-1234")
        with pytest.raises(ValueError, match="já está cadastrada"):
            monthly_service.register("Maria", "abc-1234")

    def test_is_monthly_customer_active(self, monthly_service):
        monthly_service.register("João", "ABC-1234")
        assert monthly_service.is_monthly_customer("ABC-1234")

    def test_is_not_monthly_customer(self, monthly_service):
        assert not monthly_service.is_monthly_customer("XYZ-9999")

    def test_deactivate_customer(self, monthly_service):
        c = monthly_service.register("João", "ABC-1234")
        monthly_service.deactivate(c.id)
        assert not monthly_service.is_monthly_customer("ABC-1234")

    def test_activate_customer(self, monthly_service):
        c = monthly_service.register("João", "ABC-1234")
        monthly_service.deactivate(c.id)
        monthly_service.activate(c.id)
        assert monthly_service.is_monthly_customer("ABC-1234")

    def test_list_active(self, monthly_service):
        monthly_service.register("João", "AAA-0001")
        c2 = monthly_service.register("Maria", "BBB-0002")
        monthly_service.deactivate(c2.id)
        actives = monthly_service.list_active()
        plates = [c.plate for c in actives]
        assert "AAA-0001" in plates
        assert "BBB-0002" not in plates

    def test_get_not_found_returns_none(self, monthly_service):
        assert monthly_service.get_by_id("nonexistent-id") is None
