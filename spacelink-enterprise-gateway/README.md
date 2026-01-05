# SpaceLink Enterprise Gateway

**Enterprise-Grade Network Telemetry & API Integration Platform**

> Inspired by Starlink Enterprise connectivity workflows - A technical sales reference implementation demonstrating how global enterprises integrate satellite networking into existing infrastructure.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)

---

## 🎯 Overview

SpaceLink Enterprise Gateway is a proof-of-concept (POC) enterprise integration platform that simulates the technical architecture required for satellite connectivity deployments at scale. This project demonstrates:

- **Real-time telemetry ingestion** from distributed satellite terminals
- **Enterprise API gateway** with secure authentication and RBAC
- **Partner onboarding workflows** for channel and integration partners
- **SLA monitoring and network health scoring**
- **Multi-tenant secure access** with organization isolation

### Business Context

When enterprises adopt satellite connectivity (like Starlink), they don't simply "plug in" terminals. They require:

✅ **Network Telemetry** - Real-time performance metrics (latency, packet loss, throughput)  
✅ **API Integration** - Programmatic access for automation and monitoring  
✅ **Partner Ecosystem** - Channel partners and system integrators need API access  
✅ **SLA Visibility** - Compliance tracking and alerting  
✅ **Security** - Multi-tenant isolation, RBAC, API key management  

SpaceLink addresses these requirements with a software-defined integration layer.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Enterprise Network                        │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │ Device  │    │ Device  │    │ Device  │
    │  #001   │    │  #002   │    │  #003   │
    └────┬────┘    └────┬────┘    └────┬────┘
         │               │               │
         │    Telemetry Agent (Linux)    │
         │    • Collects network metrics │
         │    • API key authentication   │
         └───────────────┬───────────────┘
                         │
                    ┌────▼────┐
                    │   API   │
                    │ Gateway │◄──── JWT Auth
                    │         │
                    └────┬────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │Telemetry│    │Networks │    │Partners │
    │   API   │    │   API   │    │   API   │
    └─────────┘    └─────────┘    └─────────┘
                         │
                    ┌────▼────┐
                    │Database │
                    │ (SQLite)│
                    └─────────┘
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.12+ or Docker
- 2GB RAM, 1GB disk space

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd spacelink-enterprise-gateway

# Start all services
docker-compose up

# Access API docs
open http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# 1. Setup API Gateway
cd api-gateway
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 2. In a new terminal, start telemetry agent
cd telemetry-agent
pip install requests pyyaml
python agent.py
```

---

## 📚 Key Features

### 1. **Device Telemetry Collection**
- Linux-based telemetry agent
- Metrics: latency, packet loss, signal strength, throughput, jitter
- Configurable collection intervals
- Batch submission support

### 2. **Enterprise API Gateway**
- RESTful APIs (v1)
- OpenAPI/Swagger documentation
- Versioned endpoints for backward compatibility
- CORS support for web applications

### 3. **Dual Authentication**
- **API Keys** - For device telemetry submission (`X-API-Key` header)
- **OAuth2/JWT** - For enterprise users and partners (`Bearer` token)

### 4. **Role-Based Access Control (RBAC)**
- **Admin** - Full access to all resources
- **Partner** - Access to own organization + partner APIs
- **Customer** - Read-only access to own organization
- **Read-Only** - Telemetry query only

### 5. **Network Health Monitoring**
- Real-time health scoring (0-100)
- SLA compliance tracking
- Performance degradation detection
- Historical trend analysis

### 6. **Partner Onboarding**
- Self-service partner registration
- API key generation for devices
- Webhook integration support
- IP whitelisting

---

## 🔐 Authentication

### Get Access Token

```bash
curl -X POST "http://localhost:8000/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=enterprise_admin&password=admin123"
```

**Default Accounts:**
- Admin: `enterprise_admin` / `admin123`
- Partner: `acme_partner` / `partner123`
- Customer: `customer_user` / `customer123`

### Send Telemetry (API Key)

```bash
curl -X POST "http://localhost:8000/v1/telemetry/send" \
  -H "X-API-Key: ok_device_001_abc123xyz" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device-001",
    "organization": "ACME Corporation",
    "timestamp": "2024-01-04T12:00:00Z",
    "latency_ms": 45.5,
    "packet_loss_percent": 0.2,
    "signal_strength": -68.5,
    "status": "active"
  }'
```

---

## 📊 API Endpoints

### Telemetry
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/v1/telemetry/send` | Submit telemetry data | API Key |
| GET | `/v1/telemetry/` | Query telemetry | JWT |
| GET | `/v1/telemetry/latest` | Latest per device | JWT |
| GET | `/v1/telemetry/stats/summary` | Statistics summary | JWT |

