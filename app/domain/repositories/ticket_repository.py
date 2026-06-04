from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.ticket import Ticket


class ITicketRepository(ABC):
    """Interface para persistência de Ticket."""

    @abstractmethod
    def save(self, ticket: Ticket) -> Ticket:
        """Persiste um novo ticket (abertura de vaga)."""
        ...

    @abstractmethod
    def find_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """Busca um ticket pelo ID."""
        ...

    @abstractmethod
    def find_open_by_plate(self, plate: str) -> Optional[Ticket]:
        """
        Retorna o ticket aberto (sem exit_time) para a placa informada.
        Retorna None se o veículo não estiver no estacionamento.
        """
        ...

    @abstractmethod
    def list_all(self) -> List[Ticket]:
        """Lista todos os tickets."""
        ...

    @abstractmethod
    def list_open(self) -> List[Ticket]:
        """Lista todos os tickets em aberto."""
        ...

    @abstractmethod
    def update(self, ticket: Ticket) -> Ticket:
        """Atualiza um ticket existente (ex.: ao registrar saída)."""
        ...
