# 🅿️ Parking System API

API REST para gerenciamento de estacionamento, desenvolvida como **projeto didático** com foco em:

- **Clean Architecture**
- **SOLID Principles**
- **Repository Pattern**
- **Strategy Pattern**
- **Dependency Injection**

---

## 📐 Arquitetura

```
parking-system/
├── app/
│   ├── domain/                  ← Regras de negócio puras (sem frameworks)
│   │   ├── entities/            ← Vehicle, ParkingSpot, Ticket, MonthlyCustomer
│   │   ├── repositories/        ← Interfaces (contratos) dos repositórios
│   │   └── strategies/          ← BillingStrategy (Strategy Pattern)
│   │
│   ├── application/             ← Casos de uso / serviços de aplicação
│   │   └── services/            ← EntryService, ExitService, BillingService, ...
│   │
│   ├── infrastructure/          ← Implementações concretas (banco de dados)
│   │   ├── database/            ← SQLAlchemy config + modelos ORM
│   │   └── repositories/        ← SQLAlchemy repositories (implementam interfaces)
│   │
│   └── api/                     ← Camada HTTP (FastAPI)
│       ├── routes/              ← Endpoints REST
│       ├── schemas/             ← Pydantic schemas (request/response)
│       └── dependencies.py      ← Injeção de dependências
│
├── tests/                       ← Pytest (SQLite em memória)
├── main.py                      ← Ponto de entrada da aplicação
├── requirements.txt
├── pyproject.toml               ← Configuração do pytest
└── .env.example
```

---

## 🧱 Princípios SOLID aplicados

| Princípio | Onde é aplicado |
|-----------|----------------|
| **SRP** — Single Responsibility | Cada serviço tem uma única responsabilidade: `EntryService` (entradas), `ExitService` (saídas), `BillingService` (cobrança), etc. |
| **OCP** — Open/Closed | `BillingStrategy` permite adicionar novas formas de cobrança sem alterar código existente. |
| **LSP** — Liskov Substitution | `HourlyBilling`, `FixedBilling` e `DailyBilling` são intercambiáveis onde `BillingStrategy` é esperado. |
| **ISP** — Interface Segregation | Repositórios separados por entidade: `IVehicleRepository`, `IParkingSpotRepository`, etc. |
| **DIP** — Dependency Inversion | Serviços dependem de interfaces (domain), não de implementações (infrastructure). A inversão é feita via injeção de dependência no FastAPI. |

---

## 🗂️ Entidades de Domínio

### Vehicle
```python
Vehicle(plate="ABC-1234", vehicle_type=VehicleType.CAR)
# VehicleType: car | motorcycle | truck
```

### ParkingSpot
```python
ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON)
# SpotType: common | elderly | pcd | motorcycle
```

### Ticket
- Representa a permanência de um veículo (entrada → saída)
- Aberto na entrada, fechado com `exit_time` e `amount` na saída

### MonthlyCustomer
- Clientes com plano mensal são isentos de cobrança (`amount = 0.00`)

---

## 📊 Strategy Pattern — Cobrança

```
BillingStrategy (interface)
├── HourlyBilling   → cobra por hora (arredonda para cima)
├── FixedBilling    → valor fixo independente do tempo
└── DailyBilling    → cobra por diária (a cada 24h ou fração)
```

Para adicionar uma nova estratégia:
```python
class WeekendBilling(BillingStrategy):
    @property
    def name(self) -> str:
        return "weekend"

    def calculate(self, duration_hours: float) -> Decimal:
        # sua lógica aqui
        ...
```
Nenhum código existente precisa ser alterado. ✅

---

## 🐳 Como executar com Docker (recomendado)

Não precisa instalar Python ou PostgreSQL — o Docker cuida de tudo.

