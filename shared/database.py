"""
Async SQLAlchemy 2.0 database setup for HD Platform.

Provides:
- AsyncEngine and async_sessionmaker (PostgreSQL)
- Base declarative class for models
- User, APIKey, and UsageLog ORM models
"""

import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://hduser:hdpassword@localhost:5432/hdplatform",
)


def _create_engine() -> Optional[AsyncEngine]:
    """Create and return an async SQLAlchemy engine, or None if DB unavailable."""
    try:
        return create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
        )
    except Exception:
        return None


engine: Optional[AsyncEngine] = _create_engine()

if engine is not None:
    async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
else:
    async_session_factory = None  # type: ignore


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class User(Base):
    """Platform user account."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email!r})>"


class APIKey(Base):
    """API key linked to a user with a usage tier and rate limit."""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tier: Mapped[str] = mapped_column(
        String(50), nullable=False, default="free"
    )  # free | pro | enterprise
    rate_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="api_keys")
    usage_logs: Mapped[list["UsageLog"]] = relationship("UsageLog", back_populates="api_key")

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name={self.name!r}, tier={self.tier!r})>"


class UsageLog(Base):
    """Per-request usage audit log."""

    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    api_key_id: Mapped[int] = mapped_column(ForeignKey("api_keys.id"), nullable=False, index=True)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    api_key: Mapped["APIKey"] = relationship("APIKey", back_populates="usage_logs")

    def __repr__(self) -> str:
        return f"<UsageLog(id={self.id}, endpoint={self.endpoint!r})>"


async def init_db() -> None:
    """Create all tables (idempotent, for development / first-run)."""
    if engine is None:
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Gracefully dispose of the engine connection pool."""
    if engine is not None:
        await engine.dispose()
