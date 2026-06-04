"""
Testes de Integração E2E: API do Sistema de Estacionamento

Verifica o ciclo de vida completo do sistema com todas as dependências reais
usando o TestClient do FastAPI e banco de dados SQLite em memória:
vagas → mensalistas → entradas → saídas → faturamento → liberação.
"""

from decimal import Decimal


def test_fluxo_completo_estacionamento(client):
    # ── 1. Vagas ─────────────────────────────────────────────────────
    response = client.post("/api/v1/spots/", json={"spot_number": "A-01", "spot_type": "common"})
    assert response.status_code == 201
    spot_a01 = response.json()
    assert spot_a01["spot_number"] == "A-01"
    assert spot_a01["spot_type"] == "common"
    assert not spot_a01["occupied"]

    response = client.post("/api/v1/spots/", json={"spot_number": "A-02", "spot_type": "common"})
    assert response.status_code == 201
    spot_a02 = response.json()

    response = client.post("/api/v1/spots/", json={"spot_number": "M-01", "spot_type": "motorcycle"})
    assert response.status_code == 201
    spot_m01 = response.json()
    assert spot_m01["spot_number"] == "M-01"
    assert spot_m01["spot_type"] == "motorcycle"

    # ── 2. Mensalista ────────────────────────────────────────────────
    response = client.post("/api/v1/monthly-customers/", json={"name": "Maria Silva", "plate": "ABC-1234"})
    assert response.status_code == 201
    cliente = response.json()
    assert cliente["name"] == "Maria Silva"
    assert cliente["plate"] == "ABC-1234"
    assert cliente["active"] is True

    # ── 3. Estado inicial das vagas (todas livres) ───────────────────
    response = client.get("/api/v1/spots/")
    assert response.status_code == 200
    vagas = response.json()
    assert len(vagas) == 3
    for vaga in vagas:
        assert not vaga["occupied"]

    # ── 4. Entradas de veículos ──────────────────────────────────────
    response = client.post("/api/v1/tickets/entry", json={"plate": "XYZ-5678", "vehicle_type": "car"})
    assert response.status_code == 201
    ticket_carro = response.json()
    assert ticket_carro["vehicle_plate"] == "XYZ-5678"
    assert ticket_carro["parking_spot_id"] == spot_a01["id"]
    assert not ticket_carro["is_closed"]

    # Veículo já no estacionamento deve ser recusado
    response = client.post("/api/v1/tickets/entry", json={"plate": "XYZ-5678", "vehicle_type": "car"})
    assert response.status_code == 400
    assert "já está no estacionamento" in response.json()["detail"]

    response = client.post("/api/v1/tickets/entry", json={"plate": "MOT-9999", "vehicle_type": "motorcycle"})
    assert response.status_code == 201
    ticket_moto = response.json()
    assert ticket_moto["vehicle_plate"] == "MOT-9999"
    assert ticket_moto["parking_spot_id"] == spot_m01["id"]

    response = client.post("/api/v1/tickets/entry", json={"plate": "ABC-1234", "vehicle_type": "car"})
    assert response.status_code == 201
    ticket_mensalista = response.json()
    assert ticket_mensalista["vehicle_plate"] == "ABC-1234"
    assert ticket_mensalista["parking_spot_id"] == spot_a02["id"]

    # ── 5. Tickets em aberto (deve haver 3) ──────────────────────────
    response = client.get("/api/v1/tickets/open")
    assert response.status_code == 200
    tickets_abertos = response.json()
    assert len(tickets_abertos) == 3
    placas = [t["vehicle_plate"] for t in tickets_abertos]
    assert "XYZ-5678" in placas
    assert "MOT-9999" in placas
    assert "ABC-1234" in placas

    # ── 6. Saídas e cobrança ─────────────────────────────────────────
    response = client.post("/api/v1/tickets/exit", json={"plate": "XYZ-5678"})
    assert response.status_code == 200
    saida_carro = response.json()
    assert saida_carro["is_closed"] is True
    assert Decimal(str(saida_carro["amount"])) >= Decimal("0.00")

    # Mensalista deve ter cobrança zerada
    response = client.post("/api/v1/tickets/exit", json={"plate": "ABC-1234"})
    assert response.status_code == 200
    saida_mensalista = response.json()
    assert saida_mensalista["is_closed"] is True
    assert Decimal(str(saida_mensalista["amount"])) == Decimal("0.00")

    response = client.post("/api/v1/tickets/exit", json={"plate": "MOT-9999"})
    assert response.status_code == 200
    saida_moto = response.json()
    assert saida_moto["is_closed"] is True

    # ── 7. Estado final (tickets fechados, vagas livres) ─────────────
    response = client.get("/api/v1/tickets/open")
    assert response.status_code == 200
    assert len(response.json()) == 0

    response = client.get("/api/v1/spots/")
    assert response.status_code == 200
    for vaga in response.json():
        assert not vaga["occupied"]