### Networks
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/v1/networks/` | Create network | JWT (Partner+) |
| GET | `/v1/networks/` | List networks | JWT |
| GET | `/v1/networks/{id}/health` | Health metrics | JWT |
| GET | `/v1/networks/{id}/sla` | SLA report | JWT |

### Partners
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/v1/partners/` | Onboard partner | JWT (Admin) |
| GET | `/v1/partners/` | List partners | JWT (Partner+) |
| POST | `/v1/partners/{id}/api-keys/generate` | Generate API key | JWT (Admin) |

**Full API Documentation:** http://localhost:8000/docs

---

## 🛠️ Python SDK

```python
from spacelink import SpaceLinkClient

# Initialize client
client = SpaceLinkClient(
    base_url="http://localhost:8000",
    api_key="ok_device_001_abc123xyz"
)

# Send telemetry
client.send_telemetry(
    device_id="device-001",
    organization="ACME Corporation",
    latency_ms=45.5,
    packet_loss_percent=0.2,
    signal_strength=-68.5,
    status="active"
)

# Or authenticate as enterprise user
client.authenticate("enterprise_admin", "admin123")

# Query telemetry
telemetry = client.query_telemetry(device_id="device-001", limit=10)

# Get network health
health = client.get_network_health("net_abc123", hours=24)
```

---

## 📁 Project Structure

```
spacelink-enterprise-gateway/
├── api-gateway/              # FastAPI backend
│   ├── app/
│   │   ├── main.py          # Application entry point
│   │   ├── auth.py          # Authentication & RBAC
│   │   ├── models.py        # SQLAlchemy + Pydantic models
│   │   ├── database.py      # DB configuration
│   │   └── routers/
│   │       ├── telemetry.py # Telemetry endpoints
│   │       ├── networks.py  # Network management
│   │       └── partners.py  # Partner onboarding
│   ├── Dockerfile
│   └── requirements.txt
├── telemetry-agent/          # Device simulator
│   ├── agent.py             # Telemetry collection agent
│   ├── config.yaml          # Configuration
│   └── Dockerfile
├── sdk/python/               # Python client SDK
│   └── spacelink/
│       ├── __init__.py
│       └── client.py
├── docs/                     # Documentation
│   ├── onboarding.md        # Customer onboarding guide
│   ├── api-reference.md     # API documentation
│   ├── partner-integration.md
│   └── sales-demo-script.md
├── postman/                  # API testing
│   └── spacelink.postman_collection.json
├── docker-compose.yml        # Full stack deployment
└── README.md                 # This file
```

---

## 🎯 Use Cases

### Enterprise WAN Failover
Satellite as backup connectivity for mission-critical sites with automatic failover monitoring.

### Remote Site Connectivity
Oil & gas, mining, research stations - locations without terrestrial infrastructure.

### Aviation & Maritime
In-flight and at-sea connectivity with real-time performance monitoring.

### Disaster Recovery
Emergency response teams deploying rapidly with satellite terminals and centralized monitoring.

### Government & Defense
Secure, monitored communications for distributed operations.

---

## 👥 Target Audience

- **Enterprise Network Engineers** - Integrate satellite into existing infrastructure
- **Technical Sales Architects** - Reference implementation for customer POCs
- **Channel Partners** - API-first integration for value-added services
- **DevOps Teams** - Infrastructure-as-code deployment practices

---

## 📖 Documentation

- **[Onboarding Guide](docs/onboarding.md)** - Step-by-step customer onboarding
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Partner Integration](docs/partner-integration.md)** - Partner integration guide
- **[Sales Demo Script](docs/sales-demo-script.md)** - Technical sales walkthrough

---

## 🔒 Security Considerations

- **Production Deployment**:
  - Change default credentials
  - Use environment variables for secrets
  - Enable HTTPS/TLS
  - Implement rate limiting
  - Use PostgreSQL instead of SQLite
  - Enable API key rotation
  - Configure proper CORS origins

---

## 🗺️ Roadmap

- [ ] gRPC telemetry ingestion for high-frequency data
- [ ] Multi-tenant database architecture
- [ ] Advanced alerting and webhooks
- [ ] Partner sandbox environments
- [ ] Grafana dashboards
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline automation

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

---

## ⚠️ Disclaimer

This project is an **independent, educational reference implementation** and is **not affiliated with or endorsed by SpaceX or Starlink**. It serves as a technical demonstration of enterprise satellite connectivity integration patterns.

---

## 🤝 Contributing

This is a portfolio/demonstration project. For questions or suggestions, please open an issue.

---

**Built with:** FastAPI, SQLAlchemy, Pydantic, Docker

**Demonstrates:** Enterprise API design, RBAC, multi-tenant architecture, telemetry systems, DevOps practices
