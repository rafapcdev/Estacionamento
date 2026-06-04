from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import MonthlyCustomer

class IMonthlyCustomerRepository(ABC):
    @abstractmethod
    def save(self, customer: MonthlyCustomer) -> MonthlyCustomer: ...
    @abstractmethod
    def find_by_id(self, customer_id: str) -> Optional[MonthlyCustomer]: ...
    @abstractmethod
    def find_by_plate(self, plate: str) -> Optional[MonthlyCustomer]: ...
    @abstractmethod
    def list_all(self) -> List[MonthlyCustomer]: ...
    @abstractmethod
    def list_active(self) -> List[MonthlyCustomer]: ...
    @abstractmethod
    def update(self, customer: MonthlyCustomer) -> MonthlyCustomer: ...
    @abstractmethod
    def delete(self, customer_id: str) -> bool: ...

class SQLAlchemyMonthlyCustomerRepository(IMonthlyCustomerRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, customer: MonthlyCustomer) -> MonthlyCustomer:
        self._session.add(customer)
        self._session.commit()
        self._session.refresh(customer)
        return customer

    def find_by_id(self, customer_id: str) -> Optional[MonthlyCustomer]:
        return self._session.get(MonthlyCustomer, customer_id)

    def find_by_plate(self, plate: str) -> Optional[MonthlyCustomer]:
        return self._session.query(MonthlyCustomer).filter(MonthlyCustomer.plate == plate).first()

    def list_all(self) -> List[MonthlyCustomer]:
        return self._session.query(MonthlyCustomer).all()

    def list_active(self) -> List[MonthlyCustomer]:
        return self._session.query(MonthlyCustomer).filter(MonthlyCustomer.active.is_(True)).all()

    def update(self, customer: MonthlyCustomer) -> MonthlyCustomer:
        self._session.commit()
        self._session.refresh(customer)
        return customer

    def delete(self, customer_id: str) -> bool:
        customer = self._session.get(MonthlyCustomer, customer_id)
        if not customer:
            return False
        self._session.delete(customer)
        self._session.commit()
        return True
