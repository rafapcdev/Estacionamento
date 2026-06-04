"""
Sistema de Estacionamento — Ponto de entrada da aplicação

Inicializa o FastAPI, registra os routers e garante que
as tabelas do banco de dados existem antes de servir as requisições.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables
from app.controllers.vehicle_controller import router as vehicle_router
from app.controllers.parking_spot_controller import router as spot_router
from app.controllers.ticket_controller import router as ticket_router
from app.controllers.monthly_customer_controller import router as monthly_router


# ─────────────────────────────────────────────
# Lifespan: cria tabelas na inicialização
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executa tarefas de startup e shutdown."""
    create_tables()
    yield
    # shutdown: nada a fazer por enquanto


# ─────────────────────────────────────────────
# Instância principal do FastAPI
# ─────────────────────────────────────────────
app = FastAPI(
    title="Parking System API",
    description=(
        "API REST para gerenciamento de estacionamento. "
        "Desenvolvida com **Clean Architecture** e **SOLID** como projeto didático."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Parking System",
        "url": "https://github.com",
    },
    license_info={
        "name": "MIT",
    },
)

# ─────────────────────────────────────────────
# CORS (permite chamadas de qualquer origem em dev)
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Registro de routers
# ─────────────────────────────────────────────
app.include_router(vehicle_router, prefix="/api/v1")
app.include_router(spot_router, prefix="/api/v1")
app.include_router(ticket_router, prefix="/api/v1")
app.include_router(monthly_router, prefix="/api/v1")


# ─────────────────────────────────────────────
# Health-check
# ─────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Verifica se a API está no ar."""
    return {"status": "ok", "service": "Parking System API"}
