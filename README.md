# 🅿️ Parking System API

API REST para gerenciamento de estacionamento, desenvolvida como **projeto didático** com foco em:

- **Arquitetura em Camadas (Layered MVC)**
- **SOLID Principles**
- **Repository Pattern**
- **Strategy Pattern**
- **Dependency Injection**

---

## 📐 Arquitetura

O projeto foi migrado de uma Clean Architecture verbosa para uma arquitetura em camadas mais direta (Layered MVC), focada em simplicidade sem abrir mão das boas práticas de Engenharia de Software.

```
parking-system/
├── app/
│   ├── models/                  ← Modelos SQLAlchemy fundidos com regras de negócio (POO)
│   ├── repositories/            ← Interfaces e implementação de persistência no DB
│   ├── services/                ← Casos de uso e regras de negócio (Estratégias de Cobrança)
│   ├── controllers/             ← Endpoints HTTP (FastAPI routers)
│   ├── schemas/                 ← Pydantic schemas (Validação de request/response)
│   ├── database.py              ← Configuração do SQLAlchemy
│   └── dependencies.py          ← Injeção de dependências do FastAPI
│
├── tests/                       ← Pytest (59 testes com SQLite em memória)
├── main.py                      ← Ponto de entrada da aplicação
├── requirements.txt
├── pyproject.toml               ← Configuração do pytest
└── .env.example
```

---

## 🧱 Princípios SOLID aplicados

| Princípio | Onde é aplicado |
|-----------|----------------|
| **SRP** — Single Responsibility | O banco de dados fica no `Repository`, o HTTP fica no `Controller`, a regra central fica no `Service`. |
| **OCP** — Open/Closed | `BillingStrategy` permite adicionar novas formas de cobrança sem alterar código existente. |
| **LSP** — Liskov Substitution | `HourlyBilling`, `FixedBilling` e `DailyBilling` são intercambiáveis onde `BillingStrategy` é esperado. |
| **ISP** — Interface Segregation | Repositórios separados por entidade: `IVehicleRepository`, `IParkingSpotRepository`, etc. |
| **DIP** — Dependency Inversion | Controllers e Services dependem das interfaces de Repositório, e não das tabelas. |

---

## 🗂️ Modelos e POO

Em vez de entidades anêmicas, nossos modelos SQLAlchemy possuem comportamentos (Orientação a Objetos rica):

### ParkingSpot
```python
spot = ParkingSpot(spot_number="A-01", spot_type=SpotType.COMMON)
spot.occupy()  # Regra de negócio executada pelo próprio objeto
```

### Ticket
```python
ticket.close(exit_time=agora, amount=Decimal("20.00"))
duracao = ticket.duration_in_hours()
```

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

---

## 🖥️ Como executar localmente (sem Docker)

### 1. Pré-requisitos
- Python 3.13+
- PostgreSQL rodando localmente

### 2. Configurar ambiente
```bash
cd parking-system
python -m venv .venv
source .venv/bin/activate       # Linux/macOS

pip install -r requirements.txt
cp .env.example .env
```

### 3. Iniciar o servidor
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Executar testes

Os testes usam **SQLite em memória** — não é necessário PostgreSQL.
Atualmente, temos **59 testes automatizados (E2E e Unitários)** testando desde a cobrança até concorrência de catracas (`SKIP LOCKED`).

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

*Projeto didático — Layered MVC + SOLID com FastAPI e Python 3.13*
