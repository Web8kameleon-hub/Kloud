"""
Kloud Cloud Settings
Industrial-grade configuration with Stripe integration and plan quotas
"""
import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field, validator
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class SubscriptionPlan(str, Enum):
    FREE = "free"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Settings(BaseSettings):
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = Field(default=True)
    
    # API Configuration
    api_title: str = "Kloud Cloud API"
    api_version: str = "1.0.0"
    api_description: str = "Industrial AI-Powered Neurological Analysis Platform"
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://Kloud:secure123@localhost:5432/Kloud_db"
    )
    database_echo: bool = Field(default=False)
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # Security
    secret_key: str = Field(
        default="your-super-secure-secret-key-change-in-production",
        min_length=32
    )
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Stripe Configuration
    stripe_publishable_key: str = Field(default="pk_test_...")
    stripe_secret_key: str = Field(default="sk_test_...")
    stripe_webhook_secret: str = Field(default="whsec_...")
    stripe_success_url: str = Field(default="https://app.Kloud.com/success")
    stripe_cancel_url: str = Field(default="https://app.Kloud.com/cancel")
    
    # Stripe Price IDs (Set these in your environment or .env file)
    stripe_price_standard: str = Field(default="price_standard_monthly")
    stripe_price_professional: str = Field(default="price_professional_monthly")
    stripe_price_enterprise: str = Field(default="price_enterprise_monthly")
    
    # File Storage
    s3_bucket: str = Field(default="Kloud-uploads")
    s3_access_key: str = Field(default="")
    s3_secret_key: str = Field(default="")
    s3_endpoint_url: Optional[str] = Field(default="http://localhost:9000")  # MinIO for local dev
    s3_region: str = Field(default="us-east-1")
    
    # File Upload Limits
    max_file_size_mb: int = 100
    allowed_file_types: List[str] = [
        "audio/wav", "audio/mpeg", "audio/mp4",
        "application/edf", "application/octet-stream"  # EEG files
    ]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # OpenTelemetry
    jaeger_endpoint: Optional[str] = Field(default="http://localhost:14268/api/traces")
    enable_tracing: bool = Field(default=True)
    
    # Subscription Plan Quotas and Features
    plan_quotas: Dict[str, Dict] = {
        "free": {
            "max_uploads_per_month": 5,
            "max_file_size_mb": 10,
            "max_concurrent_jobs": 1,
            "max_storage_gb": 1,
            "api_calls_per_hour": 100,
            "priority_processing": False,
            "advanced_analytics": False,
            "webhook_notifications": False,
            "export_formats": ["json"],
            "support_level": "community"
        },
        "standard": {
            "max_uploads_per_month": 100,
            "max_file_size_mb": 50,
            "max_concurrent_jobs": 3,
            "max_storage_gb": 10,
            "api_calls_per_hour": 1000,
            "priority_processing": False,
            "advanced_analytics": True,
            "webhook_notifications": True,
            "export_formats": ["json", "csv", "pdf"],
            "support_level": "email"
        },
        "professional": {
            "max_uploads_per_month": 500,
            "max_file_size_mb": 100,
            "max_concurrent_jobs": 10,
            "max_storage_gb": 100,
            "api_calls_per_hour": 5000,
            "priority_processing": True,
            "advanced_analytics": True,
            "webhook_notifications": True,
            "export_formats": ["json", "csv", "pdf", "xml", "dicom"],
            "support_level": "priority"
        },
        "enterprise": {
            "max_uploads_per_month": -1,  # Unlimited
            "max_file_size_mb": 500,
            "max_concurrent_jobs": 50,
            "max_storage_gb": 1000,
            "api_calls_per_hour": 25000,
            "priority_processing": True,
            "advanced_analytics": True,
            "webhook_notifications": True,
            "export_formats": ["json", "csv", "pdf", "xml", "dicom", "matlab"],
            "support_level": "dedicated",
            "custom_integrations": True,
            "white_label": True,
            "sla_guarantee": "99.9%"
        }
    }
    
    # Stripe Plan Mapping
    stripe_plan_mapping: Dict[str, str] = {
        "price_standard_monthly": "standard",
        "price_professional_monthly": "professional", 
        "price_enterprise_monthly": "enterprise"
    }
    
    # Worker Configuration
    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")
    
    # Processing Configuration
    max_processing_time_seconds: int = 1800  # 30 minutes
    processing_timeout_seconds: int = 300    # 5 minutes for individual tasks
    
    # Email Configuration (for notifications)
    smtp_server: Optional[str] = Field(default="smtp.gmail.com")
    smtp_port: int = 587
    smtp_username: Optional[str] = Field(default="")
    smtp_password: Optional[str] = Field(default="")
    smtp_use_tls: bool = True
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default="")
    log_level: str = Field(default="INFO")
    
    @validator("environment", pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator("debug")
    def validate_debug(cls, v, values):
        if "environment" in values:
            return values["environment"] == Environment.DEVELOPMENT
        return v
    
    def get_plan_quota(self, plan: str, quota_key: str, default=None):
        """Get specific quota value for a plan"""
        return self.plan_quotas.get(plan, {}).get(quota_key, default)
    
    def is_feature_enabled(self, plan: str, feature: str) -> bool:
        """Check if a feature is enabled for a specific plan"""
        return self.plan_quotas.get(plan, {}).get(feature, False)
    
    def get_stripe_price_id(self, plan: str) -> Optional[str]:
        """Get Stripe price ID for a plan"""
        plan_to_price = {
            "standard": self.stripe_price_standard,
            "professional": self.stripe_price_professional,
            "enterprise": self.stripe_price_enterprise
        }
        return plan_to_price.get(plan)
    
    def get_plan_from_price_id(self, price_id: str) -> str:
        """Get plan name from Stripe price ID"""
        return self.stripe_plan_mapping.get(price_id, "free")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Export commonly used values
DATABASE_URL = settings.database_url
REDIS_URL = settings.redis_url
SECRET_KEY = settings.secret_key
STRIPE_SECRET_KEY = settings.stripe_secret_key
STRIPE_PUBLISHABLE_KEY = settings.stripe_publishable_key



