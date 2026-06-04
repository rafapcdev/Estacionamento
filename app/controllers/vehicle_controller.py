"""
Rotas da API: Veículos

CRUD de veículos.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_vehicle_repo, get_spot_service
from app.schemas.vehicle_schema import VehicleCreateRequest, VehicleResponse
from app.models import Vehicle
from app.repositories.vehicle_repository import SQLAlchemyVehicleRepository

router = APIRouter(prefix="/vehicles", tags=["Veículos"])


@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar veículo",
)
def create_vehicle(
    body: VehicleCreateRequest,
    repo: SQLAlchemyVehicleRepository = Depends(get_vehicle_repo),
) -> VehicleResponse:
    """Cadastra um novo veículo no sistema."""
    existing = repo.find_by_plate(body.plate)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Veículo com placa '{body.plate}' já cadastrado.",
        )
    vehicle = Vehicle(plate=body.plate, vehicle_type=body.vehicle_type)
    saved = repo.save(vehicle)
    return VehicleResponse(id=saved.id, plate=saved.plate, vehicle_type=saved.vehicle_type)


@router.get(
    "/",
    response_model=List[VehicleResponse],
    summary="Listar veículos",
)
def list_vehicles(
    repo: SQLAlchemyVehicleRepository = Depends(get_vehicle_repo),
) -> List[VehicleResponse]:
    """Retorna todos os veículos cadastrados."""
    vehicles = repo.list_all()
    return [
        VehicleResponse(id=v.id, plate=v.plate, vehicle_type=v.vehicle_type)
        for v in vehicles
    ]


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Buscar veículo por ID",
)
def get_vehicle(
    vehicle_id: str,
    repo: SQLAlchemyVehicleRepository = Depends(get_vehicle_repo),
) -> VehicleResponse:
    """Retorna um veículo pelo seu ID."""
    vehicle = repo.find_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    return VehicleResponse(id=vehicle.id, plate=vehicle.plate, vehicle_type=vehicle.vehicle_type)


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover veículo",
)
def delete_vehicle(
    vehicle_id: str,
    repo: SQLAlchemyVehicleRepository = Depends(get_vehicle_repo),
) -> None:
    """Remove um veículo pelo ID."""
    removed = repo.delete(vehicle_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
