"""
Schemas da API: Veículo

Modelos Pydantic para validação de entrada/saída da API de veículos.
Mantidos separados das entidades de domínio para não poluir o domínio
com dependências de serialização (SRP + Clean Architecture).
"""

from pydantic import BaseModel, Field
from app.domain.entities.vehicle import VehicleType


# ─────────────────────────────────────────────
# Entrada
# ─────────────────────────────────────────────
class VehicleCreateRequest(BaseModel):
    plate: str = Field(..., examples=["ABC-1234"], description="Placa do veículo")
    vehicle_type: VehicleType = Field(..., description="Tipo do veículo")

    model_config = {"str_strip_whitespace": True}


# ─────────────────────────────────────────────
# Saída
# ─────────────────────────────────────────────
class VehicleResponse(BaseModel):
    id: str
    plate: str
    vehicle_type: VehicleType

    model_config = {"from_attributes": True}
