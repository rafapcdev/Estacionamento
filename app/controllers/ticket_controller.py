"""
Rotas da API: Tickets (Entrada e Saída)

Rotas que gerenciam o ciclo de vida completo de um veículo dentro do
estacionamento: entrada → permanência → saída com cobrança.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_entry_service, get_exit_service, get_ticket_repo
from app.schemas.ticket_schema import EntryRequest, ExitRequest, TicketResponse
from app.services.entry_service import EntryService
from app.services.exit_service import ExitService
from app.models import Vehicle, VehicleType
from app.repositories.ticket_repository import SQLAlchemyTicketRepository

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────
def _to_response(ticket) -> TicketResponse:
    return TicketResponse(
        id=ticket.id,
        vehicle_plate=ticket.vehicle_plate,
        parking_spot_id=ticket.parking_spot_id,
        entry_time=ticket.entry_time,
        exit_time=ticket.exit_time,
        amount=ticket.amount,
        is_closed=ticket.is_closed(),
    )


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────
@router.post(
    "/entry",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar entrada de veículo",
    description=(
        "Registra a entrada de um veículo. "
        "Se `spot_type` não for informado, o tipo de vaga é selecionado "
        "automaticamente de acordo com o tipo do veículo."
    ),
)
def register_entry(
    body: EntryRequest,
    service: EntryService = Depends(get_entry_service),
) -> TicketResponse:
    """
    Cria um Ticket aberto, ocupa a vaga e retorna os dados da entrada.

    O campo `vehicle_type` na request indica o tipo do veículo
    (car | motorcycle | truck) para seleção automática de vaga.
    """
    vehicle = Vehicle(plate=body.plate, vehicle_type=body.vehicle_type)
    try:
        ticket = service.register_entry(vehicle, body.spot_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return _to_response(ticket)


@router.post(
    "/exit",
    response_model=TicketResponse,
    summary="Registrar saída de veículo",
    description="Fecha o ticket, calcula o valor cobrado e libera a vaga.",
)
def register_exit(
    body: ExitRequest,
    service: ExitService = Depends(get_exit_service),
) -> TicketResponse:
    try:
        ticket = service.register_exit(body.plate)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return _to_response(ticket)


@router.get(
    "/open",
    response_model=List[TicketResponse],
    summary="Listar tickets em aberto (veículos presentes)",
)
def list_open_tickets(
    repo: SQLAlchemyTicketRepository = Depends(get_ticket_repo),
) -> List[TicketResponse]:
    return [_to_response(t) for t in repo.list_open()]


@router.get(
    "/",
    response_model=List[TicketResponse],
    summary="Listar todos os tickets",
)
def list_tickets(
    repo: SQLAlchemyTicketRepository = Depends(get_ticket_repo),
) -> List[TicketResponse]:
    return [_to_response(t) for t in repo.list_all()]


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Buscar ticket por ID",
)
def get_ticket(
    ticket_id: str,
    repo: SQLAlchemyTicketRepository = Depends(get_ticket_repo),
) -> TicketResponse:
    ticket = repo.find_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket não encontrado.")
    return _to_response(ticket)
