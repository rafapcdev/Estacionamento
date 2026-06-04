# 🅿️ Documentação Completa do Sistema de Estacionamento (Arquitetura em Camadas)

Bem-vindo(a) ao guia completo do **Parking System**. Este documento foi projetado para te pegar pela mão e explicar **cada engrenagem** deste sistema. Se você está chegando agora, leia com atenção.

Usamos **Python 3.13**, **FastAPI**, **PostgreSQL** e **Docker**. Toda a arquitetura foi desenhada usando a clássica **Arquitetura em Camadas (Layered MVC Architecture)** para garantir organização com baixa complexidade, além de respeitar os princípios da Orientação a Objetos (POO) e SOLID.

---

## 🏛️ A Estrutura de Pastas (O MVC Moderno)

Diferente do código "espaguete" de um arquivo só, separamos as responsabilidades do sistema em 4 pastas simples e lógicas. Essa é uma estrutura consagrada no mercado para não perder o controle do projeto:

1. **`models/` (Modelos + POO):** Onde o banco de dados (SQLAlchemy) e as regras de negócio puras se encontram. Uma vaga não tem apenas as colunas `numero` e `tipo`, ela tem também a função `ocupar()`. Tudo num só lugar.
2. **`repositories/` (Repositórios):** Onde isolamos as Queries de banco de dados. O resto do sistema não precisa saber como fazer um `SELECT` no PostgreSQL, ele apenas chama o `IVehicleRepository.find_by_plate()`. (Isso é a letra "D" e "I" do SOLID).
3. **`services/` (Serviços / Casos de Uso):** O cérebro da operação. Onde pegamos o `EntryService` e ditamos a regra: "Verifique se é mensalista; ache uma vaga; ocupe a vaga; crie um ticket; salve no banco". Tudo via Injeção de Dependência.
4. **`controllers/` (Rotas da API):** É o ponto de contato com a internet. O FastAPI atende a requisição HTTP aqui e imediatamente passa a bola para o `Service` correto.

---

## 📊 Diagrama de Classes Completo (MVC)

O diagrama abaixo mostra como a arquitetura Layered MVC está organizada, dividindo perfeitamente as responsabilidades de Banco de Dados, Regras de Negócio e HTTP:

```mermaid
classDiagram
    %% ==========================================
    %% MODELS (M) - SQLAlchemy + POO
    %% ==========================================
    class VehicleType {
        <<enumeration>>
        CAR
        MOTORCYCLE
        TRUCK
    }

    class SpotType {
        <<enumeration>>
        COMMON
        ELDERLY
        PCD
        MOTORCYCLE
    }

    class Vehicle {
        +String id
        +String plate
        +VehicleType vehicle_type
        +__init__()
        +validate()
    }

    class ParkingSpot {
        +String id
        +String spot_number
        +SpotType spot_type
        +Boolean occupied
        +occupy()
        +release()
        +is_available()
    }

    class Ticket {
        +String id
        +String vehicle_plate
        +String parking_spot_id
        +datetime entry_time
        +datetime exit_time
        +Decimal amount
        +__init__()
        +close(exit_time, amount)
        +is_closed()
        +duration_in_hours()
    }

    class MonthlyCustomer {
        +String id
        +String name
        +String plate
        +Boolean active
        +__init__()
        +validate()
        +activate()
        +deactivate()
    }
    
    Vehicle "1" -- "1" VehicleType : has
    ParkingSpot "1" -- "1" SpotType : has

    %% ==========================================
    %% ESTRATÉGIAS (S) - Cobrança
    %% ==========================================
    class BillingStrategy {
        <<interface>>
        +String name
        +calculate(duration_hours: float) Decimal
    }
    class HourlyBilling {
        -Decimal _price_per_hour
        +calculate(duration_hours) Decimal
    }
    class FixedBilling {
        -Decimal _fixed_amount
        +calculate(duration_hours) Decimal
    }
    class DailyBilling {
        -Decimal _price_per_day
        +calculate(duration_hours) Decimal
    }
    
    BillingStrategy <|.. HourlyBilling
    BillingStrategy <|.. FixedBilling
    BillingStrategy <|.. DailyBilling

    %% ==========================================
    %% REPOSITORIES (R) - Acesso ao Banco de Dados
    %% ==========================================
    class IVehicleRepository {
        <<interface>>
        +save(Vehicle) Vehicle
        +find_by_plate(String) Vehicle?
    }
    class IParkingSpotRepository {
        <<interface>>
        +find_available_by_type(SpotType) ParkingSpot?
        +lock_available_by_type(SpotType) ParkingSpot?
        +save(ParkingSpot) ParkingSpot
    }
    class ITicketRepository {
        <<interface>>
        +find_open_by_plate(String) Ticket?
        +save(Ticket) Ticket
    }
    class IMonthlyCustomerRepository {
        <<interface>>
        +find_by_plate(String) MonthlyCustomer?
        +save(MonthlyCustomer) MonthlyCustomer
    }

    class SQLAlchemyVehicleRepository
    class SQLAlchemyParkingSpotRepository
    class SQLAlchemyTicketRepository
    class SQLAlchemyMonthlyCustomerRepository

    IVehicleRepository <|.. SQLAlchemyVehicleRepository
    IParkingSpotRepository <|.. SQLAlchemyParkingSpotRepository
    ITicketRepository <|.. SQLAlchemyTicketRepository
    IMonthlyCustomerRepository <|.. SQLAlchemyMonthlyCustomerRepository

    %% ==========================================
    %% SERVICES (S) - Regras de Negócio
    %% ==========================================
    class EntryService {
        -IParkingSpotRepository _spots
        -ITicketRepository _tickets
        -MonthlyCustomerService _monthly
        +register_entry(Vehicle, SpotType?) Ticket
    }
    class ExitService {
        -IParkingSpotRepository _spots
        -ITicketRepository _tickets
        -BillingService _billing
        -MonthlyCustomerService _monthly
        +register_exit(plate: String) Ticket
    }
    class BillingService {
        -BillingStrategy _strategy
        +calculate(duration_hours: float) Decimal
    }

    EntryService ..> IParkingSpotRepository : usa
    EntryService ..> ITicketRepository : usa
    ExitService ..> IParkingSpotRepository : usa
    ExitService ..> ITicketRepository : usa
    ExitService ..> BillingService : usa
    BillingService o-- BillingStrategy : delega para

    %% ==========================================
    %% CONTROLLERS (C) - Endpoints HTTP da API
    %% ==========================================
    class VehicleController {
        +POST /api/v1/vehicles
        +GET /api/v1/vehicles
    }
    class ParkingSpotController {
        +POST /api/v1/spots
        +GET /api/v1/spots/available
    }
    class TicketController {
        +POST /api/v1/tickets/entry
        +POST /api/v1/tickets/exit
    }
    class MonthlyCustomerController {
        +POST /api/v1/monthly-customers
        +PATCH /api/v1/monthly-customers/{id}/activate
    }

    TicketController ..> EntryService : chama
    TicketController ..> ExitService : chama
```

