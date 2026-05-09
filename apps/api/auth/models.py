"""
Kloud Authentication Models
User and subscription management with SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
import enum

Base = declarative_base()


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
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic user information
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Subscription information
    subscription_plan = Column(
        Enum(SubscriptionPlan), 
        default=SubscriptionPlan.FREE,
        nullable=False
    )
    
    # Stripe integration
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # API usage tracking
    api_calls_count = Column(Integer, default=0)
    total_uploads = Column(Integer, default=0)
    storage_used_bytes = Column(Integer, default=0)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user")
    upload_sessions = relationship("UploadSession", back_populates="user")
    jobs = relationship("Job", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', plan='{self.subscription_plan}')>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_active_subscription(self) -> bool:
        """Check if user has active paid subscription"""
        return self.subscription_plan != SubscriptionPlan.FREE


class Subscription(Base):
    """Stripe subscription tracking"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Stripe identifiers
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    stripe_customer_id = Column(String(255), nullable=False)
    
    # Subscription details
    status = Column(Enum(SubscriptionStatus), nullable=False)
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    
    # Billing periods
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Cancellation handling
    cancel_at_period_end = Column(Boolean, default=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return (
            self.status == SubscriptionStatus.ACTIVE and
            self.current_period_end > datetime.now(timezone.utc)
        )


class UploadSession(Base):
    """File upload session tracking"""
    __tablename__ = "upload_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=False)
    
    # Storage information
    s3_key = Column(String(500), nullable=True)
    s3_bucket = Column(String(100), nullable=True)
    
    # Upload status
    status = Column(String(50), default="initiated")  # initiated, uploading, completed, failed
    upload_progress = Column(Numeric(5, 2), default=0.0)  # Percentage
    
    # Processing information
    is_processed = Column(Boolean, default=False)
    processing_job_id = Column(String(255), nullable=True)
    
    # Metadata
    upload_metadata = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="upload_sessions")
    
    def __repr__(self):
        return f"<UploadSession(id={self.id}, filename='{self.original_filename}', status='{self.status}')>"


class Job(Base):
    """Processing job tracking"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Job identification
    job_id = Column(String(255), unique=True, nullable=False)
    job_type = Column(String(100), nullable=False)  # analysis, processing, export
    
    # Processing details
    status = Column(String(50), default="queued")  # queued, running, completed, failed, cancelled
    progress = Column(Numeric(5, 2), default=0.0)  # Percentage
    
    # Input/Output
    input_data = Column(Text, nullable=True)  # JSON string
    output_data = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)
    
    # Priority and scheduling
    priority = Column(Integer, default=0)  # Higher number = higher priority
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    
    def __repr__(self):
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
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Key information
    key_name = Column(String(100), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    key_prefix = Column(String(20), nullable=False)  # First few chars for identification
    
    # Permissions and limits
    is_active = Column(Boolean, default=True)
    rate_limit_override = Column(Integer, nullable=True)  # Custom rate limit
    allowed_endpoints = Column(Text, nullable=True)  # JSON array of allowed endpoints
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, name='{self.key_name}', active={self.is_active})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if API key is expired"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at



