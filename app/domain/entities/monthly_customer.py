"""
Entidade de Domínio: Mensalista

Representa um cliente mensalista do estacionamento.
"""

import uuid
from dataclasses import dataclass, field


@dataclass
class MonthlyCustomer:
    """
    Entidade de domínio para clientes com plano mensal.

    Atributos:
        id (str):     Identificador único (UUID).
        name (str):   Nome completo do cliente.
        plate (str):  Placa do veículo cadastrado.
        active (bool): Indica se o plano está ativo.
    """

    name: str
    plate: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    active: bool = True

    def __post_init__(self) -> None:
        self._validate()

    # ------------------------------------------------------------------ #
    # Validações e regras de domínio
    # ------------------------------------------------------------------ #
    def _validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("O nome do mensalista não pode estar vazio.")
        if not self.plate or not self.plate.strip():
            raise ValueError("A placa não pode estar vazia.")
        self.plate = self.plate.upper().strip()
        self.name = self.name.strip()

    def activate(self) -> None:
        """Ativa o plano mensal."""
        self.active = True

    def deactivate(self) -> None:
        """Desativa o plano mensal."""
        self.active = False

    def __repr__(self) -> str:  # pragma: no cover
        status = "ativo" if self.active else "inativo"
        return (
            f"MonthlyCustomer(name={self.name!r}, "
            f"plate={self.plate!r}, status={status})"
        )
