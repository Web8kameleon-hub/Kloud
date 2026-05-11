"""
DNS & Hosting Management API
Multi-tenant DNS zones, records, and origin management.
Integrates with main API at port 8000.
"""

import os
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    Enum as SQLEnum,
    ForeignKey,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from datetime import datetime
import enum
from typing import List, Optional
import uuid

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root:password@kloud-postgres:3306/kloud"
)

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"⚠️ Database connection failed: {e}")
    SessionLocal = None

# Database Models
Base = declarative_base()


class ProxyStatus(str, enum.Enum):
    PROXIED = "Proxied"
    DNS_ONLY = "DNS only"


class RecordType(str, enum.Enum):
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    SOA = "SOA"
    SRV = "SRV"


class OriginHealth(str, enum.Enum):
    HEALTHY = "Healthy"
    WARNING = "Warning"
    DISABLED = "Disabled"


class DNSZone(Base):
    """User DNS zone (domain) model"""

    __tablename__ = "dns_zones"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    status = Column(String(50), default="active")
    nameserver_1 = Column(String(255), default="jonathan.ns.kloud.cloud")
    nameserver_2 = Column(String(255), default="katja.ns.kloud.cloud")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    records = relationship(
        "DNSRecord", back_populates="zone", cascade="all, delete-orphan"
    )


