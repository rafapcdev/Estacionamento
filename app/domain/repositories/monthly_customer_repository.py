from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.monthly_customer import MonthlyCustomer


class IMonthlyCustomerRepository(ABC):
    """Interface para persistência de MonthlyCustomer."""

    @abstractmethod
    def save(self, customer: MonthlyCustomer) -> MonthlyCustomer:
        """Persiste um novo mensalista."""
        ...

    @abstractmethod
    def find_by_id(self, customer_id: str) -> Optional[MonthlyCustomer]:
        """Busca um mensalista pelo ID."""
        ...

    @abstractmethod
    def find_by_plate(self, plate: str) -> Optional[MonthlyCustomer]:
        """Busca um mensalista pela placa do veículo."""
        ...

    @abstractmethod
    def list_all(self) -> List[MonthlyCustomer]:
        """Lista todos os mensalistas."""
        ...

    @abstractmethod
    def list_active(self) -> List[MonthlyCustomer]:
        """Lista apenas mensalistas com plano ativo."""
        ...

    @abstractmethod
    def update(self, customer: MonthlyCustomer) -> MonthlyCustomer:
        """Atualiza os dados de um mensalista."""
        ...

    @abstractmethod
    def delete(self, customer_id: str) -> bool:
        """Remove um mensalista pelo ID."""
        ...
