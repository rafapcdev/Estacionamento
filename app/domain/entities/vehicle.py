"""
Entidade de Domínio: Veículo

Representa um veículo no sistema de estacionamento.
Segue o princípio SRP: esta classe apenas descreve um veículo,
sem lógica de persistência ou de negócio externo.
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum


class VehicleType(str, Enum):
    """Tipos de veículo suportados pelo sistema."""

    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"


@dataclass
class Vehicle:
    """
    Entidade de domínio que representa um veículo.

    Atributos:
        id (str):           Identificador único (UUID).
        plate (str):        Placa do veículo (ex.: "ABC-1234").
        vehicle_type (VehicleType): Tipo do veículo.
    """

    plate: str
    vehicle_type: VehicleType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        self._validate()

    # ------------------------------------------------------------------ #
    # Validações internas (regras de domínio simples)
    # ------------------------------------------------------------------ #
    def _validate(self) -> None:
        if not self.plate or not self.plate.strip():
            raise ValueError("A placa do veículo não pode estar vazia.")
        self.plate = self.plate.upper().strip()

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Vehicle(id={self.id!r}, plate={self.plate!r}, "
            f"vehicle_type={self.vehicle_type.value!r})"
        )
