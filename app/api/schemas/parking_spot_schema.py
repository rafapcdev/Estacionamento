"""
Schemas da API: Vaga de Estacionamento
"""

from pydantic import BaseModel, Field
from app.domain.entities.parking_spot import SpotType


class ParkingSpotCreateRequest(BaseModel):
    spot_number: str = Field(..., examples=["A-01"], description="Número identificador da vaga")
    spot_type: SpotType = Field(..., description="Tipo/categoria da vaga")

    model_config = {"str_strip_whitespace": True}


class ParkingSpotResponse(BaseModel):
    id: str
    spot_number: str
    spot_type: SpotType
    occupied: bool

    model_config = {"from_attributes": True}
