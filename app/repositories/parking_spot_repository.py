from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import ParkingSpot, SpotType

class IParkingSpotRepository(ABC):
    @abstractmethod
    def save(self, spot: ParkingSpot) -> ParkingSpot: ...
    @abstractmethod
    def find_by_id(self, spot_id: str) -> Optional[ParkingSpot]: ...
    @abstractmethod
    def find_by_number(self, spot_number: str) -> Optional[ParkingSpot]: ...
    @abstractmethod
    def find_available_by_type(self, spot_type: SpotType) -> Optional[ParkingSpot]: ...
    @abstractmethod
    def lock_available_by_type(self, spot_type: SpotType) -> Optional[ParkingSpot]: ...
    @abstractmethod
    def list_all(self) -> List[ParkingSpot]: ...
    @abstractmethod
    def list_available(self) -> List[ParkingSpot]: ...
    @abstractmethod
    def update(self, spot: ParkingSpot) -> ParkingSpot: ...
    @abstractmethod
    def delete(self, spot_id: str) -> bool: ...

class SQLAlchemyParkingSpotRepository(IParkingSpotRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, spot: ParkingSpot) -> ParkingSpot:
        self._session.add(spot)
        self._session.commit()
        self._session.refresh(spot)
        return spot

    def find_by_id(self, spot_id: str) -> Optional[ParkingSpot]:
        return self._session.get(ParkingSpot, spot_id)

    def find_by_number(self, spot_number: str) -> Optional[ParkingSpot]:
        return self._session.query(ParkingSpot).filter(ParkingSpot.spot_number == spot_number).first()

    def find_available_by_type(self, spot_type: SpotType) -> Optional[ParkingSpot]:
        return (
            self._session.query(ParkingSpot)
            .filter(ParkingSpot.spot_type == spot_type, ParkingSpot.occupied.is_(False))
            .first()
        )

    def lock_available_by_type(self, spot_type: SpotType) -> Optional[ParkingSpot]:
        query = (
            self._session.query(ParkingSpot)
            .filter(ParkingSpot.spot_type == spot_type, ParkingSpot.occupied.is_(False))
        )
        try:
            dialect = self._session.get_bind().dialect.name
        except Exception:
            dialect = "sqlite"

        if dialect == "postgresql":
            query = query.with_for_update(skip_locked=True)

        return query.first()

    def list_all(self) -> List[ParkingSpot]:
        return self._session.query(ParkingSpot).all()

    def list_available(self) -> List[ParkingSpot]:
        return self._session.query(ParkingSpot).filter(ParkingSpot.occupied.is_(False)).all()

    def update(self, spot: ParkingSpot) -> ParkingSpot:
        self._session.commit()
        self._session.refresh(spot)
        return spot

    def delete(self, spot_id: str) -> bool:
        spot = self._session.get(ParkingSpot, spot_id)
        if not spot:
            return False
        self._session.delete(spot)
        self._session.commit()
        return True
