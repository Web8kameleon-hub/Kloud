# ðŸš€ Kloud DATABASE CONNECTION
# Production-Grade SQLAlchemy Engine with Real Connection Pooling
# Industrial Redis Caching, Session Management

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import redis
import json
from typing import Optional, Any, Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
class DatabaseConfig:
    def __init__(self):
        # PostgreSQL connection parameters
        self.DB_USER = os.getenv('DB_USER', 'Kloud')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'Kloud123')
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = os.getenv('DB_PORT', '5432')
        self.DB_NAME = os.getenv('DB_NAME', 'Kloud')
        
        # Connection pooling
        self.POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '20'))
        self.MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '30'))
        self.POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        self.POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))
        
        # Redis configuration
        self.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        self.REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
        self.REDIS_DB = int(os.getenv('REDIS_DB', '0'))
        self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
        self.CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour
        
        # Environment
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
        
    @property
    def database_url(self) -> str:
        """Get database URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

config = DatabaseConfig()

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    config.database_url,
    poolclass=QueuePool,
    pool_size=config.POOL_SIZE,
    max_overflow=config.MAX_OVERFLOW,
    pool_timeout=config.POOL_TIMEOUT,
    pool_recycle=config.POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before use
    echo=config.ENVIRONMENT == 'development',  # Log SQL in development
    future=True  # Use SQLAlchemy 2.0 style
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Redis client for caching
redis_client = None
try:
    redis_client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )
    # Test connection
    redis_client.ping()
    logger.info("âœ… Redis connection established")
except Exception as e:
    logger.warning(f"âš ï¸ Redis connection failed: {e}")
    redis_client = None

# Database session dependency
@contextmanager
def get_db_session() -> Session:
    """Get database session with automatic cleanup"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def get_db() -> Session:
    """Get database session for dependency injection"""
    session = SessionLocal()
    try:
        return session
    finally:
        pass  # Session will be closed by FastAPI dependency system

