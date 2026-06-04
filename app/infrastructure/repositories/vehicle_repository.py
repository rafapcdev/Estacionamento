"""
Repositório de Veículos — SQLAlchemy (infraestrutura)

Implementação concreta da interface IVehicleRepository usando SQLAlchemy 2.x.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.vehicle import Vehicle, VehicleType
from app.domain.repositories.vehicle_repository import IVehicleRepository
from app.infrastructure.database.models import VehicleModel


class SQLAlchemyVehicleRepository(IVehicleRepository):
    """Repositório de veículos com persistência em PostgreSQL via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------ #
    # Helpers de mapeamento (Model ↔ Entity)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _to_entity(model: VehicleModel) -> Vehicle:
        vehicle = Vehicle.__new__(Vehicle)
        vehicle.id = model.id
        vehicle.plate = model.plate
        vehicle.vehicle_type = VehicleType(model.vehicle_type)
        return vehicle

    @staticmethod
    def _to_model(vehicle: Vehicle) -> VehicleModel:
        return VehicleModel(
            id=vehicle.id,
            plate=vehicle.plate,
            vehicle_type=vehicle.vehicle_type.value,
        )

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    def save(self, vehicle: Vehicle) -> Vehicle:
        model = self._to_model(vehicle)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_plate(self, plate: str) -> Optional[Vehicle]:
        model = (
            self._session.query(VehicleModel)
            .filter(VehicleModel.plate == plate.upper())
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        model = self._session.get(VehicleModel, vehicle_id)
        return self._to_entity(model) if model else None

    def list_all(self) -> List[Vehicle]:
        models = self._session.query(VehicleModel).all()
        return [self._to_entity(m) for m in models]

    def delete(self, vehicle_id: str) -> bool:
        model = self._session.get(VehicleModel, vehicle_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True
