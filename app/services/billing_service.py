"""
Serviço de Cobrança (BillingService)

Responsabilidade única: calcular cobranças usando uma BillingStrategy.
Segue SRP + OCP: não sabe como o valor é calculado, apenas delega.
"""

from decimal import Decimal

from app.services.billing_strategy import BillingStrategy, HourlyBilling


class BillingService:
    """
    Serviço de cobrança.

    Recebe qualquer BillingStrategy via injeção de dependência,
    permitindo trocar a estratégia sem alterar este serviço.
    """

    def __init__(self, strategy: BillingStrategy | None = None) -> None:
        # Estratégia padrão: cobrança por hora
        self._strategy: BillingStrategy = strategy or HourlyBilling()

    def set_strategy(self, strategy: BillingStrategy) -> None:
        """Troca a estratégia em tempo de execução."""
        self._strategy = strategy

    def calculate(self, duration_hours: float) -> Decimal:
        """
        Delega o cálculo à estratégia configurada.

        Args:
            duration_hours (float): Duração da permanência em horas.

        Returns:
            Decimal: Valor a cobrar.
        """
        return self._strategy.calculate(duration_hours)

    @property
    def strategy_name(self) -> str:
        """Retorna o nome da estratégia ativa."""
        return self._strategy.name
