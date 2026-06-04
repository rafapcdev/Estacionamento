from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.parking_spot import ParkingSpot, SpotType


class IParkingSpotRepository(ABC):
    """Interface para persistência de ParkingSpot."""

    @abstractmethod
    def save(self, spot: ParkingSpot) -> ParkingSpot:
        """Persiste uma nova vaga."""
        ...

    @abstractmethod
    def find_by_id(self, spot_id: str) -> Optional[ParkingSpot]:
        """Busca uma vaga pelo ID."""
        ...

    @abstractmethod
    def find_by_number(self, spot_number: str) -> Optional[ParkingSpot]:
        """Busca uma vaga pelo número identificador."""
        ...

    @abstractmethod
    def find_available_by_type(self, spot_type: SpotType) -> Optional[ParkingSpot]:
        """Retorna a primeira vaga disponível do tipo especificado."""
        ...

    @abstractmethod
    def lock_available_by_type(self, spot_type: SpotType) -> Optional[ParkingSpot]:
        """
        Busca e trava atomicamente a primeira vaga disponível do tipo especificado.

        Em PostgreSQL usa SELECT FOR UPDATE SKIP LOCKED — garante que duas
        transações simultâneas nunca recebam a mesma vaga.
        Em outros bancos (ex.: SQLite nos testes) executa sem o lock.

        Retorna None se não houver vaga disponível.
        """
        ...

    @abstractmethod
    def list_all(self) -> List[ParkingSpot]:
        """Lista todas as vagas."""
        ...

    @abstractmethod
    def list_available(self) -> List[ParkingSpot]:
        """Lista apenas as vagas disponíveis (não ocupadas)."""
        ...

    @abstractmethod
    def update(self, spot: ParkingSpot) -> ParkingSpot:
        """Atualiza os dados de uma vaga existente."""
        ...

    @abstractmethod
    def delete(self, spot_id: str) -> bool:
        """Remove uma vaga pelo ID."""
        ...
