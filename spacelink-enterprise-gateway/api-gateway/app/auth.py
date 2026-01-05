# api-gateway/app/auth.py
"""
SpaceLink Enterprise Gateway - Authentication & Authorization
Implements API key authentication for devices and OAuth2/JWT for partners
"""

from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import secrets

# Security Configuration
SECRET_KEY = "spacelink-enterprise-secret-key-change-in-production"  # TODO: Move to env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
API_KEY_HEADER = "X-API-Key"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
security_bearer = HTTPBearer()
security_api_key = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


# ============================================================================
# Data Models
# ============================================================================

class User(BaseModel):
    """User/Partner account model"""
    username: str
    email: str
    role: str  # "admin", "partner", "customer", "readonly"
    organization: str
    disabled: bool = False


class TokenData(BaseModel):
    """JWT token payload"""
    username: Optional[str] = None
    role: Optional[str] = None
    organization: Optional[str] = None


class Token(BaseModel):
    """OAuth2 token response"""
    access_token: str
    token_type: str
    expires_in: int
    role: str


class APIKeyData(BaseModel):
    """API Key metadata"""
    key_id: str
    device_id: str
    organization: str
    created_at: datetime
    last_used: Optional[datetime] = None
    active: bool = True


# ============================================================================
# In-Memory Data Stores (Replace with Database in Production)
# ============================================================================

def _init_users_db():
    """Initialize user database with hashed passwords"""
    # Pre-hash passwords to avoid bcrypt bug detection issues
    # Using a try-except to handle bcrypt version compatibility
    try:
        admin_hash = pwd_context.hash("admin123")
        partner_hash = pwd_context.hash("partner123")
        customer_hash = pwd_context.hash("customer123")
    except Exception:
        # Fallback: use plain text for development (NOT FOR PRODUCTION)
        # In production, use environment variables with pre-hashed passwords
        import warnings
        warnings.warn("Using plain text passwords - NOT FOR PRODUCTION")
        admin_hash = "admin123"
        partner_hash = "partner123"
        customer_hash = "customer123"
    
    return {
        "enterprise_admin": {
            "username": "enterprise_admin",
            "email": "admin@enterprise.example.com",
            "hashed_password": admin_hash,
            "role": "admin",
            "organization": "SpaceLink Internal",
            "disabled": False,
        },
        "acme_partner": {
            "username": "acme_partner",
            "email": "tech@acme.example.com",
            "hashed_password": partner_hash,
            "role": "partner",
            "organization": "ACME Corporation",
            "disabled": False,
        },
        "customer_user": {
            "username": "customer_user",
            "email": "ops@customer.example.com",
            "hashed_password": customer_hash,
            "role": "customer",
            "organization": "Customer Inc",
            "disabled": False,
        },
    }

# Simulated user database (lazy initialization)
USERS_DB: Dict[str, Dict] = {}

# Simulated API key database
API_KEYS_DB: Dict[str, APIKeyData] = {
    "ok_device_001_abc123xyz": APIKeyData(
        key_id="ok_device_001_abc123xyz",
        device_id="device-001",  # Used by telemetry agent
        organization="ACME Corporation",
        created_at=datetime.now(timezone.utc),
        active=True,
    ),
    "ok_device_002_def456uvw": APIKeyData(
        key_id="ok_device_002_def456uvw",
        device_id="mobile-001",  # Used by mobile unit
        organization="Customer Inc",
        created_at=datetime.now(timezone.utc),
        active=True,
    ),
    "ok_sat_001_abc123xyz": APIKeyData(
        key_id="ok_sat_001_abc123xyz",
        device_id="sat-001",  # Used by satellite terminal
        organization="ACME Corporation",
        created_at=datetime.now(timezone.utc),
        active=True,
    ),
}


# ============================================================================
# Password & Token Utilities
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback for development (plain text comparison)
        # NOT FOR PRODUCTION
        return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        organization: str = payload.get("organization")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
        return TokenData(username=username, role=role, organization=organization)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


# ============================================================================
# Authentication Functions
# ============================================================================

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user with username and password"""
    # Lazy initialize users database
    if not USERS_DB:
        USERS_DB.update(_init_users_db())
    
    user = USERS_DB.get(username)
    
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    return user


def validate_api_key(api_key: str) -> APIKeyData:
    """Validate device API key"""
    key_data = API_KEYS_DB.get(api_key)
    
    if not key_data or not key_data.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Update last used timestamp
    key_data.last_used = datetime.now(timezone.utc)
    
    return key_data


def generate_api_key(device_id: str, organization: str) -> str:
    """Generate new API key for device"""
    prefix = "ok"  # SpaceLink key prefix
    random_suffix = secrets.token_urlsafe(16)
    api_key = f"{prefix}_{device_id}_{random_suffix}"
    
    # Store in database
    API_KEYS_DB[api_key] = APIKeyData(
        key_id=api_key,
        device_id=device_id,
        organization=organization,
        created_at=datetime.now(timezone.utc),
        active=True,
    )
    
    return api_key


# ============================================================================
# FastAPI Dependencies for Route Protection
# ============================================================================

async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Security(security_bearer)
) -> User:
    """
    Dependency: Extract and validate user from JWT token
    Usage: user = Depends(get_current_user_from_token)
    """
    # Lazy initialize users database
    if not USERS_DB:
        USERS_DB.update(_init_users_db())
    
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    user = USERS_DB.get(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if user.get("disabled"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return User(**user)


async def get_api_key_data(
    api_key: Optional[str] = Security(security_api_key)
) -> APIKeyData:
    """
    Dependency: Validate API key from header
    Usage: key_data = Depends(get_api_key_data)
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"API key required in {API_KEY_HEADER} header",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return validate_api_key(api_key)


# ============================================================================
# Role-Based Access Control (RBAC)
# ============================================================================

class RoleChecker:
    """
    RBAC dependency for protecting routes by role
    Usage: Depends(RoleChecker(["admin", "partner"]))
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_user_from_token)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}",
            )
        return user


# Convenience role checkers
require_admin = RoleChecker(["admin"])
require_partner = RoleChecker(["admin", "partner"])
require_customer = RoleChecker(["admin", "partner", "customer"])


# ============================================================================
# Utility Functions
# ============================================================================

def get_user_permissions(role: str) -> List[str]:
    """Get permissions for a given role"""
    permissions_map = {
        "admin": [
            "telemetry:read",
            "telemetry:write",
            "networks:read",
            "networks:write",
            "partners:read",
            "partners:write",
            "users:manage",
        ],
        "partner": [
            "telemetry:read",
            "telemetry:write",
            "networks:read",
            "partners:read",
        ],
        "customer": [
            "telemetry:read",
            "networks:read",
        ],
        "readonly": [
            "telemetry:read",
        ],
    }
    
    return permissions_map.get(role, [])


def check_organization_access(user: User, resource_organization: str) -> bool:
    """
    Check if user has access to resources from a specific organization
    Admins have global access, others only to their own organization
    """
    if user.role == "admin":
        return True
    
    return user.organization == resource_organization
