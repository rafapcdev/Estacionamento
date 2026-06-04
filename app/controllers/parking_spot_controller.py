"""
Rotas da API: Vagas de Estacionamento

Gerenciamento de vagas de estacionamento.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_spot_service
from app.schemas.parking_spot_schema import ParkingSpotCreateRequest, ParkingSpotResponse
from app.services.parking_spot_service import ParkingSpotService

router = APIRouter(prefix="/spots", tags=["Vagas"])


def _to_response(spot) -> ParkingSpotResponse:
    return ParkingSpotResponse(
        id=spot.id,
        spot_number=spot.spot_number,
        spot_type=spot.spot_type,
        occupied=spot.occupied,
    )


@router.post(
    "/",
    response_model=ParkingSpotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar vaga",
)
def create_spot(
    body: ParkingSpotCreateRequest,
    service: ParkingSpotService = Depends(get_spot_service),
) -> ParkingSpotResponse:
    """Cadastra uma nova vaga de estacionamento."""
    try:
        spot = service.create_spot(body.spot_number, body.spot_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return _to_response(spot)


@router.get(
    "/",
    response_model=List[ParkingSpotResponse],
    summary="Listar todas as vagas",
)
def list_spots(
    service: ParkingSpotService = Depends(get_spot_service),
) -> List[ParkingSpotResponse]:
    return [_to_response(s) for s in service.list_all_spots()]


@router.get(
    "/available",
    response_model=List[ParkingSpotResponse],
    summary="Listar vagas disponíveis",
)
def list_available(
    service: ParkingSpotService = Depends(get_spot_service),
) -> List[ParkingSpotResponse]:
    return [_to_response(s) for s in service.list_available_spots()]


@router.get(
    "/{spot_id}",
    response_model=ParkingSpotResponse,
    summary="Buscar vaga por ID",
)
def get_spot(
    spot_id: str,
    service: ParkingSpotService = Depends(get_spot_service),
) -> ParkingSpotResponse:
    spot = service.get_spot_by_id(spot_id)
    if not spot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaga não encontrada.")
    return _to_response(spot)


@router.delete(
    "/{spot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover vaga",
)
def delete_spot(
    spot_id: str,
    service: ParkingSpotService = Depends(get_spot_service),
) -> None:
    try:
        service.delete_spot(spot_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
