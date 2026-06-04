"""
Entidade de Domínio: Vaga de Estacionamento

Representa uma vaga de estacionamento.
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum


class SpotType(str, Enum):
    """Categorias de vagas disponíveis no estacionamento."""

    COMMON = "common"          # Vaga comum
    ELDERLY = "elderly"        # Idosos
    PCD = "pcd"                # Pessoa com Deficiência
    MOTORCYCLE = "motorcycle"  # Motocicletas


@dataclass
class ParkingSpot:
    """
    Entidade de domínio que representa uma vaga de estacionamento.

    Atributos:
        id (str):            Identificador único (UUID).
        spot_number (str):   Identificação visual da vaga (ex.: "A-01").
        spot_type (SpotType): Categoria da vaga.
        occupied (bool):     Indica se a vaga está ocupada.
    """

    spot_number: str
    spot_type: SpotType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occupied: bool = False

    def occupy(self) -> None:
        """Marca a vaga como ocupada."""
        if self.occupied:
            raise ValueError(f"A vaga {self.spot_number} já está ocupada.")
        self.occupied = True

    def release(self) -> None:
        """Libera a vaga."""
        if not self.occupied:
            raise ValueError(f"A vaga {self.spot_number} já está livre.")
        self.occupied = False

    def is_available(self) -> bool:
        """Retorna True se a vaga estiver disponível."""
        return not self.occupied

    def __repr__(self) -> str:  # pragma: no cover
        status = "ocupada" if self.occupied else "livre"
        return (
            f"ParkingSpot(number={self.spot_number!r}, "
            f"type={self.spot_type.value!r}, status={status})"
        )
