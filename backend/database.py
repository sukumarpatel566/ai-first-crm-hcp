import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Database URL is expected in the environment; defaults to SQLite for local dev.
# SQLite is used to avoid native build dependencies (psycopg2) on Windows + Python 3.13.
# For production, you can override with: DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ai_first_crm_hcp.db",
)

# SQLAlchemy engine configuration
# For SQLite, we need check_same_thread=False to work with FastAPI's async nature
# and connect_args to ensure thread-safe operation
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
)

# Scoped session factory for thread-safe database access
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db() -> Generator:
    """
    FastAPI dependency that provides a SQLAlchemy session and
    ensures it is closed after the request is handled.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

