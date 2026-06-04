"""
Serviço de Vagas (ParkingSpotService)

Responsabilidade: gerenciar o ciclo de vida das vagas de estacionamento.
"""

from typing import List, Optional

from app.domain.entities.parking_spot import ParkingSpot, SpotType
from app.domain.repositories.parking_spot_repository import IParkingSpotRepository


class ParkingSpotService:
    """
    Serviço de vagas.

    Operações: criar, listar, buscar e remover vagas.
    Não tem conhecimento de banco de dados — usa a interface do repositório.
    """

    def __init__(self, spot_repository: IParkingSpotRepository) -> None:
        self._repo = spot_repository

    # ------------------------------------------------------------------ #
    # Criação
    # ------------------------------------------------------------------ #
    def create_spot(self, spot_number: str, spot_type: SpotType) -> ParkingSpot:
        """
        Cria e persiste uma nova vaga.

        Args:
            spot_number: Número/identificação visual da vaga.
            spot_type:   Categoria da vaga.

        Returns:
            ParkingSpot: Entidade persistida.

        Raises:
            ValueError: Se já existir uma vaga com o mesmo número.
        """
        existing = self._repo.find_by_number(spot_number)
        if existing:
            raise ValueError(f"Já existe uma vaga com o número '{spot_number}'.")
        spot = ParkingSpot(spot_number=spot_number, spot_type=spot_type)
        return self._repo.save(spot)

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    def get_spot_by_id(self, spot_id: str) -> Optional[ParkingSpot]:
        return self._repo.find_by_id(spot_id)

    def get_spot_by_number(self, spot_number: str) -> Optional[ParkingSpot]:
        return self._repo.find_by_number(spot_number)

    def list_all_spots(self) -> List[ParkingSpot]:
        return self._repo.list_all()

    def list_available_spots(self) -> List[ParkingSpot]:
        return self._repo.list_available()

    def find_available_spot(self, spot_type: SpotType) -> Optional[ParkingSpot]:
        """Retorna a primeira vaga livre do tipo solicitado."""
        return self._repo.find_available_by_type(spot_type)

    # ------------------------------------------------------------------ #
    # Remoção
    # ------------------------------------------------------------------ #
    def delete_spot(self, spot_id: str) -> bool:
        spot = self._repo.find_by_id(spot_id)
        if not spot:
            raise ValueError("Vaga não encontrada.")
        if spot.occupied:
            raise ValueError("Não é possível remover uma vaga ocupada.")
        return self._repo.delete(spot_id)
