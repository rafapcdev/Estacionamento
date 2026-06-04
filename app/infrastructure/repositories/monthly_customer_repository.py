"""
Infrastructure Repository: SQLAlchemyMonthlyCustomerRepository
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.monthly_customer import MonthlyCustomer
from app.domain.repositories.monthly_customer_repository import IMonthlyCustomerRepository
from app.infrastructure.database.models import MonthlyCustomerModel


class SQLAlchemyMonthlyCustomerRepository(IMonthlyCustomerRepository):
    """Repositório de mensalistas com persistência em PostgreSQL via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------ #
    # Mapeamentos
    # ------------------------------------------------------------------ #
    @staticmethod
    def _to_entity(model: MonthlyCustomerModel) -> MonthlyCustomer:
        customer = MonthlyCustomer.__new__(MonthlyCustomer)
        customer.id = model.id
        customer.name = model.name
        customer.plate = model.plate
        customer.active = model.active
        return customer

    @staticmethod
    def _to_model(customer: MonthlyCustomer) -> MonthlyCustomerModel:
        return MonthlyCustomerModel(
            id=customer.id,
            name=customer.name,
            plate=customer.plate,
            active=customer.active,
        )

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    def save(self, customer: MonthlyCustomer) -> MonthlyCustomer:
        model = self._to_model(customer)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, customer_id: str) -> Optional[MonthlyCustomer]:
        model = self._session.get(MonthlyCustomerModel, customer_id)
        return self._to_entity(model) if model else None

    def find_by_plate(self, plate: str) -> Optional[MonthlyCustomer]:
        model = (
            self._session.query(MonthlyCustomerModel)
            .filter(MonthlyCustomerModel.plate == plate.upper())
            .first()
        )
        return self._to_entity(model) if model else None

    def list_all(self) -> List[MonthlyCustomer]:
        return [self._to_entity(m) for m in self._session.query(MonthlyCustomerModel).all()]

    def list_active(self) -> List[MonthlyCustomer]:
        models = (
            self._session.query(MonthlyCustomerModel)
            .filter(MonthlyCustomerModel.active.is_(True))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def update(self, customer: MonthlyCustomer) -> MonthlyCustomer:
        model = self._session.get(MonthlyCustomerModel, customer.id)
        if not model:
            raise ValueError(f"Mensalista com ID '{customer.id}' não encontrado.")
        model.name = customer.name
        model.plate = customer.plate
        model.active = customer.active
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, customer_id: str) -> bool:
        model = self._session.get(MonthlyCustomerModel, customer_id)
        if not model:
            return False
        self._session.delete(model)
        self._session.commit()
        return True
