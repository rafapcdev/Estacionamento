"""
Schemas da API: Ticket
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field
from app.domain.entities.parking_spot import SpotType
from app.domain.entities.vehicle import VehicleType


class EntryRequest(BaseModel):
    plate: str = Field(..., examples=["ABC-1234"], description="Placa do veículo")
    vehicle_type: VehicleType = Field(
        VehicleType.CAR,
        description="Tipo do veículo (car | motorcycle | truck)",
    )
    spot_type: Optional[SpotType] = Field(
        None,
        description="Tipo de vaga preferencial (None = automático por tipo de veículo)",
    )

    model_config = {"str_strip_whitespace": True}


class ExitRequest(BaseModel):
    plate: str = Field(..., examples=["ABC-1234"], description="Placa do veículo")

    model_config = {"str_strip_whitespace": True}


class TicketResponse(BaseModel):
    id: str
    vehicle_plate: str
    parking_spot_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    amount: Optional[Decimal] = None
    is_closed: bool = False

    model_config = {"from_attributes": True}