### 1. Pré-requisito
- [Docker](https://docs.docker.com/get-docker/) + [Docker Compose](https://docs.docker.com/compose/)

### 2. Subir a aplicação
```bash
cd parking-system

# Copiar e ajustar as variáveis (opcional — os defaults já funcionam)
cp .env.docker .env

# Construir e subir API + PostgreSQL
docker compose up --build
```

Aguarde o log `Application startup complete.` e acesse:
- **Swagger UI**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

### 3. Outros comandos úteis

```bash
# Subir em background
docker compose up -d --build

# Ver logs da API
docker compose logs -f api

# Parar tudo
docker compose down

# Parar e remover volume do banco (reset total)
docker compose down -v

# Rodar testes dentro do Docker
docker compose --profile test up tests
```

### 4. Hot-reload no desenvolvimento

```bash
# Reflete mudanças em app/ automaticamente sem rebuild
docker compose watch
```

---

## 🖥️ Como executar localmente (sem Docker)

### 1. Pré-requisitos
- Python 3.13+
- PostgreSQL rodando localmente

### 2. Configurar ambiente
```bash
cd parking-system

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# edite o .env com suas credenciais do PostgreSQL
```

### 3. Criar o banco de dados PostgreSQL
```sql
CREATE DATABASE parking_db;
```

### 4. Iniciar o servidor
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Acessar a documentação interativa
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

---

## 🧪 Executar testes

Os testes usam **SQLite em memória** — não é necessário PostgreSQL.

```bash
# Na pasta parking-system
pytest

# Com cobertura (requer pytest-cov)
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

---

## 📡 Endpoints da API

### Veículos — `/api/v1/vehicles`
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/` | Cadastrar veículo |
| GET | `/` | Listar todos |
| GET | `/{id}` | Buscar por ID |
| DELETE | `/{id}` | Remover |

### Vagas — `/api/v1/spots`
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/` | Criar vaga |
| GET | `/` | Listar todas |
| GET | `/available` | Listar disponíveis |
| GET | `/{id}` | Buscar por ID |
| DELETE | `/{id}` | Remover |

### Tickets — `/api/v1/tickets`
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/entry` | Registrar entrada |
| POST | `/exit` | Registrar saída |
| GET | `/` | Listar todos |
| GET | `/open` | Listar em aberto |
| GET | `/{id}` | Buscar por ID |

### Mensalistas — `/api/v1/monthly-customers`
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/` | Cadastrar mensalista |
| GET | `/` | Listar todos |
| GET | `/active` | Listar ativos |
| GET | `/{id}` | Buscar por ID |
| PATCH | `/{id}/activate` | Ativar plano |
| PATCH | `/{id}/deactivate` | Desativar plano |
| DELETE | `/{id}` | Remover |

---

## 💡 Exemplo de uso completo

```bash
BASE=http://localhost:8000/api/v1

# 1. Criar uma vaga
curl -X POST "$BASE/spots" \
  -H "Content-Type: application/json" \
  -d '{"spot_number": "A-01", "spot_type": "common"}'

# 2. Registrar entrada
curl -X POST "$BASE/tickets/entry" \
  -H "Content-Type: application/json" \
  -d '{"plate": "ABC-1234", "vehicle_type": "car"}'

# 3. Registrar saída (cobra automaticamente)
curl -X POST "$BASE/tickets/exit" \
  -H "Content-Type: application/json" \
  -d '{"plate": "ABC-1234"}'
```

---

## 🛠️ Stack Tecnológica

| Tecnologia | Versão | Finalidade |
|-----------|--------|-----------|
| Python | 3.13 | Linguagem principal |
| FastAPI | 0.115 | Framework web |
| SQLAlchemy | 2.0 | ORM |
| PostgreSQL | — | Banco de produção |
| Pydantic | 2.x | Validação de dados |
| Uvicorn | 0.32 | Servidor ASGI |
| Pytest | 8.x | Testes |
| SQLite | (memória) | Banco de testes |

---

## 📚 Conceitos abordados

Este projeto é ideal para estudo de:
- **Clean Architecture** (Domain → Application → Infrastructure → API)
- **Repository Pattern** (interface no domínio, implementação na infraestrutura)
- **Strategy Pattern** (BillingStrategy e suas implementações)
- **Dependency Injection** no FastAPI via `Depends()`
- **ORM com SQLAlchemy 2.x** e mapeamento Model ↔ Entity
- **Testes com Pytest** usando fixtures e banco em memória

---

*Projeto didático — Clean Architecture + SOLID com FastAPI e Python 3.13*
