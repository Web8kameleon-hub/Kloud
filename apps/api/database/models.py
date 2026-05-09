# ðŸš€ Kloud PRODUCTION DATABASE MODELS
# Industrial-Grade SQLAlchemy Models with Real Relationships
# Production PostgreSQL Schema, Real Business Logic

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON, Enum as SQLEnum, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime, timedelta
from enum import Enum
import uuid

Base = declarative_base()

# Enums for type safety
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    ANALYST = "analyst"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    SEPA = "sepa"
    PAYPAL = "paypal"
    KLARNA = "klarna"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"

class FileUploadStatus(str, Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DELETED = "deleted"

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(str, Enum):
    AUDIO_ANALYSIS = "audio_analysis"
    VIDEO_PROCESSING = "video_processing"
    FILE_CONVERSION = "file_conversion"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    CONTENT_MODERATION = "content_moderation"

# ðŸ‘¤ USER MANAGEMENT
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Profile information
    avatar_url = Column(String(500))
    bio = Column(Text)
    preferences = Column(JSONB)
    
    # Relationships
    file_uploads = relationship("FileUpload", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_role', 'role'),
        Index('idx_users_created', 'created_at'),
    )

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500), unique=True, nullable=False, index=True)
    
    # Session metadata
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    device_info = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_used = Column(DateTime, default=datetime.utcnow)
    
    # Security
    is_active = Column(Boolean, default=True, nullable=False)
    revoked_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_sessions_user_active', 'user_id', 'is_active'),
        Index('idx_sessions_expires', 'expires_at'),
    )

# ðŸ’° PAYMENT SYSTEM
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR", nullable=False)
    method = Column(SQLEnum(PaymentMethod), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # External references
    external_id = Column(String(255), index=True)  # PayPal, Klarna, etc. transaction ID
    gateway_reference = Column(String(255))
    
    # Payment method specific data
    payment_data = Column(JSONB)  # SEPA IBAN, PayPal details, etc.
    
    # Metadata
    description = Column(String(500))
    payment_metadata = Column(JSONB)
    
    # Webhook verification
    webhook_received = Column(Boolean, default=False)
    webhook_verified = Column(Boolean, default=False)
    webhook_data = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    # Indexes
    __table_args__ = (
        Index('idx_payments_user_status', 'user_id', 'status'),
        Index('idx_payments_method', 'method'),
        Index('idx_payments_external_id', 'external_id'),
        Index('idx_payments_created', 'created_at'),
    )

# ðŸ“ FILE MANAGEMENT
class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # File information
    original_name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False, index=True)
    mimetype = Column(String(100), nullable=False, index=True)
    file_size = Column(Integer, nullable=False)
    
    # Storage information
    file_path = Column(String(1000))
    s3_key = Column(String(1000), index=True)
    s3_bucket = Column(String(100))
    s3_region = Column(String(50))
    
    # File integrity
    checksum_md5 = Column(String(32))
    checksum_sha256 = Column(String(64), index=True)
    
    # Status and metadata
    status = Column(SQLEnum(FileUploadStatus), default=FileUploadStatus.UPLOADING, nullable=False)
    file_metadata = Column(JSONB)  # File-specific metadata (dimensions, duration, etc.)
    
    # Processing results
    thumbnails = Column(JSONB)  # Array of thumbnail info
    processing_results = Column(JSONB)
    processing_errors = Column(JSONB)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime)
    expires_at = Column(DateTime)  # For temporary files
    
    # Relationships
    user = relationship("User", back_populates="file_uploads")
    jobs = relationship("Job", back_populates="file_upload", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_files_user_status', 'user_id', 'status'),
        Index('idx_files_mimetype', 'mimetype'),
        Index('idx_files_uploaded', 'uploaded_at'),
        Index('idx_files_expires', 'expires_at'),
    )

