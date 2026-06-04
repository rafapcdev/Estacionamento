"""
Tests: Domain Entities

Verifica as regras de domínio das entidades sem depender de banco de dados.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from app.domain.entities.vehicle import Vehicle, VehicleType
from app.domain.entities.parking_spot import ParkingSpot, SpotType
from app.domain.entities.ticket import Ticket
from app.domain.entities.monthly_customer import MonthlyCustomer


# ─────────────────────────────────────────────
# Vehicle
# ─────────────────────────────────────────────
class TestVehicle:
    def test_create_vehicle(self):
        v = Vehicle(plate="abc-1234", vehicle_type=VehicleType.CAR)
        assert v.plate == "ABC-1234"  # normalizado para maiúsculas
        assert v.vehicle_type == VehicleType.CAR
        assert v.id  # UUID gerado

    def test_empty_plate_raises(self):
        with pytest.raises(ValueError, match="placa"):
            Vehicle(plate="   ", vehicle_type=VehicleType.CAR)

    def test_vehicle_type_enum(self):
        assert VehicleType("motorcycle") == VehicleType.MOTORCYCLE


# ─────────────────────────────────────────────
# ParkingSpot
# ─────────────────────────────────────────────
class TestParkingSpot:
    def test_initial_state_is_available(self):
        spot = ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON)
        assert spot.is_available()
        assert not spot.occupied

    def test_occupy_and_release(self):
        spot = ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON)
        spot.occupy()
        assert spot.occupied
        spot.release()
        assert not spot.occupied

    def test_double_occupy_raises(self):
        spot = ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON)
        spot.occupy()
        with pytest.raises(ValueError, match="já está ocupada"):
            spot.occupy()

    def test_release_already_free_raises(self):
        spot = ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON)
        with pytest.raises(ValueError, match="já está livre"):
            spot.release()

    def test_spot_types(self):
        for st in SpotType:
            spot = ParkingSpot(spot_number="X-00", spot_type=st)
            assert spot.spot_type == st


# ─────────────────────────────────────────────
# Ticket
# ─────────────────────────────────────────────
class TestTicket:
    def _make_ticket(self) -> Ticket:
        return Ticket(vehicle_plate="ABC-1234", parking_spot_id="spot-uuid-123")

    def test_ticket_is_open_by_default(self):
        t = self._make_ticket()
        assert not t.is_closed()
        assert t.exit_time is None
        assert t.amount is None

    def test_close_ticket(self):
        t = self._make_ticket()
        exit_time = t.entry_time + timedelta(hours=2)
        t.close(exit_time=exit_time, amount=Decimal("20.00"))
        assert t.is_closed()
        assert t.duration_in_hours() == pytest.approx(2.0, abs=0.01)

    def test_close_twice_raises(self):
        t = self._make_ticket()
        exit_time = t.entry_time + timedelta(hours=1)
        t.close(exit_time=exit_time, amount=Decimal("10.00"))
        with pytest.raises(ValueError, match="já foi encerrado"):
            t.close(exit_time=exit_time, amount=Decimal("10.00"))

    def test_exit_before_entry_raises(self):
        t = self._make_ticket()
        bad_exit = t.entry_time - timedelta(minutes=1)
        with pytest.raises(ValueError, match="anterior"):
            t.close(exit_time=bad_exit, amount=Decimal("5.00"))

    def test_duration_open_ticket(self):
        t = self._make_ticket()
        assert t.duration_in_hours() == 0.0


# ─────────────────────────────────────────────
# MonthlyCustomer
# ─────────────────────────────────────────────
class TestMonthlyCustomer:
    def test_create_customer(self):
        c = MonthlyCustomer(name="João Silva", plate="xyz-9876")
        assert c.name == "João Silva"
        assert c.plate == "XYZ-9876"
        assert c.active

    def test_activate_deactivate(self):
        c = MonthlyCustomer(name="Maria", plate="ABC-0001")
        c.deactivate()
        assert not c.active
        c.activate()
        assert c.active

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="nome"):
            MonthlyCustomer(name="  ", plate="ABC-0001")

    def test_empty_plate_raises(self):
        with pytest.raises(ValueError, match="placa"):
            MonthlyCustomer(name="João", plate="")
