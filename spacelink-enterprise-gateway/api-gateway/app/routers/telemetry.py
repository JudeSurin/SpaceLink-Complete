# api-gateway/app/routers/telemetry.py
"""
SpaceLink Enterprise Gateway - Telemetry API
Endpoints for device telemetry ingestion and querying
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import uuid

from ..database import get_db
from ..models import (
    Telemetry,
    TelemetryCreate,
    TelemetryResponse,
    TelemetryBatch,
    DeviceStatus,
)
from ..auth import (
    get_api_key_data,
    get_current_user_from_token,
    APIKeyData,
    User,
    check_organization_access,
)

router = APIRouter(
    prefix="/v1/telemetry",
    tags=["Telemetry"],
)


# ============================================================================
# Device Endpoints (API Key Authentication)
# ============================================================================

@router.post("/send", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
async def send_telemetry(
    telemetry: TelemetryCreate,
    db: Session = Depends(get_db),
    api_key_data: APIKeyData = Depends(get_api_key_data),
):
    """
    **Device Endpoint**: Submit telemetry data
    
    Requires API key authentication via X-API-Key header.
    Device must match the API key's registered device_id.
    """
    # Verify device_id matches API key
    if telemetry.device_id != api_key_data.device_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Device ID mismatch. API key is for {api_key_data.device_id}",
        )
    
    # Ensure organization matches API key
    telemetry.organization = api_key_data.organization
    
    # Create telemetry record
    db_telemetry = Telemetry(**telemetry.model_dump())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    
    return db_telemetry


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def send_telemetry_batch(
    batch: TelemetryBatch,
    db: Session = Depends(get_db),
    api_key_data: APIKeyData = Depends(get_api_key_data),
):
    """
    **Device Endpoint**: Submit multiple telemetry records in batch
    
    Efficient for devices with intermittent connectivity.
    """
    created_count = 0
    
    for telemetry in batch.telemetry:
        # Verify each device_id matches API key
        if telemetry.device_id != api_key_data.device_id:
            continue  # Skip mismatched records
        
        telemetry.organization = api_key_data.organization
        db_telemetry = Telemetry(**telemetry.model_dump())
        db.add(db_telemetry)
        created_count += 1
    
    db.commit()
    
    return {
        "message": f"Batch processed",
        "records_submitted": len(batch.telemetry),
        "records_created": created_count,
    }


# ============================================================================
# Enterprise Query Endpoints (JWT Authentication)
# ============================================================================

@router.get("/", response_model=List[TelemetryResponse])
async def query_telemetry(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    organization: Optional[str] = Query(None, description="Filter by organization"),
    status: Optional[DeviceStatus] = Query(None, description="Filter by status"),
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """
    **Enterprise Endpoint**: Query telemetry data with filters
    
    Requires JWT authentication. Users can only access data from their organization
    unless they have admin role.
    """
    query = db.query(Telemetry)
    
    # Apply organization filter based on user role
    if user.role != "admin":
        query = query.filter(Telemetry.organization == user.organization)
    elif organization:
        query = query.filter(Telemetry.organization == organization)
    
    # Apply filters
    if device_id:
        query = query.filter(Telemetry.device_id == device_id)
    
    if status:
        query = query.filter(Telemetry.status == status.value)
    
    if start_time:
        query = query.filter(Telemetry.timestamp >= start_time)
    
    if end_time:
        query = query.filter(Telemetry.timestamp <= end_time)
    
    # Execute query with pagination
    telemetry_data = (
        query.order_by(Telemetry.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return telemetry_data


@router.get("/latest", response_model=List[TelemetryResponse])
async def get_latest_telemetry(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """
    **Enterprise Endpoint**: Get latest telemetry for each device
    
    Returns the most recent telemetry reading for each device in the organization.
    """
    # Subquery to get latest timestamp per device
    subquery = (
        db.query(
            Telemetry.device_id,
            func.max(Telemetry.timestamp).label("max_timestamp"),
        )
        .group_by(Telemetry.device_id)
    )
    
    # Filter by organization if not admin
    if user.role != "admin":
        subquery = subquery.filter(Telemetry.organization == user.organization)
    
    subquery = subquery.subquery()
    
    # Join to get full records
    latest_telemetry = (
        db.query(Telemetry)
        .join(
            subquery,
            and_(
                Telemetry.device_id == subquery.c.device_id,
                Telemetry.timestamp == subquery.c.max_timestamp,
            ),
        )
        .all()
    )
    
    return latest_telemetry


@router.get("/devices/{device_id}/latest", response_model=TelemetryResponse)
async def get_device_latest(
    device_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """
    **Enterprise Endpoint**: Get latest telemetry for a specific device
    """
    query = db.query(Telemetry).filter(Telemetry.device_id == device_id)
    
    # Apply organization filter
    if user.role != "admin":
        query = query.filter(Telemetry.organization == user.organization)
    
    telemetry = query.order_by(Telemetry.timestamp.desc()).first()
    
    if not telemetry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry found for device {device_id}",
        )
    
    return telemetry


@router.get("/devices/{device_id}/history", response_model=List[TelemetryResponse])
async def get_device_history(
    device_id: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history (max 7 days)"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """
    **Enterprise Endpoint**: Get telemetry history for a device
    """
    start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    query = (
        db.query(Telemetry)
        .filter(
            Telemetry.device_id == device_id,
            Telemetry.timestamp >= start_time,
        )
    )
    
    # Apply organization filter
    if user.role != "admin":
        query = query.filter(Telemetry.organization == user.organization)
    
    history = query.order_by(Telemetry.timestamp.asc()).all()
    
    return history


@router.get("/stats/summary")
async def get_telemetry_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """
    **Enterprise Endpoint**: Get telemetry statistics summary
    
    Returns aggregated metrics for the organization.
    """
    query = db.query(Telemetry)
    
    # Filter by organization
    if user.role != "admin":
        query = query.filter(Telemetry.organization == user.organization)
    
    # Get counts by status
    total_devices = query.with_entities(
        func.count(func.distinct(Telemetry.device_id))
    ).scalar()
    
    active_devices = query.filter(Telemetry.status == "active").with_entities(
        func.count(func.distinct(Telemetry.device_id))
    ).scalar()
    
    # Get average metrics from last 24 hours
    yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_query = query.filter(Telemetry.timestamp >= yesterday)
    
    avg_metrics = recent_query.with_entities(
        func.avg(Telemetry.latency_ms).label("avg_latency"),
        func.avg(Telemetry.packet_loss_percent).label("avg_packet_loss"),
        func.avg(Telemetry.throughput_mbps).label("avg_throughput"),
        func.avg(Telemetry.signal_strength).label("avg_signal"),
    ).first()
    
    return {
        "organization": user.organization,
        "total_devices": total_devices or 0,
        "active_devices": active_devices or 0,
        "offline_devices": (total_devices or 0) - (active_devices or 0),
        "last_24h_metrics": {
            "avg_latency_ms": round(avg_metrics.avg_latency, 2) if avg_metrics.avg_latency else None,
            "avg_packet_loss_percent": round(avg_metrics.avg_packet_loss, 2) if avg_metrics.avg_packet_loss else None,
            "avg_throughput_mbps": round(avg_metrics.avg_throughput, 2) if avg_metrics.avg_throughput else None,
            "avg_signal_strength": round(avg_metrics.avg_signal, 2) if avg_metrics.avg_signal else None,
        },
    }


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device_telemetry(
    device_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    """
    **Enterprise Endpoint**: Delete all telemetry for a device
    
    Requires admin role.
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete telemetry data",
        )
    
    deleted_count = (
        db.query(Telemetry)
        .filter(Telemetry.device_id == device_id)
        .delete()
    )
    
    db.commit()
    
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry found for device {device_id}",
        )
    
    return None
