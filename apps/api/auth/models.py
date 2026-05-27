"""
Kloud Authentication Models
User and subscription management with SQLAlchemy
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIALING = "trialing"


class User(Base):
    """User model with subscription management"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Basic user information
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Authentication
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Subscription information
    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False
    )

    # Stripe integration
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # API usage tracking
    api_calls_count: Mapped[int] = mapped_column(Integer, default=0)
    total_uploads: Mapped[int] = mapped_column(Integer, default=0)
    storage_used_bytes: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    subscriptions: Mapped[list[Subscription]] = relationship(
        "Subscription", back_populates="user"
    )
    upload_sessions: Mapped[list[UploadSession]] = relationship(
        "UploadSession", back_populates="user"
    )
    jobs: Mapped[list[Job]] = relationship("Job", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', plan='{self.subscription_plan}')>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def has_active_subscription(self) -> bool:
        """Check if user has active paid subscription"""
        return self.subscription_plan != SubscriptionPlan.FREE


class Subscription(Base):
    """Stripe subscription tracking"""

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    # Stripe identifiers
    stripe_subscription_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    stripe_customer_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Subscription details
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus), nullable=False
    )
    plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(SubscriptionPlan), nullable=False
    )

    # Billing periods
    current_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Cancellation handling
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan}', status='{self.status}')>"

    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return (
            self.status == SubscriptionStatus.ACTIVE
            and self.current_period_end > datetime.now(timezone.utc)
        )


class UploadSession(Base):
    """File upload session tracking"""

    __tablename__ = "upload_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    # File information
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Storage information
    s3_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    s3_bucket: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Upload status
    status: Mapped[str] = mapped_column(
        String(50), default="initiated"
    )  # initiated, uploading, completed, failed
    upload_progress: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0.0
    )  # Percentage

    # Processing information
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_job_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Metadata
    upload_metadata: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON string

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="upload_sessions")

    def __repr__(self) -> str:
        return f"<UploadSession(id={self.id}, filename='{self.original_filename}', status='{self.status}')>"


class Job(Base):
    """Processing job tracking"""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    # Job identification
    job_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    job_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # analysis, processing, export

    # Processing details
    status: Mapped[str] = mapped_column(
        String(50), default="queued"
    )  # queued, running, completed, failed, cancelled
    progress: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)  # Percentage

    # Input/Output
    input_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    output_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Priority and scheduling
    priority: Mapped[int] = mapped_column(
        Integer, default=0
    )  # Higher number = higher priority
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="jobs")

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, job_id='{self.job_id}', status='{self.status}')>"

    @property
    def is_running(self) -> bool:
        """Check if job is currently running"""
        return self.status == "running"

    @property
    def is_completed(self) -> bool:
        """Check if job is completed (successfully or with error)"""
        return self.status in ["completed", "failed", "cancelled"]


class APIKey(Base):
    """API key management for programmatic access"""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    # Key information
    key_name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    key_prefix: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # First few chars for identification

    # Permissions and limits
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_limit_override: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # Custom rate limit
    allowed_endpoints: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON array of allowed endpoints

    # Usage tracking
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<APIKey(id={self.id}, name='{self.key_name}', active={self.is_active})>"
        )

    @property
    def is_expired(self) -> bool:
        """Check if API key is expired"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at