---

## 📡 Guia de Endpoints da API REST

> 💡 **Dica de Ouro:** Você pode testar e brincar com todos esses endpoints através de uma interface visual clicando em **http://localhost:8000/docs** no seu navegador, caso o Docker já esteja rodando.

### 🚗 1. Tickets (O Coração do Fluxo) — `/api/v1/tickets`

| Método | Rota | O que faz? (Explicação Estagiário-Friendly) |
| :--- | :--- | :--- |
| **POST** | `/entry` | **Registra a entrada de um veículo**. Você manda a Placa. O sistema verifica se é mensalista, acha uma vaga livre, "tranca" ela (`SKIP LOCKED` no banco), e devolve um Ticket Aberto. |
| **POST** | `/exit` | **Registra a saída**. Manda a Placa. O sistema acha o ticket aberto, calcula o preço (zero se for mensalista), fecha o ticket e libera a vaga física. |

### 🅿️ 2. Vagas de Estacionamento — `/api/v1/spots`

| Método | Rota | O que faz? (Explicação Estagiário-Friendly) |
| :--- | :--- | :--- |
| **POST** | `/` | **Cria uma vaga nova** no banco. Você passa o número (ex: "B-22") e o tipo (ex: "pcd"). |
| **GET** | `/available`| Mostra apenas as vagas que estão 100% livres e prontas para uso. |

### 💳 3. Clientes Mensalistas — `/api/v1/monthly-customers`

| Método | Rota | O que faz? (Explicação Estagiário-Friendly) |
| :--- | :--- | :--- |
| **POST** | `/` | **Cadastra um mensalista**. Você informa Nome e Placa. O carro dessa placa agora passa livre (R$ 0,00) na saída. |
| **PATCH**| `/{id}/deactivate`| Cancela ou suspende o plano. Se o cara entrar, vai ter que pagar por hora como qualquer pessoa normal. |

---

## 🏎️ Como a Entrada Evita Bater Carros Virtuais (`SKIP LOCKED`)

Quando programamos para web, imagine que **duas catracas abrem exatamente no mesmo milissegundo** e ambos os motoristas apertam o botão de ticket. 

1. **O Problema Clássico:** 
   Ambas as catracas olham para o banco e veem a "Vaga 1" livre. **Boom! 💥 Duas pessoas são enviadas para a mesma vaga.**

2. **A Solução Elegante (`lock_available_by_type` no Repositório):**
   Nós resolvemos isso na raiz do banco de dados (PostgreSQL) usando uma magia chamada `FOR UPDATE SKIP LOCKED`.
   - Quando a Catraca 1 pede uma vaga livre, ela **TRACA (lock)** aquela linha da Vaga 1 na mesma fração de segundo. 
   - Quando a Catraca 2 pede uma vaga 1 milissegundo depois, a query vê que a Vaga 1 está trancada, **PULA (skip)** para a linha de baixo e devolve a Vaga 2.

---

## 🐳 Cheatsheet do Desenvolvedor (Comandos)

Para você copiar e colar e não perder tempo.

**Ligar Tudo (Banco + API):**
```bash
docker compose up -d
```

**Parar Tudo:**
```bash
docker compose down
```

**Ver os logs em tempo real (se algo quebrou):**
```bash
docker compose logs -f api
```

**Rodar TODOS os testes automatizados (Temos 59 deles passando!):**
```bash
# Rodar com Docker:
docker compose --profile test run --rm tests

# Rodar localmente no seu terminal:
.venv/bin/python -m pytest
```
