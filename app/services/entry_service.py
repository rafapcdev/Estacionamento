"""
Serviço de Entrada de Veículos (EntryService)

Responsabilidade única: registrar a ENTRADA de um veículo.

Fluxo:
1. Verifica se o veículo já está no estacionamento.
2. Verifica se é mensalista (isento de cobrança normal).
3. Localiza uma vaga disponível compatível com o tipo de veículo.
4. Ocupa a vaga e cria o Ticket.
"""

from app.models import SpotType
from app.models import Ticket
from app.models import Vehicle, VehicleType
from app.repositories.parking_spot_repository import IParkingSpotRepository
from app.repositories.ticket_repository import ITicketRepository
from app.services.monthly_customer_service import MonthlyCustomerService


# Mapa: tipo de veículo → tipo de vaga preferencial
_VEHICLE_TO_SPOT: dict[VehicleType, SpotType] = {
    VehicleType.MOTORCYCLE: SpotType.MOTORCYCLE,
    VehicleType.CAR: SpotType.COMMON,
    VehicleType.TRUCK: SpotType.COMMON,
}


class EntryService:
    """
    Serviço de entrada de veículos.

    Injetado com repositórios e serviço de mensalistas
    (sem depender de implementações concretas).
    """

    def __init__(
        self,
        spot_repository: IParkingSpotRepository,
        ticket_repository: ITicketRepository,
        monthly_customer_service: MonthlyCustomerService,
    ) -> None:
        self._spots = spot_repository
        self._tickets = ticket_repository
        self._monthly = monthly_customer_service

    def register_entry(self, vehicle: Vehicle, spot_type: SpotType | None = None) -> Ticket:
        """
        Registra a entrada de um veículo.

        Args:
            vehicle:    Entidade do veículo que está entrando.
            spot_type:  Tipo de vaga desejado (None = automático por tipo de veículo).

        Returns:
            Ticket: Ticket aberto com hora de entrada.

        Raises:
            ValueError: Se o veículo já estiver dentro ou não houver vaga disponível.
        """
        # 1. Verifica se já existe ticket aberto para esta placa
        open_ticket = self._tickets.find_open_by_plate(vehicle.plate)
        if open_ticket:
            raise ValueError(
                f"O veículo '{vehicle.plate}' já está no estacionamento "
                f"(ticket: {open_ticket.id})."
            )

        # 2. Determina o tipo de vaga
        preferred_type = spot_type or _VEHICLE_TO_SPOT.get(vehicle.vehicle_type, SpotType.COMMON)

        # 3. Localiza e trava atomicamente uma vaga disponível (SKIP LOCKED no PostgreSQL)
        spot = self._spots.lock_available_by_type(preferred_type)
        if spot is None:
            # Tenta vaga comum como fallback (exceto para motos)
            if preferred_type != SpotType.COMMON:
                spot = self._spots.lock_available_by_type(SpotType.COMMON)
            if spot is None:
                raise ValueError(
                    f"Não há vagas disponíveis do tipo '{preferred_type.value}'."
                )

        # 4. Ocupa a vaga
        spot.occupy()
        self._spots.update(spot)

        # 5. Cria e persiste o ticket
        ticket = Ticket(
            vehicle_plate=vehicle.plate,
            parking_spot_id=spot.id,
        )
        return self._tickets.save(ticket)
