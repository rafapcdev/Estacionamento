import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import DateTime, Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_plate: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    parking_spot_id: Mapped[str] = mapped_column(String(36), ForeignKey("parking_spots.id"), nullable=False)
    entry_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    exit_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    spot: Mapped["ParkingSpot"] = relationship("ParkingSpot", back_populates="tickets", lazy="select")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.entry_time is None:
            self.entry_time = datetime.now(timezone.utc)

    def is_closed(self) -> bool:
        return self.exit_time is not None

    def duration_in_hours(self, current_time: datetime | None = None) -> float:
        end_time = self.exit_time or current_time or datetime.now(timezone.utc)
        if end_time < self.entry_time:
            raise ValueError("O horário de saída não pode ser anterior ao horário de entrada.")
        delta = end_time - self.entry_time
        return delta.total_seconds() / 3600.0

    def close(self, exit_time: datetime, amount: Decimal) -> None:
        if self.is_closed():
            raise ValueError(f"O ticket {self.id} já foi encerrado.")
        if exit_time < self.entry_time:
            raise ValueError("O horário de saída não pode ser anterior ao de entrada.")
        self.exit_time = exit_time
        self.amount = amount
