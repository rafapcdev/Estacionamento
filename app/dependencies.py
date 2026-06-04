"""
Injeção de Dependências da API

Fornece repositórios e serviços configurados para os endpoints do FastAPI.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.vehicle_repository import SQLAlchemyVehicleRepository
from app.repositories.parking_spot_repository import SQLAlchemyParkingSpotRepository
from app.repositories.ticket_repository import SQLAlchemyTicketRepository
from app.repositories.monthly_customer_repository import SQLAlchemyMonthlyCustomerRepository

from app.services.billing_service import BillingService
from app.services.monthly_customer_service import MonthlyCustomerService
from app.services.parking_spot_service import ParkingSpotService
from app.services.entry_service import EntryService
from app.services.exit_service import ExitService


# ─────────────────────────────────────────────
# Repositórios
# ─────────────────────────────────────────────
def get_vehicle_repo(db: Session = Depends(get_db)) -> SQLAlchemyVehicleRepository:
    return SQLAlchemyVehicleRepository(db)


def get_spot_repo(db: Session = Depends(get_db)) -> SQLAlchemyParkingSpotRepository:
    return SQLAlchemyParkingSpotRepository(db)


def get_ticket_repo(db: Session = Depends(get_db)) -> SQLAlchemyTicketRepository:
    return SQLAlchemyTicketRepository(db)


def get_monthly_repo(db: Session = Depends(get_db)) -> SQLAlchemyMonthlyCustomerRepository:
    return SQLAlchemyMonthlyCustomerRepository(db)


# ─────────────────────────────────────────────
# Serviços
# ─────────────────────────────────────────────
def get_billing_service() -> BillingService:
    return BillingService()


def get_monthly_service(
    repo: SQLAlchemyMonthlyCustomerRepository = Depends(get_monthly_repo),
) -> MonthlyCustomerService:
    return MonthlyCustomerService(repo)


def get_spot_service(
    repo: SQLAlchemyParkingSpotRepository = Depends(get_spot_repo),
) -> ParkingSpotService:
    return ParkingSpotService(repo)


def get_entry_service(
    spot_repo: SQLAlchemyParkingSpotRepository = Depends(get_spot_repo),
    ticket_repo: SQLAlchemyTicketRepository = Depends(get_ticket_repo),
    monthly_service: MonthlyCustomerService = Depends(get_monthly_service),
) -> EntryService:
    return EntryService(spot_repo, ticket_repo, monthly_service)


def get_exit_service(
    spot_repo: SQLAlchemyParkingSpotRepository = Depends(get_spot_repo),
    ticket_repo: SQLAlchemyTicketRepository = Depends(get_ticket_repo),
    billing_service: BillingService = Depends(get_billing_service),
    monthly_service: MonthlyCustomerService = Depends(get_monthly_service),
) -> ExitService:
    return ExitService(spot_repo, ticket_repo, billing_service, monthly_service)
