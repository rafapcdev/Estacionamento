"""
Repositório de Vagas — SQLAlchemy (infraestrutura)
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.parking_spot import ParkingSpot, SpotType
from app.domain.repositories.parking_spot_repository import IParkingSpotRepository
from app.infrastructure.database.models import ParkingSpotModel


class SQLAlchemyParkingSpotRepository(IParkingSpotRepository):
    """Repositório de vagas com persistência em PostgreSQL via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------ #
    # Mapeamentos
    # ------------------------------------------------------------------ #
    @staticmethod
    def _to_entity(model: ParkingSpotModel) -> ParkingSpot:
        spot = ParkingSpot.__new__(ParkingSpot)
        spot.id = model.id
        spot.spot_number = model.spot_number
        spot.spot_type = SpotType(model.spot_type)
        spot.occupied = model.occupied
        return spot

    @staticmethod
    def _to_model(spot: ParkingSpot) -> ParkingSpotModel:
        return ParkingSpotModel(
            id=spot.id,
            spot_number=spot.spot_number,
            spot_type=spot.spot_type.value,
            occupied=spot.occupied,
        )

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    def save(self, spot: ParkingSpot) -> ParkingSpot:
        model = self._to_model(spot)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, spot_id: str) -> Optional[ParkingSpot]:
        model = self._session.get(ParkingSpotModel, spot_id)
        return self._to_entity(model) if model else None

    def find_by_number(self, spot_number: str) -> Optional[ParkingSpot]:
        model = (
            self._session.query(ParkingSpotModel)
            .filter(ParkingSpotModel.spot_number == spot_number)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_available_by_type(self, spot_type: SpotType) -> Optional[ParkingSpot]:
        model = (
            self._session.query(ParkingSpotModel)
            .filter(
                ParkingSpotModel.spot_type == spot_type.value,
                ParkingSpotModel.occupied.is_(False),
            )
            .first()
        )
        return self._to_entity(model) if model else None

    def lock_available_by_type(self, spot_type: SpotType) -> Optional[ParkingSpot]:
        """
        Busca e trava atomicamente a primeira vaga livre via SELECT FOR UPDATE SKIP LOCKED.

        - PostgreSQL: aplica SKIP LOCKED — transações concorrentes recebem vagas diferentes.
        - SQLite (testes): executa sem o lock (SQLite não suporta SKIP LOCKED).
        """
        query = (
            self._session.query(ParkingSpotModel)
            .filter(
                ParkingSpotModel.spot_type == spot_type.value,
                ParkingSpotModel.occupied.is_(False),
            )
        )
        try:
            dialect = self._session.get_bind().dialect.name
        except Exception:
            dialect = "sqlite"

        if dialect == "postgresql":
            query = query.with_for_update(skip_locked=True)

        model = query.first()
        return self._to_entity(model) if model else None

    def list_all(self) -> List[ParkingSpot]:
        return [self._to_entity(m) for m in self._session.query(ParkingSpotModel).all()]

    def list_available(self) -> List[ParkingSpot]:
        models = (
            self._session.query(ParkingSpotModel)
            .filter(ParkingSpotModel.occupied.is_(False))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def update(self, spot: ParkingSpot) -> ParkingSpot:
        model = self._session.get(ParkingSpotModel, spot.id)
        if not model:
            raise ValueError(f"Vaga com ID '{spot.id}' não encontrada.")
        model.spot_number = spot.spot_number
        model.spot_type = spot.spot_type.value
        model.occupied = spot.occupied
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, spot_id: str) -> bool:
        model = self._session.get(ParkingSpotModel, spot_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True
