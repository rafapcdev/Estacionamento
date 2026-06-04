from app.domain.repositories.vehicle_repository import IVehicleRepository
from app.domain.repositories.parking_spot_repository import IParkingSpotRepository
from app.domain.repositories.ticket_repository import ITicketRepository
from app.domain.repositories.monthly_customer_repository import IMonthlyCustomerRepository

__all__ = [
    "IVehicleRepository",
    "IParkingSpotRepository",
    "ITicketRepository",
    "IMonthlyCustomerRepository",
]