# Cache operations
class CacheManager:
    """Redis cache manager for database queries"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.default_ttl = config.CACHE_TTL
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
            
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.redis:
            return False
            
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            return self.redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis:
            return False
            
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        if not self.redis:
            return 0
            
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
        except Exception as e:
            logger.warning(f"Cache delete pattern error: {e}")
        return 0
    
    def clear_user_cache(self, user_id: str):
        """Clear all cache entries for a user"""
        patterns = [
            f"user:{user_id}:*",
            f"files:{user_id}:*",
            f"payments:{user_id}:*",
            f"jobs:{user_id}:*"
        ]
        
        for pattern in patterns:
            self.delete_pattern(pattern)
    
    def invalidate_model_cache(self, model_name: str, model_id: str = "*"):
        """Invalidate cache for a specific model"""
        pattern = f"{model_name}:{model_id}:*"
        return self.delete_pattern(pattern)

# Initialize cache manager
cache = CacheManager(redis_client)

# Database health check
def check_database_health() -> Dict[str, Any]:
    """Check database connection health"""
    try:
        with get_db_session() as session:
            # Simple query to test connection
            result = session.execute("SELECT 1 as health_check")
            row = result.fetchone()
            
            if row and row[0] == 1:
                return {
                    "database": "healthy",
                    "connection_pool": {
                        "size": engine.pool.size(),
                        "checked_in": engine.pool.checkedin(),
                        "checked_out": engine.pool.checkedout(),
                        "overflow": engine.pool.overflow(),
                        "invalid": engine.pool.invalid()
                    }
                }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "database": "unhealthy",
            "error": str(e)
        }

def check_redis_health() -> Dict[str, Any]:
    """Check Redis connection health"""
    if not redis_client:
        return {"redis": "not_configured"}
        
    try:
        # Ping Redis
        redis_client.ping()
        
        # Get Redis info
        info = redis_client.info()
        
        return {
            "redis": "healthy",
            "version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
            "uptime_in_seconds": info.get("uptime_in_seconds")
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "redis": "unhealthy",
            "error": str(e)
        }

# Query helpers with caching
class QueryHelper:
    """Helper class for common database queries with caching"""
    
    @staticmethod
    def get_user_by_id(user_id: str, use_cache: bool = True) -> Optional[Dict]:
        """Get user by ID with caching"""
        cache_key = f"user:{user_id}"
        
        # Try cache first
        if use_cache:
            cached_user = cache.get(cache_key)
            if cached_user:
                return cached_user
        
        # Query database
        try:
            with get_db_session() as session:
                from app.database.models import User
                user = session.query(User).filter(User.id == user_id, User.is_active == True).first()
                
                if user:
                    user_data = {
                        "id": str(user.id),
                        "email": user.email,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role,
                        "is_verified": user.is_verified,
                        "created_at": user.created_at.isoformat(),
                        "last_login": user.last_login.isoformat() if user.last_login else None
                    }
                    
                    # Cache result
                    if use_cache:
                        cache.set(cache_key, user_data, ttl=1800)  # 30 minutes
                    
                    return user_data
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
        
        return None
    
    @staticmethod
    def get_user_files(user_id: str, limit: int = 50, use_cache: bool = True) -> List[Dict]:
        """Get user files with caching"""
        cache_key = f"files:{user_id}:recent:{limit}"
        
        # Try cache first
        if use_cache:
            cached_files = cache.get(cache_key)
            if cached_files:
                return cached_files
        
        # Query database
        try:
            with get_db_session() as session:
                from app.database.models import FileUpload
                files = session.query(FileUpload).filter(
                    FileUpload.user_id == user_id
                ).order_by(
                    FileUpload.uploaded_at.desc()
                ).limit(limit).all()
                
                files_data = []
                for file in files:
                    files_data.append({
                        "id": str(file.id),
                        "original_name": file.original_name,
                        "filename": file.filename,
                        "mimetype": file.mimetype,
                        "file_size": file.file_size,
                        "status": file.status,
                        "uploaded_at": file.uploaded_at.isoformat(),
                        "processed_at": file.processed_at.isoformat() if file.processed_at else None
                    })
                
                # Cache result
                if use_cache:
                    cache.set(cache_key, files_data, ttl=300)  # 5 minutes
                
                return files_data
        except Exception as e:
            logger.error(f"Error getting files for user {user_id}: {e}")
        
        return []
    
    @staticmethod
    def get_system_stats(use_cache: bool = True) -> Dict[str, Any]:
        """Get system statistics with caching"""
        cache_key = "system:stats"
        
        # Try cache first
        if use_cache:
            cached_stats = cache.get(cache_key)
            if cached_stats:
                return cached_stats
        
        # Query database
        try:
            with get_db_session() as session:
                from app.database.models import User, FileUpload, Payment, Job
                from sqlalchemy import func, text
                
                # Count queries
                total_users = session.query(func.count(User.id)).scalar()
                active_users = session.query(func.count(User.id)).filter(User.is_active == True).scalar()
                total_files = session.query(func.count(FileUpload.id)).scalar()
                total_payments = session.query(func.count(Payment.id)).scalar()
                pending_jobs = session.query(func.count(Job.id)).filter(Job.status == 'queued').scalar()
                
                # Database size (PostgreSQL specific)
                db_size_result = session.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
                db_size = db_size_result.scalar()
                
                stats = {
                    "users": {
                        "total": total_users,
                        "active": active_users
                    },
                    "files": {
                        "total": total_files
                    },
                    "payments": {
                        "total": total_payments
                    },
                    "jobs": {
                        "pending": pending_jobs
                    },
                    "database": {
                        "size": db_size
                    }
                }
                
                # Cache result
                if use_cache:
                    cache.set(cache_key, stats, ttl=60)  # 1 minute
                
                return stats
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
        
        return {}

# Initialize query helper
query_helper = QueryHelper()

# Export commonly used items
__all__ = [
    'engine',
    'SessionLocal',
    'get_db_session',
    'get_db',
    'cache',
    'check_database_health',
    'check_redis_health',
    'query_helper',
    'config'
]



