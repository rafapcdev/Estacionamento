import uuid
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class MonthlyCustomer(Base):
    __tablename__ = "monthly_customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    plate: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "active" not in kwargs:
            self.active = True
        self.validate()

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("O nome do cliente não pode estar vazio.")
        if not self.plate or not self.plate.strip():
            raise ValueError("A placa do veículo não pode estar vazia.")
        self.plate = self.plate.upper().strip()

    def activate(self) -> None:
        self.active = True

    def deactivate(self) -> None:
        self.active = False
