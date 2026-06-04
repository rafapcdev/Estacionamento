"""
Estratégias de Cobrança (domínio)

Aplica o padrão Strategy + OCP (Open/Closed Principle):
- BillingStrategy: interface (contrato).
- Implementações concretas podem ser adicionadas sem alterar código existente.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from math import ceil


# ─────────────────────────────────────────────
# Interface
# ─────────────────────────────────────────────
class BillingStrategy(ABC):
    """
    Interface para estratégias de cobrança.

    Todas as implementações recebem a duração em horas
    e retornam o valor a cobrar como Decimal.
    """

    @abstractmethod
    def calculate(self, duration_hours: float) -> Decimal:
        """
        Calcula o valor da cobrança.

        Args:
            duration_hours (float): Tempo total de permanência em horas.

        Returns:
            Decimal: Valor a ser cobrado.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome legível da estratégia."""
        ...


# ─────────────────────────────────────────────
# Implementação 1: Por hora
# ─────────────────────────────────────────────
class HourlyBilling(BillingStrategy):
    """
    Cobra por hora cheia (ou fração arredondada para cima).

    Exemplo: 1,5 h → 2 horas cobradas.
    """

    def __init__(self, price_per_hour: Decimal = Decimal("10.00")) -> None:
        self._price_per_hour = price_per_hour

    @property
    def name(self) -> str:
        return "hourly"

    def calculate(self, duration_hours: float) -> Decimal:
        if duration_hours <= 0:
            return Decimal("0.00")
        hours = Decimal(str(ceil(duration_hours)))
        return (hours * self._price_per_hour).quantize(Decimal("0.01"))


# ─────────────────────────────────────────────
# Implementação 2: Tarifa fixa
# ─────────────────────────────────────────────
class FixedBilling(BillingStrategy):
    """
    Cobra um valor fixo independente do tempo de permanência.

    Útil para eventos ou promoções com tempo máximo predefinido.
    """

    def __init__(self, fixed_amount: Decimal = Decimal("20.00")) -> None:
        self._fixed_amount = fixed_amount

    @property
    def name(self) -> str:
        return "fixed"

    def calculate(self, duration_hours: float) -> Decimal:
        return self._fixed_amount.quantize(Decimal("0.01"))


# ─────────────────────────────────────────────
# Implementação 3: Por diária
# ─────────────────────────────────────────────
class DailyBilling(BillingStrategy):
    """
    Cobra por diária (a cada 24 horas ou fração).

    Exemplo: 25 h → 2 diárias cobradas.
    """

    def __init__(self, price_per_day: Decimal = Decimal("50.00")) -> None:
        self._price_per_day = price_per_day

    @property
    def name(self) -> str:
        return "daily"

    def calculate(self, duration_hours: float) -> Decimal:
        if duration_hours <= 0:
            return Decimal("0.00")
        days = Decimal(str(ceil(duration_hours / 24)))
        return (days * self._price_per_day).quantize(Decimal("0.01"))
