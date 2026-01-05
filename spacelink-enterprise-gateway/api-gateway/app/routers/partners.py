# api-gateway/app/routers/partners.py
"""
SpaceLink Enterprise Gateway - Partners API
Endpoints for partner onboarding, management, and integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from ..database import get_db
from ..models import (
    Partner,
    PartnerCreate,
    PartnerUpdate,
    PartnerResponse,
    PartnerType,
)
from ..auth import (
    get_current_user_from_token,
    generate_api_key,
    User,
    require_admin,
    require_partner,
)

router = APIRouter(
    prefix="/v1/partners",
    tags=["Partners"],
)


# ============================================================================
# Partner Management
# ============================================================================

@router.post("/", response_model=PartnerResponse, status_code=status.HTTP_201_CREATED)
async def onboard_partner(
    partner: PartnerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    **Onboard New Partner**
    
    Create a new partner organization in the system.
    Admin only - used for channel partner onboarding.
    """
    # Generate unique partner ID
    partner_id = f"partner_{uuid.uuid4().hex[:12]}"
    
    # Create partner record
    db_partner = Partner(
        partner_id=partner_id,
        **partner.model_dump(),
        status="active",
        api_access_enabled=True,
        onboarded_at=datetime.now(timezone.utc),
    )
    
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    
    return db_partner


@router.get("/", response_model=List[PartnerResponse])
async def list_partners(
    partner_type: Optional[PartnerType] = Query(None, description="Filter by partner type"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    user: User = Depends(require_partner),
):
    """
    **List Partners**
    
    Query all partner organizations.
    Partners can only see their own record, admins see all.
    """
    query = db.query(Partner)
    
    # Non-admins can only see their own partner record
    if user.role != "admin":
        query = query.filter(Partner.organization_name == user.organization)
    
    if partner_type:
        query = query.filter(Partner.partner_type == partner_type.value)
    
    if tier:
        query = query.filter(Partner.tier == tier)
    
    if status:
        query = query.filter(Partner.status == status)
    
    partners = query.order_by(Partner.onboarded_at.desc()).all()
    return partners


@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(
    partner_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_partner),
):
    """
    **Get Partner Details**
    
    Retrieve detailed information about a partner.
    """
    partner = db.query(Partner).filter(Partner.partner_id == partner_id).first()
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )
    
    # Non-admins can only view their own partner record
    if user.role != "admin" and partner.organization_name != user.organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this partner record",
        )
    
    return partner


@router.patch("/{partner_id}", response_model=PartnerResponse)
async def update_partner(
    partner_id: str,
    partner_update: PartnerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    **Update Partner Information**
    
    Modify partner settings and configuration. Admin only.
    """
    partner = db.query(Partner).filter(Partner.partner_id == partner_id).first()
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )
    
    # Apply updates
    update_data = partner_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(partner, field, value)
    
    db.commit()
    db.refresh(partner)
    
    return partner


@router.post("/{partner_id}/suspend", response_model=PartnerResponse)
async def suspend_partner(
    partner_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    **Suspend Partner Access**
    
    Temporarily disable a partner's API access. Admin only.
    """
    partner = db.query(Partner).filter(Partner.partner_id == partner_id).first()
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )
    
    partner.status = "suspended"
    partner.api_access_enabled = False
    
    db.commit()
    db.refresh(partner)
    
    return partner


@router.post("/{partner_id}/activate", response_model=PartnerResponse)
async def activate_partner(
    partner_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    **Activate Partner Access**
    
    Re-enable a suspended partner. Admin only.
    """
    partner = db.query(Partner).filter(Partner.partner_id == partner_id).first()
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )
    
    partner.status = "active"
    partner.api_access_enabled = True
    
    db.commit()
    db.refresh(partner)
    
    return partner


# ============================================================================
# Partner Integration Support
# ============================================================================

@router.post("/{partner_id}/api-keys/generate")
async def generate_partner_api_key(
    partner_id: str,
    device_id: str = Query(..., description="Device ID for the API key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    **Generate API Key for Partner Device**
    
    Create a new API key for a partner's device to send telemetry.
    Admin only.
    """
    partner = db.query(Partner).filter(Partner.partner_id == partner_id).first()
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )
    
    if not partner.api_access_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Partner API access is disabled",
        )
    
    # Generate API key
    api_key = generate_api_key(device_id, partner.organization_name)
    
    return {
        "partner_id": partner_id,
        "device_id": device_id,
        "api_key": api_key,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "usage": f"Include in X-API-Key header when sending telemetry",
    }


@router.get("/{partner_id}/integration-status")
async def get_partner_integration_status(
    partner_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_partner),
):
    """
    **Get Partner Integration Status**
    
    Check integration health and recent activity for a partner.
    """
    partner = db.query(Partner).filter(Partner.partner_id == partner_id).first()
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )
    
    # Non-admins can only view their own status
    if user.role != "admin" and partner.organization_name != user.organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Get recent telemetry count
    from ..models import Telemetry
    from datetime import timedelta
    
    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_telemetry_count = (
        db.query(Telemetry)
        .filter(
            Telemetry.organization == partner.organization_name,
            Telemetry.timestamp >= last_24h,
        )
        .count()
    )
    
    return {
        "partner_id": partner_id,
        "organization": partner.organization_name,
        "status": partner.status,
        "api_access_enabled": partner.api_access_enabled,
        "integration_active": recent_telemetry_count > 0,
        "last_24h_telemetry_count": recent_telemetry_count,
        "webhook_configured": partner.webhook_url is not None,
        "ip_whitelist_configured": partner.ip_whitelist is not None,
    }


@router.delete("/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_partner(
    partner_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """
    **Delete Partner**
    
    Permanently remove a partner from the system. Admin only.
    Use with caution - this cannot be undone.
    """
    partner = db.query(Partner).filter(Partner.partner_id == partner_id).first()
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )
    
    db.delete(partner)
    db.commit()
    
    return None
