"""
Infrastructure: Database Configuration

Configura o engine e a sessão do SQLAlchemy 2.x.
Lê a DATABASE_URL do arquivo .env via python-dotenv.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/parking_db",
)


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy."""
    pass


engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db():
    """
    Gerador de sessão para injeção de dependência no FastAPI.

    Uso:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Cria todas as tabelas definidas nos modelos (uso em dev/testes)."""
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Remove todas as tabelas (uso em testes)."""
    Base.metadata.drop_all(bind=engine)
