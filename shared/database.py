"""
Async SQLAlchemy 2.0 database setup for HD Platform.

Provides:
- AsyncEngine and async_sessionmaker (PostgreSQL)
- Base declarative class for models
- User, APIKey, and UsageLog ORM models
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    JSON,
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
    "__SET_DATABASE_URL__",
)


def _create_engine() -> Optional[AsyncEngine]:
    """Create and return an async SQLAlchemy engine, or None if DB unavailable."""
    try:
        if not DATABASE_URL or DATABASE_URL.startswith("__SET_"):
            return None
        kwargs = {}
        if not DATABASE_URL.startswith("sqlite"):
            kwargs["pool_size"] = 20
            kwargs["max_overflow"] = 10
            kwargs["pool_pre_ping"] = True
        return create_async_engine(
            DATABASE_URL,
            echo=False,
            **kwargs
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
    subscription_status: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, default="inactive"
    )
    access_status: Mapped[str] = mapped_column(String(50), nullable=False, default="paid")
    trial_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deletion_scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    demo_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    demo_renewal_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    demo_last_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    demo_deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    coaching_container_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    coach_review_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    coach_review_consent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    coach_review_consent_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    coach_review_consent_revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    guide_name: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    guide_name_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", back_populates="user")
    invitations: Mapped[list["Invitation"]] = relationship("Invitation", back_populates="user")
    bot_instance: Mapped[Optional["BotInstance"]] = relationship(
        "BotInstance", back_populates="user", uselist=False
    )

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


class Invitation(Base):
    """Stores short-lived tokens to link anonymous checkout sessions to a Telegram User ID."""

    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=24),
    )

    user: Mapped["User"] = relationship("User", back_populates="invitations")


class BotInstance(Base):
    """Tracks provisioning status, workspace location, and resource metrics of the guest bot container."""

    __tablename__ = "bot_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)
    telegram_user_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    container_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    workspace_path: Mapped[str] = mapped_column(String(500), nullable=False)
    api_key_limits: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="provisioning")
    host_node_ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="100.90.63.4")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="bot_instance")


async def init_db() -> None:
    """Create all tables (idempotent, for development / first-run)."""
    if engine is None:
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Run manual migration to add is_premium and coaching_container_end columns if missing
    from sqlalchemy import text
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT FALSE"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN access_status VARCHAR(50) DEFAULT 'paid' NOT NULL"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN trial_expires_at TIMESTAMP WITH TIME ZONE"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN deactivated_at TIMESTAMP WITH TIME ZONE"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN deletion_scheduled_at TIMESTAMP WITH TIME ZONE"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN demo_started_at TIMESTAMP WITH TIME ZONE"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN demo_renewal_count INTEGER DEFAULT 0 NOT NULL"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN demo_last_source VARCHAR(100)"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN demo_deleted_at TIMESTAMP WITH TIME ZONE"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN coaching_container_end TIMESTAMP WITH TIME ZONE"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN coach_review_consent BOOLEAN DEFAULT FALSE NOT NULL"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN coach_review_consent_at TIMESTAMP WITH TIME ZONE"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN coach_review_consent_source VARCHAR(100)"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN coach_review_consent_revoked_at TIMESTAMP WITH TIME ZONE"))
        except Exception:
            pass


async def close_db() -> None:
    """Gracefully dispose of the engine connection pool."""
    if engine is not None:
        await engine.dispose()