class DNSRecord(Base):
    """Individual DNS record model"""

    __tablename__ = "dns_records"

    id = Column(String(36), primary_key=True)
    zone_id = Column(String(36), ForeignKey("dns_zones.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)  # subdomain or @
    type = Column(SQLEnum(RecordType), nullable=False)
    content = Column(String(1000), nullable=False)
    ttl = Column(Integer, default=3600)
    proxy_status = Column(SQLEnum(ProxyStatus), default=ProxyStatus.DNS_ONLY)
    priority = Column(Integer, nullable=True)  # for MX, SRV
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    zone = relationship("DNSZone", back_populates="records")


class HostingOrigin(Base):
    """Hosting origin/hosting server model"""

    __tablename__ = "hosting_origins"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    endpoint = Column(String(255), nullable=False)  # IP or hostname
    health_status = Column(SQLEnum(OriginHealth), default=OriginHealth.HEALTHY)
    region = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)  # frontend, api, storage, etc.
    last_health_check = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Schemas
from pydantic import BaseModel


class DNSRecordSchema(BaseModel):
    id: Optional[str] = None
    name: str
    type: RecordType
    content: str
    ttl: int = 3600
    proxy_status: ProxyStatus = ProxyStatus.DNS_ONLY
    priority: Optional[int] = None

    class Config:
        from_attributes = True


class DNSZoneSchema(BaseModel):
    id: Optional[str] = None
    domain: str
    status: str = "active"
    nameserver_1: str
    nameserver_2: str
    created_at: Optional[datetime] = None
    records: List[DNSRecordSchema] = []

    class Config:
        from_attributes = True


class HostingOriginSchema(BaseModel):
    id: Optional[str] = None
    name: str
    endpoint: str
    health_status: OriginHealth = OriginHealth.HEALTHY
    region: str
    role: str
    last_health_check: Optional[datetime] = None

    class Config:
        from_attributes = True


# API Router
router = APIRouter(prefix="/api/dns", tags=["dns-hosting"])


def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extract user_id from auth header or use demo user"""
    if authorization:
        try:
            scheme, token = authorization.split(" ")
            if scheme.lower() == "bearer":
                return token
        except ValueError:
            pass
    return "demo-user-001"  # Demo fallback


def get_db() -> Session:
    """Provide database session to endpoints"""
    if SessionLocal is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/zones", response_model=List[DNSZoneSchema])
async def list_dns_zones(
    user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    """List all DNS zones for the authenticated user"""
    zones = db.query(DNSZone).filter(DNSZone.user_id == user_id).all()
    return zones


@router.post("/zones", response_model=DNSZoneSchema)
async def create_dns_zone(
    zone: DNSZoneSchema,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new DNS zone for the user"""
    db_zone = DNSZone(
        id=str(uuid.uuid4()),
        user_id=user_id,
        domain=zone.domain,
        status=zone.status,
        nameserver_1=zone.nameserver_1,
        nameserver_2=zone.nameserver_2,
    )
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.get("/zones/{zone_id}", response_model=DNSZoneSchema)
async def get_dns_zone(
    zone_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a specific DNS zone with all records"""
    zone = (
        db.query(DNSZone)
        .filter(DNSZone.id == zone_id, DNSZone.user_id == user_id)
        .first()
    )
    if not zone:
        raise HTTPException(status_code=404, detail="DNS zone not found")
    return zone


@router.post("/zones/{zone_id}/records", response_model=DNSRecordSchema)
async def create_dns_record(
    zone_id: str,
    record: DNSRecordSchema,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Add a new DNS record to a zone"""
    # Verify zone ownership
    zone = (
        db.query(DNSZone)
        .filter(DNSZone.id == zone_id, DNSZone.user_id == user_id)
        .first()
    )
    if not zone:
        raise HTTPException(status_code=403, detail="Unauthorized")

    db_record = DNSRecord(
        id=str(uuid.uuid4()),
        zone_id=zone_id,
        name=record.name,
        type=record.type,
        content=record.content,
        ttl=record.ttl,
        proxy_status=record.proxy_status,
        priority=record.priority,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.put("/records/{record_id}", response_model=DNSRecordSchema)
async def update_dns_record(
    record_id: str,
    record_update: DNSRecordSchema,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update an existing DNS record"""
    # Verify ownership through zone
    db_record = (
        db.query(DNSRecord)
        .join(DNSZone)
        .filter(DNSRecord.id == record_id, DNSZone.user_id == user_id)
        .first()
    )
    if not db_record:
        raise HTTPException(status_code=403, detail="Unauthorized")

    db_record.name = record_update.name
    db_record.type = record_update.type
    db_record.content = record_update.content
    db_record.ttl = record_update.ttl
    db_record.proxy_status = record_update.proxy_status
    db_record.priority = record_update.priority
    db_record.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/records/{record_id}")
async def delete_dns_record(
    record_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete a DNS record"""
    # Verify ownership through zone
    db_record = (
        db.query(DNSRecord)
        .join(DNSZone)
        .filter(DNSRecord.id == record_id, DNSZone.user_id == user_id)
        .first()
    )
    if not db_record:
        raise HTTPException(status_code=403, detail="Unauthorized")

    db.delete(db_record)
    db.commit()
    return {"status": "deleted"}


@router.get("/origins", response_model=List[HostingOriginSchema])
async def list_hosting_origins(
    user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    """List all hosting origins for the user"""
    origins = db.query(HostingOrigin).filter(HostingOrigin.user_id == user_id).all()
    return origins


@router.post("/origins", response_model=HostingOriginSchema)
async def create_hosting_origin(
    origin: HostingOriginSchema,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new hosting origin"""
    db_origin = HostingOrigin(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=origin.name,
        endpoint=origin.endpoint,
        health_status=origin.health_status,
        region=origin.region,
        role=origin.role,
    )
    db.add(db_origin)
    db.commit()
    db.refresh(db_origin)
    return db_origin


@router.get("/origins/{origin_id}", response_model=HostingOriginSchema)
async def get_hosting_origin(
    origin_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a specific hosting origin"""
    origin = (
        db.query(HostingOrigin)
        .filter(HostingOrigin.id == origin_id, HostingOrigin.user_id == user_id)
        .first()
    )
    if not origin:
        raise HTTPException(status_code=404, detail="Origin not found")
    return origin


@router.delete("/origins/{origin_id}")
async def delete_hosting_origin(
    origin_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete a hosting origin"""
    origin = (
        db.query(HostingOrigin)
        .filter(HostingOrigin.id == origin_id, HostingOrigin.user_id == user_id)
        .first()
    )
    if not origin:
        raise HTTPException(status_code=403, detail="Unauthorized")

    db.delete(origin)
    db.commit()
    return {"status": "deleted"}
