"""
Interfaces de Repositório (domínio)

Contratos (interfaces) para todos os repositórios.
A camada de domínio NÃO conhece detalhes de banco de dados —
apenas define o que precisa. (DIP — Dependency Inversion Principle)
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.vehicle import Vehicle


class IVehicleRepository(ABC):
    """Interface para persistência de Vehicle."""

    @abstractmethod
    def save(self, vehicle: Vehicle) -> Vehicle:
        """Persiste um novo veículo e retorna a entidade salva."""
        ...

    @abstractmethod
    def find_by_plate(self, plate: str) -> Optional[Vehicle]:
        """Busca um veículo pela placa. Retorna None se não encontrado."""
        ...

    @abstractmethod
    def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """Busca um veículo pelo ID."""
        ...

    @abstractmethod
    def list_all(self) -> List[Vehicle]:
        """Retorna todos os veículos cadastrados."""
        ...

    @abstractmethod
    def delete(self, vehicle_id: str) -> bool:
        """Remove um veículo pelo ID. Retorna True se removido."""
        ...
