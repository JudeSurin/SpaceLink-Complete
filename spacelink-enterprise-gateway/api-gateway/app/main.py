# api-gateway/app/main.py
"""
SpaceLink Enterprise Gateway - Main Application
FastAPI application entry point
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from contextlib import asynccontextmanager

from .database import init_db
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_user_from_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    User,
)
from .routers import telemetry, networks, partners


# ============================================================================
# Application Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    Initialize database on startup
    """
    print("🚀 Initializing SpaceLink Enterprise Gateway...")
    init_db()
    print("✅ Database initialized")
    print("📡 API Gateway ready for enterprise connectivity")
    yield
    print("👋 Shutting down SpaceLink Enterprise Gateway")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="SpaceLink Enterprise Gateway",
    description="""
    **Enterprise Network Telemetry & Integration Platform**
    
    SpaceLink provides secure APIs for satellite network integration,
    real-time telemetry ingestion, and partner onboarding workflows.
    
    ## Authentication
    
    - **Device Authentication**: Use `X-API-Key` header for telemetry submission
    - **Enterprise Authentication**: Use OAuth2 Bearer token for query/management APIs
    
    ## Key Features
    
    - 🛰️ Real-time network telemetry collection
    - 📊 Enterprise-grade monitoring and SLA tracking
    - 🤝 Partner onboarding and channel management
    - 🔒 Multi-tenant secure access control
    - 📈 Network health scoring and analytics
    
    ## API Versioning
    
    Current version: **v1**
    All endpoints are prefixed with `/v1/`
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "OAuth2 authentication endpoints for enterprise users and partners",
        },
        {
            "name": "Telemetry",
            "description": "Device telemetry ingestion and query endpoints",
        },
        {
            "name": "Networks",
            "description": "Network configuration and health monitoring",
        },
        {
            "name": "Partners",
            "description": "Partner onboarding and integration management",
        },
        {
            "name": "System",
            "description": "System health and status endpoints",
        },
    ],
)

# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on deployment environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Register Routers
# ============================================================================

app.include_router(telemetry.router)
app.include_router(networks.router)
app.include_router(partners.router)


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/v1/auth/token", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    **OAuth2 Token Endpoint**
    
    Authenticate with username and password to receive a JWT access token.
    
    **Default Test Credentials:**
    - Admin: `enterprise_admin` / `admin123`
    - Partner: `acme_partner` / `partner123`
    - Customer: `customer_user` / `customer123`
    
    Use the access token in the `Authorization: Bearer <token>` header.
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"],
            "organization": user["organization"],
        },
        expires_delta=access_token_expires,
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user["role"],
    )


@app.get("/v1/auth/me", response_model=User, tags=["Authentication"])
async def get_current_user(user: User = Depends(get_current_user_from_token)):
    """
    **Get Current User**
    
    Retrieve information about the authenticated user.
    """
    return user


# ============================================================================
# System Health Endpoints
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """
    **Health Check**
    
    Simple endpoint to verify API is operational.
    """
    return {
        "status": "healthy",
        "service": "SpaceLink Enterprise Gateway",
        "version": "1.0.0",
    }


@app.get("/", tags=["System"])
async def root():
    """
    **API Root**
    
    Welcome endpoint with quick links.
    """
    return {
        "message": "Welcome to SpaceLink Enterprise Gateway",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
        },
        "endpoints": {
            "authentication": "/v1/auth/token",
            "telemetry": "/v1/telemetry",
            "networks": "/v1/networks",
            "partners": "/v1/partners",
        },
        "status": "operational",
    }


@app.get("/v1/status", tags=["System"])
async def api_status():
    """
    **API Status**
    
    Detailed status information about the gateway.
    """
    return {
        "api_version": "v1",
        "service": "SpaceLink Enterprise Gateway",
        "status": "operational",
        "features": {
            "telemetry_ingestion": "enabled",
            "network_monitoring": "enabled",
            "partner_management": "enabled",
            "authentication": "enabled",
        },
        "supported_auth_methods": [
            "API Key (X-API-Key header)",
            "OAuth2 Bearer Token",
        ],
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return {
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "documentation": "/docs",
    }


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
