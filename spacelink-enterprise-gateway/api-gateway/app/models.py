# api-gateway/app/models.py
"""
SpaceLink Enterprise Gateway - Data Models
SQLAlchemy ORM models and Pydantic schemas
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum

from .database import Base


# ============================================================================
# SQLAlchemy ORM Models (Database Schema)
# ============================================================================

class Telemetry(Base):
    """Network telemetry data from devices"""
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    organization = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    
    # Location data
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Network metrics
    signal_strength = Column(Float)  # dBm or percentage
    latency_ms = Column(Float)  # Round-trip time in milliseconds
    packet_loss_percent = Column(Float)  # Packet loss percentage
    throughput_mbps = Column(Float)  # Throughput in Mbps
    jitter_ms = Column(Float)  # Jitter in milliseconds
    
    # Status
    status = Column(String, default="active")  # active, degraded, offline, maintenance
    
    # Metadata
    firmware_version = Column(String)
    error_message = Column(Text, nullable=True)


class Network(Base):
    """Enterprise network configurations"""
    __tablename__ = "networks"

    id = Column(Integer, primary_key=True, index=True)
    network_id = Column(String, unique=True, index=True, nullable=False)
    organization = Column(String, index=True, nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(Text)
    network_type = Column(String)  # wan, lan, satellite, hybrid
    
    # Configuration
    config = Column(JSON)  # Flexible JSON storage for network config
    
    # Status
    status = Column(String, default="active")
    health_score = Column(Float)  # 0-100 health score
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # SLA tracking
    sla_uptime_target = Column(Float, default=99.9)  # Target uptime percentage
    sla_latency_target = Column(Float, default=100.0)  # Target latency in ms


class Partner(Base):
    """Partner organizations and channel partners"""
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(String, unique=True, index=True, nullable=False)
    
    # Organization info
    organization_name = Column(String, nullable=False)
    partner_type = Column(String)  # channel, integration, reseller, enterprise
    tier = Column(String)  # platinum, gold, silver, bronze
    
    # Contact info
    primary_contact_name = Column(String)
    primary_contact_email = Column(String)
    primary_contact_phone = Column(String)
    
    # Technical details
    api_access_enabled = Column(Boolean, default=True)
    webhook_url = Column(String, nullable=True)
    ip_whitelist = Column(JSON)  # List of allowed IPs
    
    # Status
    status = Column(String, default="active")  # active, suspended, pending
    onboarded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Metadata
    notes = Column(Text)
    tags = Column(JSON)  # Flexible tagging


class Alert(Base):
    """Network alerts and incidents"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True, nullable=False)
    
    device_id = Column(String, index=True)
    network_id = Column(String, index=True)
    organization = Column(String, index=True)
    
    severity = Column(String)  # critical, high, medium, low, info
    alert_type = Column(String)  # latency, packet_loss, outage, degradation
    
    title = Column(String)
    description = Column(Text)
    
    triggered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)
    
    status = Column(String, default="open")  # open, acknowledged, resolved, false_positive
    assigned_to = Column(String, nullable=True)


# ============================================================================
# Pydantic Schemas (API Request/Response Models)
# ============================================================================

# --- Enums ---

class DeviceStatus(str, Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class NetworkType(str, Enum):
    WAN = "wan"
    LAN = "lan"
    SATELLITE = "satellite"
    HYBRID = "hybrid"


class PartnerType(str, Enum):
    CHANNEL = "channel"
    INTEGRATION = "integration"
    RESELLER = "reseller"
    ENTERPRISE = "enterprise"


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


# --- Telemetry Schemas ---

class TelemetryBase(BaseModel):
    device_id: str = Field(..., description="Unique device identifier")
    organization: str = Field(..., description="Organization identifier")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    signal_strength: Optional[float] = Field(None, description="Signal strength")
    latency_ms: Optional[float] = Field(None, ge=0, description="Latency in milliseconds")
    packet_loss_percent: Optional[float] = Field(None, ge=0, le=100)
    throughput_mbps: Optional[float] = Field(None, ge=0)
    jitter_ms: Optional[float] = Field(None, ge=0)
    status: DeviceStatus = Field(default=DeviceStatus.ACTIVE)
    firmware_version: Optional[str] = None
    error_message: Optional[str] = None


class TelemetryCreate(TelemetryBase):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TelemetryResponse(TelemetryBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class TelemetryBatch(BaseModel):
    """Batch telemetry submission"""
    telemetry: List[TelemetryCreate]


# --- Network Schemas ---

class NetworkBase(BaseModel):
    name: str
    description: Optional[str] = None
    network_type: NetworkType
    config: Optional[Dict[str, Any]] = None
    sla_uptime_target: float = Field(default=99.9, ge=0, le=100)
    sla_latency_target: float = Field(default=100.0, ge=0)


class NetworkCreate(NetworkBase):
    organization: str


class NetworkUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    network_type: Optional[NetworkType] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    sla_uptime_target: Optional[float] = None
    sla_latency_target: Optional[float] = None


class NetworkResponse(NetworkBase):
    id: int
    network_id: str
    organization: str
    status: str
    health_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Partner Schemas ---

class PartnerBase(BaseModel):
    organization_name: str
    partner_type: PartnerType
    tier: str = Field(default="bronze", pattern="^(platinum|gold|silver|bronze)$")
    primary_contact_name: str
    primary_contact_email: str
    primary_contact_phone: Optional[str] = None
    webhook_url: Optional[str] = None
    ip_whitelist: Optional[List[str]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class PartnerCreate(PartnerBase):
    pass


class PartnerUpdate(BaseModel):
    organization_name: Optional[str] = None
    partner_type: Optional[PartnerType] = None
    tier: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    webhook_url: Optional[str] = None
    ip_whitelist: Optional[List[str]] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class PartnerResponse(PartnerBase):
    id: int
    partner_id: str
    status: str
    api_access_enabled: bool
    onboarded_at: datetime

    class Config:
        from_attributes = True


# --- Alert Schemas ---

class AlertCreate(BaseModel):
    device_id: Optional[str] = None
    network_id: Optional[str] = None
    organization: str
    severity: AlertSeverity
    alert_type: str
    title: str
    description: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    alert_id: str
    device_id: Optional[str]
    network_id: Optional[str]
    organization: str
    severity: str
    alert_type: str
    title: str
    description: Optional[str]
    triggered_at: datetime
    resolved_at: Optional[datetime]
    status: str
    assigned_to: Optional[str]

    class Config:
        from_attributes = True


# --- Health & Metrics Schemas ---

class NetworkHealth(BaseModel):
    """Network health summary"""
    network_id: str
    organization: str
    health_score: float = Field(ge=0, le=100)
    status: str
    avg_latency_ms: Optional[float]
    avg_packet_loss_percent: Optional[float]
    uptime_percent: Optional[float]
    last_updated: datetime


class OrganizationMetrics(BaseModel):
    """Organization-wide metrics"""
    organization: str
    total_devices: int
    active_devices: int
    total_networks: int
    healthy_networks: int
    open_alerts: int
    avg_latency_ms: Optional[float]
    avg_throughput_mbps: Optional[float]
