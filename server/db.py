import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def _build_database_url() -> str:
    host = os.environ.get("POSTGRES_HOST", "postgres")
    port = os.environ.get("POSTGRES_PORT", "5432")
    # The app DB may live under its own least-privilege role, separate from the
    # vector-store DB — e.g. managed Postgres (RDS/Aurora) where each database
    # has an isolated owner role with no cross-DB access. Prefer APP_DB_USER/
    # APP_DB_PASSWORD when set; otherwise fall back to the shared POSTGRES_*
    # credentials (single-role / local docker-compose setups keep working).
    user = os.environ.get("APP_DB_USER") or os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("APP_DB_PASSWORD") or os.environ.get("POSTGRES_PASSWORD", "postgres")
    db = os.environ.get("APP_DB_NAME", "mem0_app")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


engine = create_engine(_build_database_url(), pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a SQLAlchemy session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
