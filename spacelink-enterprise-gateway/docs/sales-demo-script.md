# SpaceLink - Technical Sales Demo Script

## Demo Overview (30 minutes)

**Audience:** Enterprise network engineers, IT directors, channel partners
**Goal:** Demonstrate enterprise satellite connectivity integration

## Part 1: Business Context (5 min)

"Today I'll show you how SpaceLink solves the satellite connectivity integration challenge..."

**Key Points:**
- Enterprises need programmatic access to satellite telemetry
- Manual monitoring doesn't scale
- Partners need secure API access
- SLA compliance is critical

## Part 2: Live Demo (20 min)

### A. API Gateway Tour
1. Open Swagger UI: `http://localhost:8000/docs`
2. Show authentication flow
3. Demonstrate telemetry ingestion
4. Query network health

### B. Telemetry Collection
1. Start agent: `python agent.py`
2. Show real-time metrics
3. Explain device authentication

### C. Enterprise Features
1. Network health scoring
2. SLA compliance reporting
3. Partner onboarding
4. Multi-tenant isolation

### D. Integration Demo
```python
from spacelink import SpaceLinkClient

client = SpaceLinkClient(api_key="...")
client.send_telemetry(device_id="demo-001", latency_ms=45.5)
```

## Part 3: Q&A (5 min)

**Common Questions:**
- Scale: Handles thousands of devices
- Security: API keys + JWT + RBAC
- Integration: REST API + Python SDK
- Deployment: Docker + Kubernetes ready

## Follow-up Materials

- Technical architecture diagram
- API reference documentation  
- Pricing and licensing (TBD)
- Customer case studies

## Success Metrics

- Demo completion: 100%
- API requests made: >10
- Questions answered
- Next steps scheduled
