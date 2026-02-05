from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TaskRun(Base):
    __tablename__ = "task_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    client_id: Mapped[str] = mapped_column(String(128))
    workflow_type: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
