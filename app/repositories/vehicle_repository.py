from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Vehicle

class IVehicleRepository(ABC):
    @abstractmethod
    def save(self, vehicle: Vehicle) -> Vehicle: ...
    @abstractmethod
    def find_by_plate(self, plate: str) -> Optional[Vehicle]: ...
    @abstractmethod
    def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]: ...
    @abstractmethod
    def list_all(self) -> List[Vehicle]: ...
    @abstractmethod
    def delete(self, vehicle_id: str) -> bool: ...

class SQLAlchemyVehicleRepository(IVehicleRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, vehicle: Vehicle) -> Vehicle:
        self._session.add(vehicle)
        self._session.commit()
        self._session.refresh(vehicle)
        return vehicle

    def find_by_plate(self, plate: str) -> Optional[Vehicle]:
        return self._session.query(Vehicle).filter(Vehicle.plate == plate).first()

    def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        return self._session.get(Vehicle, vehicle_id)

    def list_all(self) -> List[Vehicle]:
        return self._session.query(Vehicle).all()

    def delete(self, vehicle_id: str) -> bool:
        vehicle = self._session.get(Vehicle, vehicle_id)
        if not vehicle:
            return False
        self._session.delete(vehicle)
        self._session.commit()
        return True
