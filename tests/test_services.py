"""
Tests: EntryService e ExitService (integração com SQLite em memória)

Verifica o fluxo completo: entrada → permanência → saída com cobrança.
"""

import pytest
from decimal import Decimal

from app.models import Vehicle, VehicleType
from app.models import ParkingSpot, SpotType


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _create_spot(spot_repo, number="A-01", spot_type=SpotType.COMMON) -> ParkingSpot:
    spot = ParkingSpot(spot_number=number, spot_type=spot_type)
    return spot_repo.save(spot)


def _make_car(plate="ABC-1234") -> Vehicle:
    return Vehicle(plate=plate, vehicle_type=VehicleType.CAR)


def _make_moto(plate="MOT-0001") -> Vehicle:
    return Vehicle(plate=plate, vehicle_type=VehicleType.MOTORCYCLE)


# ─────────────────────────────────────────────
# EntryService
# ─────────────────────────────────────────────
class TestEntryService:
    def test_register_entry_creates_ticket(self, entry_service, spot_repo):
        _create_spot(spot_repo)
        vehicle = _make_car()
        ticket = entry_service.register_entry(vehicle)
        assert ticket.vehicle_plate == "ABC-1234"
        assert not ticket.is_closed()
        assert ticket.exit_time is None

    def test_entry_occupies_spot(self, entry_service, spot_repo):
        spot = _create_spot(spot_repo)
        vehicle = _make_car()
        entry_service.register_entry(vehicle)
        updated = spot_repo.find_by_id(spot.id)
        assert updated.occupied

    def test_entry_same_vehicle_twice_raises(self, entry_service, spot_repo):
        _create_spot(spot_repo, "A-01")
        _create_spot(spot_repo, "A-02")
        vehicle = _make_car()
        entry_service.register_entry(vehicle)
        with pytest.raises(ValueError, match="já está no estacionamento"):
            entry_service.register_entry(vehicle)

    def test_no_available_spot_raises(self, entry_service, spot_repo):
        # Nenhuma vaga cadastrada
        with pytest.raises(ValueError, match="vagas disponíveis"):
            entry_service.register_entry(_make_car())

    def test_motorcycle_uses_motorcycle_spot(self, entry_service, spot_repo, ticket_repo):
        moto_spot = _create_spot(spot_repo, "M-01", SpotType.MOTORCYCLE)
        vehicle = _make_moto()
        ticket = entry_service.register_entry(vehicle)
        assert ticket.parking_spot_id == moto_spot.id

    def test_monthly_customer_can_enter(
        self, entry_service, spot_repo, monthly_service
    ):
        _create_spot(spot_repo)
        monthly_service.register("João", "ABC-1234")
        vehicle = _make_car("ABC-1234")
        ticket = entry_service.register_entry(vehicle)
        assert ticket.vehicle_plate == "ABC-1234"


# ─────────────────────────────────────────────
# ExitService
# ─────────────────────────────────────────────
class TestExitService:
    def test_exit_closes_ticket_with_amount(
        self, entry_service, exit_service, spot_repo
    ):
        _create_spot(spot_repo)
        entry_service.register_entry(_make_car())
        ticket = exit_service.register_exit("ABC-1234")
        assert ticket.is_closed()
        assert ticket.amount is not None
        assert ticket.amount >= Decimal("0.00")

    def test_exit_releases_spot(self, entry_service, exit_service, spot_repo):
        spot = _create_spot(spot_repo)
        entry_service.register_entry(_make_car())
        exit_service.register_exit("ABC-1234")
        updated = spot_repo.find_by_id(spot.id)
        assert not updated.occupied

    def test_exit_without_entry_raises(self, exit_service):
        with pytest.raises(ValueError, match="Nenhum ticket aberto"):
            exit_service.register_exit("XYZ-9999")

    def test_monthly_customer_charged_zero(
        self, entry_service, exit_service, spot_repo, monthly_service
    ):
        _create_spot(spot_repo)
        monthly_service.register("Maria", "ABC-1234")
        entry_service.register_entry(_make_car("ABC-1234"))
        ticket = exit_service.register_exit("ABC-1234")
        assert ticket.amount == Decimal("0.00")
