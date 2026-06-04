"""
Entidade de Domínio: Ticket

Representa o comprovante de uso de uma vaga — da entrada à saída.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Ticket:
    """
    Entidade de domínio que registra a permanência de um veículo.

    Atributos:
        id (str):              Identificador único (UUID).
        vehicle_plate (str):   Placa do veículo associado.
        parking_spot_id (str): Referência à vaga utilizada.
        entry_time (datetime): Momento de entrada.
        exit_time (datetime | None): Momento de saída (None se ainda no local).
        amount (Decimal | None): Valor cobrado (None até o fechamento).
    """

    vehicle_plate: str
    parking_spot_id: str
    entry_time: datetime = field(default_factory=datetime.utcnow)  # noqa: DTZ003
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exit_time: Optional[datetime] = None
    amount: Optional[Decimal] = None

    # ------------------------------------------------------------------ #
    # Regras de domínio
    # ------------------------------------------------------------------ #
    def close(self, exit_time: datetime, amount: Decimal) -> None:
        """
        Fecha o ticket registrando saída e valor cobrado.

        Raises:
            ValueError: Se o ticket já estiver fechado ou a saída for
                        anterior à entrada.
        """
        if self.is_closed():
            raise ValueError("Este ticket já foi encerrado.")
        if exit_time < self.entry_time:
            raise ValueError("A saída não pode ser anterior à entrada.")
        self.exit_time = exit_time
        self.amount = amount

    def is_closed(self) -> bool:
        """Retorna True se o ticket já tiver sido encerrado."""
        return self.exit_time is not None

    def duration_in_hours(self) -> float:
        """
        Calcula a duração da permanência em horas.

        Returns:
            float: Horas de permanência; 0 se o ticket ainda estiver aberto.
        """
        if not self.is_closed():
            return 0.0
        delta = self.exit_time - self.entry_time  # type: ignore[operator]
        return delta.total_seconds() / 3600

    def __repr__(self) -> str:  # pragma: no cover
        status = "fechado" if self.is_closed() else "aberto"
        return (
            f"Ticket(id={self.id!r}, plate={self.vehicle_plate!r}, "
            f"spot={self.parking_spot_id!r}, status={status})"
        )
