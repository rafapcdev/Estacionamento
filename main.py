"""
Sistema de Estacionamento — Ponto de entrada da aplicação

Inicializa o FastAPI, registra os routers e garante que
as tabelas do banco de dados existem antes de servir as requisições.
"""

from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables
from app.logger import logger
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
        "Desenvolvida com **Layered MVC** e **SOLID** como projeto didático."
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
# Middleware de Logging
# ─────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Registra a chegada da requisição
    logger.info(f"Recebido: {request.method} {request.url.path}")
    
    # Processa a requisição
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f"{process_time:.2f}ms"
    
    # Registra a saída com o status code e tempo
    logger.info(f"Concluído: {request.method} {request.url.path} - Status: {response.status_code} - Tempo: {formatted_process_time}")
    
    return response

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
