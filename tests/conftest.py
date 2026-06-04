"""
Test fixtures compartilhadas (conftest.py).

Usa SQLite em memória para testes — sem necessidade de PostgreSQL.
Injeta os repositórios nos serviços automaticamente.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.database import Base
from app.infrastructure.repositories.vehicle_repository import SQLAlchemyVehicleRepository
from app.infrastructure.repositories.parking_spot_repository import SQLAlchemyParkingSpotRepository
from app.infrastructure.repositories.ticket_repository import SQLAlchemyTicketRepository
from app.infrastructure.repositories.monthly_customer_repository import SQLAlchemyMonthlyCustomerRepository

from app.application.services.billing_service import BillingService
from app.application.services.monthly_customer_service import MonthlyCustomerService
from app.application.services.parking_spot_service import ParkingSpotService
from app.application.services.entry_service import EntryService
from app.application.services.exit_service import ExitService
from fastapi.testclient import TestClient
from main import app
from app.infrastructure.database.database import get_db


# ─────────────────────────────────────────────
# Engine SQLite em memória (escopo de sessão de teste)
# ─────────────────────────────────────────────
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture()
def db_session(engine):
    """Sessão com rollback após cada teste — garante isolamento."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# ─────────────────────────────────────────────
# Repositórios
# ─────────────────────────────────────────────
@pytest.fixture()
def vehicle_repo(db_session):
    return SQLAlchemyVehicleRepository(db_session)


@pytest.fixture()
def spot_repo(db_session):
    return SQLAlchemyParkingSpotRepository(db_session)


@pytest.fixture()
def ticket_repo(db_session):
    return SQLAlchemyTicketRepository(db_session)


@pytest.fixture()
def monthly_repo(db_session):
    return SQLAlchemyMonthlyCustomerRepository(db_session)


# ─────────────────────────────────────────────
# Serviços
# ─────────────────────────────────────────────
@pytest.fixture()
def billing_service():
    return BillingService()


@pytest.fixture()
def monthly_service(monthly_repo):
    return MonthlyCustomerService(monthly_repo)


@pytest.fixture()
def spot_service(spot_repo):
    return ParkingSpotService(spot_repo)


@pytest.fixture()
def entry_service(spot_repo, ticket_repo, monthly_service):
    return EntryService(spot_repo, ticket_repo, monthly_service)


@pytest.fixture()
def exit_service(spot_repo, ticket_repo, billing_service, monthly_service):
    return ExitService(spot_repo, ticket_repo, billing_service, monthly_service)


@pytest.fixture()
def client(db_session):
    """Retorna um TestClient do FastAPI com a dependência de DB substituída pelo db_session de teste."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

