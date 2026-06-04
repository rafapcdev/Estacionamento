"""
Serviço de Mensalistas (MonthlyCustomerService)

Responsabilidade: cadastro e gerenciamento de clientes mensalistas.
"""

from typing import List, Optional

from app.models import MonthlyCustomer
from app.repositories.monthly_customer_repository import IMonthlyCustomerRepository


class MonthlyCustomerService:
    """
    Serviço de mensalistas.

    Permite cadastrar, listar, ativar/desativar e remover mensalistas.
    """

    def __init__(self, customer_repository: IMonthlyCustomerRepository) -> None:
        self._repo = customer_repository

    # ------------------------------------------------------------------ #
    # Criação
    # ------------------------------------------------------------------ #
    def register(self, name: str, plate: str) -> MonthlyCustomer:
        """
        Cadastra um novo mensalista.

        Raises:
            ValueError: Se a placa já estiver associada a outro mensalista ativo.
        """
        plate = plate.upper().strip()
        existing = self._repo.find_by_plate(plate)
        if existing and existing.active:
            raise ValueError(
                f"A placa '{plate}' já está cadastrada para o mensalista '{existing.name}'."
            )
        customer = MonthlyCustomer(name=name, plate=plate)
        return self._repo.save(customer)

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    def get_by_id(self, customer_id: str) -> Optional[MonthlyCustomer]:
        return self._repo.find_by_id(customer_id)

    def get_by_plate(self, plate: str) -> Optional[MonthlyCustomer]:
        return self._repo.find_by_plate(plate.upper().strip())

    def is_monthly_customer(self, plate: str) -> bool:
        """Retorna True se a placa pertencer a um mensalista ativo."""
        customer = self._repo.find_by_plate(plate.upper().strip())
        return customer is not None and customer.active

    def list_all(self) -> List[MonthlyCustomer]:
        return self._repo.list_all()

    def list_active(self) -> List[MonthlyCustomer]:
        return self._repo.list_active()

    # ------------------------------------------------------------------ #
    # Atualização
    # ------------------------------------------------------------------ #
    def activate(self, customer_id: str) -> MonthlyCustomer:
        customer = self._get_or_raise(customer_id)
        customer.activate()
        return self._repo.update(customer)

    def deactivate(self, customer_id: str) -> MonthlyCustomer:
        customer = self._get_or_raise(customer_id)
        customer.deactivate()
        return self._repo.update(customer)

    # ------------------------------------------------------------------ #
    # Remoção
    # ------------------------------------------------------------------ #
    def delete(self, customer_id: str) -> bool:
        self._get_or_raise(customer_id)
        return self._repo.delete(customer_id)

    # ------------------------------------------------------------------ #
    # Helpers privados
    # ------------------------------------------------------------------ #
    def _get_or_raise(self, customer_id: str) -> MonthlyCustomer:
        customer = self._repo.find_by_id(customer_id)
        if not customer:
            raise ValueError(f"Mensalista com ID '{customer_id}' não encontrado.")
        return customer
