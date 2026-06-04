"""
Injeção de Dependências da API

Centraliza a criação dos repositórios e serviços,
conectando a camada de infraestrutura à camada de aplicação.

FastAPI chama get_db() → cria sessão → injeta nos repositórios → injeta nos serviços.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.vehicle_repository import SQLAlchemyVehicleRepository
from app.infrastructure.repositories.parking_spot_repository import SQLAlchemyParkingSpotRepository
from app.infrastructure.repositories.ticket_repository import SQLAlchemyTicketRepository
from app.infrastructure.repositories.monthly_customer_repository import SQLAlchemyMonthlyCustomerRepository

from app.application.services.billing_service import BillingService
from app.application.services.entry_service import EntryService
from app.application.services.exit_service import ExitService
from app.application.services.parking_spot_service import ParkingSpotService
from app.application.services.monthly_customer_service import MonthlyCustomerService


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
    """Retorna BillingService com estratégia padrão (HourlyBilling)."""
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
