"""
Rotas da API: Mensalistas
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_monthly_service
from app.schemas.monthly_customer_schema import (
    MonthlyCustomerCreateRequest,
    MonthlyCustomerResponse,
)
from app.services.monthly_customer_service import MonthlyCustomerService

router = APIRouter(prefix="/monthly-customers", tags=["Mensalistas"])


def _to_response(c) -> MonthlyCustomerResponse:
    return MonthlyCustomerResponse(id=c.id, name=c.name, plate=c.plate, active=c.active)


@router.post(
    "/",
    response_model=MonthlyCustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar mensalista",
)
def create_monthly_customer(
    body: MonthlyCustomerCreateRequest,
    service: MonthlyCustomerService = Depends(get_monthly_service),
) -> MonthlyCustomerResponse:
    try:
        customer = service.register(body.name, body.plate)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return _to_response(customer)


@router.get(
    "/",
    response_model=List[MonthlyCustomerResponse],
    summary="Listar mensalistas",
)
def list_monthly_customers(
    service: MonthlyCustomerService = Depends(get_monthly_service),
) -> List[MonthlyCustomerResponse]:
    return [_to_response(c) for c in service.list_all()]


@router.get(
    "/active",
    response_model=List[MonthlyCustomerResponse],
    summary="Listar mensalistas ativos",
)
def list_active(
    service: MonthlyCustomerService = Depends(get_monthly_service),
) -> List[MonthlyCustomerResponse]:
    return [_to_response(c) for c in service.list_active()]


@router.get(
    "/{customer_id}",
    response_model=MonthlyCustomerResponse,
    summary="Buscar mensalista por ID",
)
def get_monthly_customer(
    customer_id: str,
    service: MonthlyCustomerService = Depends(get_monthly_service),
) -> MonthlyCustomerResponse:
    customer = service.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mensalista não encontrado."
        )
    return _to_response(customer)


@router.patch(
    "/{customer_id}/activate",
    response_model=MonthlyCustomerResponse,
    summary="Ativar plano mensal",
)
def activate(
    customer_id: str,
    service: MonthlyCustomerService = Depends(get_monthly_service),
) -> MonthlyCustomerResponse:
    try:
        return _to_response(service.activate(customer_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch(
    "/{customer_id}/deactivate",
    response_model=MonthlyCustomerResponse,
    summary="Desativar plano mensal",
)
def deactivate(
    customer_id: str,
    service: MonthlyCustomerService = Depends(get_monthly_service),
) -> MonthlyCustomerResponse:
    try:
        return _to_response(service.deactivate(customer_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover mensalista",
)
def delete_monthly_customer(
    customer_id: str,
    service: MonthlyCustomerService = Depends(get_monthly_service),
) -> None:
    try:
        service.delete(customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
