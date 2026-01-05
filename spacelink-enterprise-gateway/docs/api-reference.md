# SpaceLink API Reference

## Base URL
```
http://localhost:8000
```

## Authentication

### OAuth2 Token
**Endpoint:** `POST /v1/auth/token`

**Request:**
```
username=enterprise_admin&password=admin123
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Telemetry APIs

### Submit Telemetry
**POST** `/v1/telemetry/send`  
**Auth:** API Key (`X-API-Key` header)

```json
{
  "device_id": "device-001",
  "organization": "ACME Corp",
  "latency_ms": 45.5,
  "packet_loss_percent": 0.2,
  "signal_strength": -68.5,
  "status": "active"
}
```

### Query Telemetry
**GET** `/v1/telemetry/?device_id=xxx&limit=100`  
**Auth:** Bearer token

### Get Latest
**GET** `/v1/telemetry/latest`  
**Auth:** Bearer token

## Network APIs

### Create Network
**POST** `/v1/networks/`  
**Auth:** Bearer token (Partner+)

```json
{
  "name": "Primary WAN",
  "organization": "ACME Corp",
  "network_type": "satellite",
  "sla_uptime_target": 99.9
}
```

### Get Network Health
**GET** `/v1/networks/{id}/health?hours=24`  
**Auth:** Bearer token

## Partner APIs

### Onboard Partner
**POST** `/v1/partners/`  
**Auth:** Bearer token (Admin)

### Generate API Key
**POST** `/v1/partners/{id}/api-keys/generate?device_id=xxx`  
**Auth:** Bearer token (Admin)

**Interactive Docs:** http://localhost:8000/docs
