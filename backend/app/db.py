from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

settings = get_settings()

connect_args = {}
poolclass = None
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    poolclass = StaticPool

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=connect_args,
    poolclass=poolclass,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