# ðŸ”§ JOB PROCESSING
class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_upload_id = Column(UUID(as_uuid=True), ForeignKey("file_uploads.id", ondelete="CASCADE"))
    
    # Job details
    job_type = Column(SQLEnum(JobType), nullable=False, index=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.QUEUED, nullable=False, index=True)
    priority = Column(Integer, default=0)  # Higher number = higher priority
    
    # Job configuration
    parameters = Column(JSONB)  # Job-specific parameters
    
    # Processing information
    worker_id = Column(String(100))  # Which worker is processing this job
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Results and errors
    result = Column(JSONB)
    error_message = Column(Text)
    error_details = Column(JSONB)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    progress_message = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    retry_after = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    file_upload = relationship("FileUpload", back_populates="jobs")
    
    # Indexes
    __table_args__ = (
        Index('idx_jobs_status_priority', 'status', 'priority'),
        Index('idx_jobs_user_type', 'user_id', 'job_type'),
        Index('idx_jobs_created', 'created_at'),
        Index('idx_jobs_retry', 'retry_after'),
    )

# ðŸ“Š SYSTEM MONITORING
class SystemMetric(Base):
    __tablename__ = "system_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metric identification
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # cpu, memory, disk, network, custom
    
    # Metric values
    value = Column(Float, nullable=False)
    unit = Column(String(20))  # %, bytes, count, seconds, etc.
    
    # Context
    hostname = Column(String(100), index=True)
    service = Column(String(50), index=True)
    environment = Column(String(20), default="production")
    
    # Additional data
    labels = Column(JSONB)  # Additional labels for filtering/grouping
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_metrics_name_time', 'metric_name', 'timestamp'),
        Index('idx_metrics_service_time', 'service', 'timestamp'),
        Index('idx_metrics_host_time', 'hostname', 'timestamp'),
    )

# ðŸ“‹ AUDIT LOGS
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(100), index=True)
    
    # Request context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    request_id = Column(String(100), index=True)
    
    # Changes
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    
    # Metadata
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text)
    duration_ms = Column(Integer)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_action_time', 'action', 'timestamp'),
        Index('idx_audit_entity_time', 'entity_type', 'entity_id', 'timestamp'),
        Index('idx_audit_user_time', 'user_id', 'timestamp'),
    )

# ðŸ”— API INTEGRATIONS
class APIIntegration(Base):
    __tablename__ = "api_integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Integration details
    name = Column(String(100), nullable=False, unique=True)
    provider = Column(String(50), nullable=False)  # paypal, aws, google, etc.
    
    # Configuration
    config = Column(JSONB, nullable=False)  # API keys, endpoints, etc.
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_healthy = Column(Boolean, default=True, nullable=False)
    
    # Health check
    last_health_check = Column(DateTime)
    health_check_interval = Column(Integer, default=300)  # seconds
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    
    # Usage statistics
    request_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_integrations_provider', 'provider'),
        Index('idx_integrations_health', 'is_healthy', 'last_health_check'),
    )

# Helper functions for common queries
def get_active_users(session: Session):
    """Get all active users"""
    return session.query(User).filter(User.is_active == True).all()

def get_user_by_email(session: Session, email: str):
    """Get user by email"""
    return session.query(User).filter(User.email == email, User.is_active == True).first()

def get_pending_jobs(session: Session, job_type: JobType = None):
    """Get queued jobs, optionally filtered by type"""
    query = session.query(Job).filter(Job.status == JobStatus.QUEUED)
    if job_type:
        query = query.filter(Job.job_type == job_type)
    return query.order_by(Job.priority.desc(), Job.created_at.asc()).all()

def get_user_files(session: Session, user_id: str, status: FileUploadStatus = None):
    """Get user's files, optionally filtered by status"""
    query = session.query(FileUpload).filter(FileUpload.user_id == user_id)
    if status:
        query = query.filter(FileUpload.status == status)
    return query.order_by(FileUpload.uploaded_at.desc()).all()

def get_recent_payments(session: Session, user_id: str = None, days: int = 30):
    """Get recent payments"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    query = session.query(Payment).filter(Payment.created_at >= cutoff)
    if user_id:
        query = query.filter(Payment.user_id == user_id)
    return query.order_by(Payment.created_at.desc()).all()



