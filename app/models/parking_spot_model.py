import uuid
from sqlalchemy import Boolean, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import SpotType

class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    spot_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    spot_type: Mapped[str] = mapped_column(
        Enum(SpotType, values_callable=lambda e: [i.value for i in e]),
        nullable=False,
    )
    occupied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="spot", lazy="select"
    )

    def occupy(self) -> None:
        if self.occupied:
            raise ValueError(f"A vaga {self.spot_number} já está ocupada.")
        self.occupied = True

    def release(self) -> None:
        if not self.occupied:
            raise ValueError(f"A vaga {self.spot_number} já está livre.")
        self.occupied = False

    def is_available(self) -> bool:
        return not self.occupied
