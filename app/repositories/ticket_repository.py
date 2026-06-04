from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Ticket

class ITicketRepository(ABC):
    @abstractmethod
    def save(self, ticket: Ticket) -> Ticket: ...
    @abstractmethod
    def find_by_id(self, ticket_id: str) -> Optional[Ticket]: ...
    @abstractmethod
    def find_open_by_plate(self, plate: str) -> Optional[Ticket]: ...
    @abstractmethod
    def list_all(self) -> List[Ticket]: ...
    @abstractmethod
    def list_open(self) -> List[Ticket]: ...
    @abstractmethod
    def update(self, ticket: Ticket) -> Ticket: ...

class SQLAlchemyTicketRepository(ITicketRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, ticket: Ticket) -> Ticket:
        self._session.add(ticket)
        self._session.commit()
        self._session.refresh(ticket)
        return ticket

    def find_by_id(self, ticket_id: str) -> Optional[Ticket]:
        return self._session.get(Ticket, ticket_id)

    def find_open_by_plate(self, plate: str) -> Optional[Ticket]:
        return (
            self._session.query(Ticket)
            .filter(Ticket.vehicle_plate == plate, Ticket.exit_time.is_(None))
            .first()
        )

    def list_all(self) -> List[Ticket]:
        return self._session.query(Ticket).all()

    def list_open(self) -> List[Ticket]:
        return self._session.query(Ticket).filter(Ticket.exit_time.is_(None)).all()

    def update(self, ticket: Ticket) -> Ticket:
        self._session.commit()
        self._session.refresh(ticket)
        return ticket
