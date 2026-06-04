"""
Schemas da API: Mensalista
"""

from pydantic import BaseModel, Field


class MonthlyCustomerCreateRequest(BaseModel):
    name: str = Field(..., examples=["João Silva"], description="Nome completo do mensalista")
    plate: str = Field(..., examples=["XYZ-9876"], description="Placa do veículo")

    model_config = {"str_strip_whitespace": True}


class MonthlyCustomerResponse(BaseModel):
    id: str
    name: str
    plate: str
    active: bool

    model_config = {"from_attributes": True}
