# SpaceLink Enterprise Gateway - Customer Onboarding Guide

## Welcome to SpaceLink

This guide walks you through setting up and integrating SpaceLink Enterprise Gateway into your network infrastructure.

## Prerequisites

- Python 3.12+ or Docker
- Network administrator access
- Basic understanding of REST APIs

## Quick Start (5 Minutes)

### 1. Installation

**Docker (Recommended):**
```bash
docker-compose up -d
```

**Local:**
```bash
cd api-gateway
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Get Access Token

```bash
curl -X POST "http://localhost:8000/v1/auth/token" \
  -d "username=enterprise_admin&password=admin123"
```

### 3. Deploy Telemetry Agent

Configure `telemetry-agent/config.yaml` then run:
```bash
python agent.py
```

### 4. Verify Data Flow

```bash
curl "http://localhost:8000/v1/telemetry/latest" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Full Configuration Guide

See sections on network creation, API key management, and monitoring in the complete docs.

**Next:** Explore `/docs` for interactive API documentation
