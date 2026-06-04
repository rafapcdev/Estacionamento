"""
Repositório de Tickets — SQLAlchemy (infraestrutura)
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.ticket import Ticket
from app.domain.repositories.ticket_repository import ITicketRepository
from app.infrastructure.database.models import TicketModel


class SQLAlchemyTicketRepository(ITicketRepository):
    """Repositório de tickets com persistência em PostgreSQL via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------ #
    # Mapeamentos
    # ------------------------------------------------------------------ #
    @staticmethod
    def _to_entity(model: TicketModel) -> Ticket:
        ticket = Ticket.__new__(Ticket)
        ticket.id = model.id
        ticket.vehicle_plate = model.vehicle_plate
        ticket.parking_spot_id = model.parking_spot_id
        ticket.entry_time = model.entry_time
        ticket.exit_time = model.exit_time
        ticket.amount = Decimal(str(model.amount)) if model.amount is not None else None
        return ticket

    @staticmethod
    def _to_model(ticket: Ticket) -> TicketModel:
        return TicketModel(
            id=ticket.id,
            vehicle_plate=ticket.vehicle_plate,
            parking_spot_id=ticket.parking_spot_id,
            entry_time=ticket.entry_time,
            exit_time=ticket.exit_time,
            amount=ticket.amount,
        )

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    def save(self, ticket: Ticket) -> Ticket:
        model = self._to_model(ticket)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, ticket_id: str) -> Optional[Ticket]:
        model = self._session.get(TicketModel, ticket_id)
        return self._to_entity(model) if model else None

    def find_open_by_plate(self, plate: str) -> Optional[Ticket]:
        model = (
            self._session.query(TicketModel)
            .filter(
                TicketModel.vehicle_plate == plate.upper(),
                TicketModel.exit_time.is_(None),
            )
            .first()
        )
        return self._to_entity(model) if model else None

    def list_all(self) -> List[Ticket]:
        return [self._to_entity(m) for m in self._session.query(TicketModel).all()]

    def list_open(self) -> List[Ticket]:
        models = (
            self._session.query(TicketModel)
            .filter(TicketModel.exit_time.is_(None))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def update(self, ticket: Ticket) -> Ticket:
        model = self._session.get(TicketModel, ticket.id)
        if not model:
            raise ValueError(f"Ticket com ID '{ticket.id}' não encontrado.")
        model.exit_time = ticket.exit_time
        model.amount = ticket.amount
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)
