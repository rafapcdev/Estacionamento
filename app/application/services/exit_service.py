"""
Serviço de Saída de Veículos (ExitService)

Responsabilidade única: registrar a SAÍDA de um veículo.

Fluxo:
1. Localiza o ticket aberto pela placa.
2. Calcula o valor (mensalistas pagam R$ 0,00).
3. Fecha o ticket com exit_time e amount.
4. Libera a vaga.
"""

from datetime import datetime
from decimal import Decimal

from app.domain.entities.ticket import Ticket
from app.domain.repositories.parking_spot_repository import IParkingSpotRepository
from app.domain.repositories.ticket_repository import ITicketRepository
from app.application.services.billing_service import BillingService
from app.application.services.monthly_customer_service import MonthlyCustomerService


class ExitService:
    """
    Serviço de saída de veículos.

    Calcula a cobrança e libera a vaga utilizada.
    """

    def __init__(
        self,
        spot_repository: IParkingSpotRepository,
        ticket_repository: ITicketRepository,
        billing_service: BillingService,
        monthly_customer_service: MonthlyCustomerService,
    ) -> None:
        self._spots = spot_repository
        self._tickets = ticket_repository
        self._billing = billing_service
        self._monthly = monthly_customer_service

    def register_exit(self, plate: str) -> Ticket:
        """
        Registra a saída de um veículo identificado pela placa.

        Args:
            plate (str): Placa do veículo.

        Returns:
            Ticket: Ticket fechado com valor calculado.

        Raises:
            ValueError: Se não houver ticket aberto para a placa informada
                        ou se a vaga não for encontrada.
        """
        plate = plate.upper().strip()

        # 1. Localiza ticket aberto
        ticket = self._tickets.find_open_by_plate(plate)
        if not ticket:
            raise ValueError(
                f"Nenhum ticket aberto encontrado para a placa '{plate}'."
            )

        # 2. Determina o valor (mensalistas são isentos)
        exit_time = datetime.utcnow()  # noqa: DTZ003
        if self._monthly.is_monthly_customer(plate):
            amount = Decimal("0.00")
        else:
            duration = (exit_time - ticket.entry_time).total_seconds() / 3600
            amount = self._billing.calculate(duration)

        # 3. Fecha o ticket
        ticket.close(exit_time=exit_time, amount=amount)
        self._tickets.update(ticket)

        # 4. Libera a vaga
        spot = self._spots.find_by_id(ticket.parking_spot_id)
        if spot:
            spot.release()
            self._spots.update(spot)

        return ticket
