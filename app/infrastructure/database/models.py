"""
Infrastructure: SQLAlchemy ORM Models

Mapeia as entidades de domínio para tabelas no PostgreSQL.
Os modelos ficam na camada de infraestrutura — o domínio
não tem conhecimento deles (Clean Architecture).
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.database import Base
from app.domain.entities.vehicle import VehicleType
from app.domain.entities.parking_spot import SpotType


class VehicleModel(Base):
    """Modelo de persistência para Vehicle."""

    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    plate: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    vehicle_type: Mapped[str] = mapped_column(
        Enum(VehicleType, values_callable=lambda e: [i.value for i in e]),
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<VehicleModel plate={self.plate!r}>"


class ParkingSpotModel(Base):
    """Modelo de persistência para ParkingSpot."""

    __tablename__ = "parking_spots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    spot_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    spot_type: Mapped[str] = mapped_column(
        Enum(SpotType, values_callable=lambda e: [i.value for i in e]),
        nullable=False,
    )
    occupied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    tickets: Mapped[list["TicketModel"]] = relationship(
        "TicketModel", back_populates="spot", lazy="select"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ParkingSpotModel number={self.spot_number!r}>"


class TicketModel(Base):
    """Modelo de persistência para Ticket."""

    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    vehicle_plate: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    parking_spot_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parking_spots.id"), nullable=False
    )
    entry_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    spot: Mapped["ParkingSpotModel"] = relationship(
        "ParkingSpotModel", back_populates="tickets", lazy="select"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TicketModel plate={self.vehicle_plate!r}>"


class MonthlyCustomerModel(Base):
    """Modelo de persistência para MonthlyCustomer."""

    __tablename__ = "monthly_customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    plate: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MonthlyCustomerModel name={self.name!r}>"
