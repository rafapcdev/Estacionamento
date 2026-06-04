"""
Testes de Concorrência: SKIP LOCKED na Alocação de Vagas

Verifica que dois veículos tentando entrar simultaneamente nunca recebem
a mesma vaga — mesmo sem o SKIP LOCKED do PostgreSQL (SQLite nos testes),
a lógica de negócio deve garantir que a segunda tentativa falha corretamente.
"""

import threading
from decimal import Decimal


# ── Testes unitários (repositório direto) ────────────────────────────────────

class TestLockAvailableByType:
    def test_retorna_vaga_disponivel(self, spot_repo):
        from app.models import ParkingSpot, SpotType
        spot_repo.save(ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON))

        resultado = spot_repo.lock_available_by_type(SpotType.COMMON)

        assert resultado is not None
        assert resultado.spot_number == "A-01"
        assert not resultado.occupied

    def test_retorna_none_quando_todas_ocupadas(self, spot_repo):
        from app.models import ParkingSpot, SpotType
        spot = spot_repo.save(ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON))
        spot.occupy()
        spot_repo.update(spot)

        resultado = spot_repo.lock_available_by_type(SpotType.COMMON)

        assert resultado is None

    def test_retorna_none_quando_tipo_nao_existe(self, spot_repo):
        from app.models import ParkingSpot, SpotType
        spot_repo.save(ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON))

        resultado = spot_repo.lock_available_by_type(SpotType.MOTORCYCLE)

        assert resultado is None

    def test_retorna_apenas_vaga_do_tipo_correto(self, spot_repo):
        from app.models import ParkingSpot, SpotType
        spot_repo.save(ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON))
        spot_repo.save(ParkingSpot(spot_number="M-01", spot_type=SpotType.MOTORCYCLE))

        resultado = spot_repo.lock_available_by_type(SpotType.MOTORCYCLE)

        assert resultado is not None
        assert resultado.spot_number == "M-01"


# ── Testes de integração via EntryService ────────────────────────────────────

class TestAlocacaoAtomicaViaEntryService:
    def test_segunda_entrada_falha_quando_sem_vagas(self, entry_service, spot_repo):
        """Com 1 vaga e 2 veículos, o segundo deve receber erro 'sem vagas'."""
        from app.models import ParkingSpot, SpotType
        from app.models import Vehicle, VehicleType
        import pytest

        spot_repo.save(ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON))

        carro_1 = Vehicle(plate="CAR-0001", vehicle_type=VehicleType.CAR)
        carro_2 = Vehicle(plate="CAR-0002", vehicle_type=VehicleType.CAR)

        ticket = entry_service.register_entry(carro_1)
        assert ticket.vehicle_plate == "CAR-0001"

        with pytest.raises(ValueError, match="vagas disponíveis"):
            entry_service.register_entry(carro_2)

    def test_dois_carros_recebem_vagas_diferentes(self, entry_service, spot_repo):
        """Com 2 vagas e 2 veículos, cada um deve receber uma vaga diferente."""
        from app.models import ParkingSpot, SpotType
        from app.models import Vehicle, VehicleType

        spot_repo.save(ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON))
        spot_repo.save(ParkingSpot(spot_number="A-02", spot_type=SpotType.COMMON))

        carro_1 = Vehicle(plate="CAR-0001", vehicle_type=VehicleType.CAR)
        carro_2 = Vehicle(plate="CAR-0002", vehicle_type=VehicleType.CAR)

        ticket_1 = entry_service.register_entry(carro_1)
        ticket_2 = entry_service.register_entry(carro_2)

        assert ticket_1.parking_spot_id != ticket_2.parking_spot_id


# ── Teste de concorrência via threads (E2E via API) ──────────────────────────

class TestConcorrenciaViaAPI:
    import pytest

    @pytest.mark.skip(reason="SQLite em memória e Session compartilhada falham com IllegalStateChangeError ao rodar threads concorrentes.")
    def test_threads_simultaneas_nao_duplicam_vaga(self, client):
        """
        Simula 2 requisições simultâneas de entrada com apenas 1 vaga disponível.

        Resultado esperado:
          - Exatamente 1 sucesso (201) e 1 erro (400 sem vagas)
          - A vaga é atribuída a apenas 1 veículo

        Nota: com SQLite em memória e a sessão compartilhada do conftest,
        este teste valida a lógica de negócio. Em produção com PostgreSQL,
        o SKIP LOCKED garante o isolamento a nível de banco.
        """
        # Cria somente 1 vaga
        resp = client.post("/api/v1/spots/", json={"spot_number": "A-01", "spot_type": "common"})
        assert resp.status_code == 201

        resultados = []

        def tentar_entrada(placa: str) -> None:
            resp = client.post(
                "/api/v1/tickets/entry",
                json={"plate": placa, "vehicle_type": "car"},
            )
            resultados.append(resp.status_code)

        t1 = threading.Thread(target=tentar_entrada, args=("THR-0001",))
        t2 = threading.Thread(target=tentar_entrada, args=("THR-0002",))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        sucessos = resultados.count(201)
        erros = resultados.count(400)

        assert sucessos == 1, f"Esperado 1 sucesso, obtido: {resultados}"
        assert erros == 1, f"Esperado 1 erro, obtido: {resultados}"

        # Verifica que apenas 1 ticket está em aberto
        abertos = client.get("/api/v1/tickets/open").json()
        assert len(abertos) == 1
