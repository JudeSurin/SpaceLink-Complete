# api-gateway/app/routers/networks.py
"""
SpaceLink Enterprise Gateway - Networks API
Endpoints for network configuration and health monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import uuid

from ..database import get_db
from ..models import (
    Network,
    Telemetry,
    NetworkCreate,
    NetworkUpdate,
    NetworkResponse,
    NetworkHealth,
    NetworkType,
)
from ..auth import (
    get_current_user_from_token,
    User,
    require_admin,
    require_partner,
)

router = APIRouter(
    prefix="/v1/networks",
    tags=["Networks"],
)


# ============================================================================
# Network CRUD Operations
# ============================================================================

@router.post("/", response_model=NetworkResponse, status_code=status.HTTP_201_CREATED)
async def create_network(
    network: NetworkCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_partner),
):
    """
    **Create Network Configuration**
    
    Define a new network for monitoring and management.
    Requires partner or admin role.
    """
    # Ensure non-admins can only create networks for their organization
    if user.role != "admin" and network.organization != user.organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create network for different organization",
        )
    
    # Generate unique network ID
    network_id = f"net_{uuid.uuid4().hex[:12]}"
    
    # Create network record
    db_network = Network(
        network_id=network_id,
        **network.model_dump(),
        status="active",
        health_score=100.0,
    )
    
    db.add(db_network)
    db.commit()
    db.refresh(db_network)
    
    return db_network


@router.get("/", response_model=List[NetworkResponse])
async def list_networks(
    organization: Optional[str] = Query(None, description="Filter by organization"),
    network_type: Optional[NetworkType] = Query(None, description="Filter by network type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """
    **List Networks**
    
    Query all networks with optional filters.
    """
    query = db.query(Network)
    
    # Apply organization filter based on role
    if user.role != "admin":
        query = query.filter(Network.organization == user.organization)
    elif organization:
        query = query.filter(Network.organization == organization)
    
    if network_type:
        query = query.filter(Network.network_type == network_type.value)
    
    if status:
        query = query.filter(Network.status == status)
    
    networks = query.order_by(Network.created_at.desc()).all()
    return networks


@router.get("/{network_id}", response_model=NetworkResponse)
async def get_network(
    network_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """
    **Get Network Details**
    
    Retrieve detailed information about a specific network.
    """
    network = db.query(Network).filter(Network.network_id == network_id).first()
    
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network {network_id} not found",
        )
    
    # Check organization access
    if user.role != "admin" and network.organization != user.organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this network",
        )
    
    return network


@router.patch("/{network_id}", response_model=NetworkResponse)
async def update_network(
    network_id: str,
    network_update: NetworkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_partner),
):
    """
    **Update Network Configuration**
    
    Modify network settings and configuration.
    """
    network = db.query(Network).filter(Network.network_id == network_id).first()
    
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network {network_id} not found",
        )
    
    # Check organization access
    if user.role != "admin" and network.organization != user.organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify network from different organization",
        )
    
    # Apply updates
    update_data = network_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(network, field, value)
    
    network.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(network)
    
    return network


@router.delete("/{network_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_network(
    network_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    **Delete Network**
    
    Remove a network configuration. Admin only.
    """
    network = db.query(Network).filter(Network.network_id == network_id).first()
    
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network {network_id} not found",
        )
    
    db.delete(network)
    db.commit()
    
    return None


# ============================================================================
# Network Health & Monitoring
# ============================================================================

