import uuid
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.enums import VehicleType

class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plate: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    vehicle_type: Mapped[str] = mapped_column(
        Enum(VehicleType, values_callable=lambda e: [i.value for i in e]),
        nullable=False,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())
        self.validate()

    def validate(self) -> None:
        if not self.plate or not self.plate.strip():
            raise ValueError("A placa do veículo não pode estar vazia.")
        self.plate = self.plate.upper().strip()