@router.get("/{network_id}/health", response_model=NetworkHealth)
async def get_network_health(
    network_id: str,
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """
    **Get Network Health Metrics**
    
    Calculate health score and performance metrics for a network.
    """
    network = db.query(Network).filter(Network.network_id == network_id).first()
    
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network {network_id} not found",
        )
    
    # Check organization access
    if user.role != "admin" and network.organization != user.organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this network",
        )
    
    # Calculate metrics from telemetry data
    start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    telemetry_stats = (
        db.query(
            func.avg(Telemetry.latency_ms).label("avg_latency"),
            func.avg(Telemetry.packet_loss_percent).label("avg_packet_loss"),
            func.count(Telemetry.id).label("total_readings"),
        )
        .filter(
            Telemetry.organization == network.organization,
            Telemetry.timestamp >= start_time,
        )
        .first()
    )
    
    # Calculate uptime percentage
    total_readings = telemetry_stats.total_readings or 0
    active_readings = (
        db.query(func.count(Telemetry.id))
        .filter(
            Telemetry.organization == network.organization,
            Telemetry.timestamp >= start_time,
            Telemetry.status == "active",
        )
        .scalar() or 0
    )
    
    uptime_percent = (active_readings / total_readings * 100) if total_readings > 0 else 0
    
    # Calculate health score (simplified algorithm)
    health_score = 100.0
    
    if telemetry_stats.avg_latency:
        # Deduct points for high latency
        if telemetry_stats.avg_latency > network.sla_latency_target:
            health_score -= min(30, (telemetry_stats.avg_latency - network.sla_latency_target) / 10)
    
    if telemetry_stats.avg_packet_loss:
        # Deduct points for packet loss
        health_score -= min(30, telemetry_stats.avg_packet_loss * 3)
    
    # Deduct for low uptime
    if uptime_percent < network.sla_uptime_target:
        health_score -= min(40, (network.sla_uptime_target - uptime_percent) * 2)
    
    health_score = max(0, health_score)
    
    # Update network health score
    network.health_score = round(health_score, 2)
    db.commit()
    
    return NetworkHealth(
        network_id=network.network_id,
        organization=network.organization,
        health_score=round(health_score, 2),
        status=network.status,
        avg_latency_ms=round(telemetry_stats.avg_latency, 2) if telemetry_stats.avg_latency else None,
        avg_packet_loss_percent=round(telemetry_stats.avg_packet_loss, 2) if telemetry_stats.avg_packet_loss else None,
        uptime_percent=round(uptime_percent, 2),
        last_updated=datetime.now(timezone.utc),
    )


@router.get("/{network_id}/sla", )
async def get_network_sla_report(
    network_id: str,
    start_date: Optional[datetime] = Query(None, description="Report start date"),
    end_date: Optional[datetime] = Query(None, description="Report end date"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """
    **Get SLA Compliance Report**
    
    Generate SLA compliance metrics for a network over a time period.
    """
    network = db.query(Network).filter(Network.network_id == network_id).first()
    
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network {network_id} not found",
        )
    
    # Check organization access
    if user.role != "admin" and network.organization != user.organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this network",
        )
    
    # Default to last 30 days if not specified
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Query telemetry for period
    telemetry_data = (
        db.query(Telemetry)
        .filter(
            Telemetry.organization == network.organization,
            Telemetry.timestamp >= start_date,
            Telemetry.timestamp <= end_date,
        )
        .all()
    )
    
    total_readings = len(telemetry_data)
    if total_readings == 0:
        return {
            "network_id": network_id,
            "period_start": start_date,
            "period_end": end_date,
            "message": "No telemetry data available for this period",
        }
    
    # Calculate SLA metrics
    active_readings = sum(1 for t in telemetry_data if t.status == "active")
    uptime_percent = (active_readings / total_readings) * 100
    
    latencies = [t.latency_ms for t in telemetry_data if t.latency_ms is not None]
    avg_latency = sum(latencies) / len(latencies) if latencies else None
    
    sla_compliance = {
        "uptime_compliance": uptime_percent >= network.sla_uptime_target,
        "latency_compliance": avg_latency <= network.sla_latency_target if avg_latency else None,
    }
    
    return {
        "network_id": network_id,
        "organization": network.organization,
        "period_start": start_date,
        "period_end": end_date,
        "total_readings": total_readings,
        "sla_targets": {
            "uptime_target": network.sla_uptime_target,
            "latency_target_ms": network.sla_latency_target,
        },
        "actual_performance": {
            "uptime_percent": round(uptime_percent, 2),
            "avg_latency_ms": round(avg_latency, 2) if avg_latency else None,
        },
        "compliance": sla_compliance,
        "status": "COMPLIANT" if all(sla_compliance.values()) else "NON_COMPLIANT",
    }
