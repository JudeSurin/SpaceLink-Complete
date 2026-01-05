# Partner Integration Guide

## Overview

This guide helps channel partners and system integrators integrate with SpaceLink Enterprise Gateway.

## Partner Types

- **Channel Partner** - Resell SpaceLink to customers
- **Integration Partner** - Build value-added services
- **Reseller** - White-label solutions
- **Enterprise** - Direct enterprise customers

## Integration Steps

### 1. Partner Onboarding

Contact SpaceLink admin team for partner account creation.

### 2. Authentication

```python
from spacelink import SpaceLinkClient

client = SpaceLinkClient(base_url="https://api.spacelink.com")
client.authenticate("partner_username", "partner_password")
```

### 3. API Key Management

Generate API keys for customer devices:

```bash
curl -X POST "/v1/partners/{partner_id}/api-keys/generate?device_id=xxx" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Telemetry Integration

Deploy agents to customer devices or integrate SDK:

```python
client.send_telemetry(
    device_id="customer-device-001",
    organization="Customer Corp",
    latency_ms=45.5
)
```

### 5. Webhook Configuration

Configure webhooks for real-time alerts:

```json
{
  "webhook_url": "https://partner.com/webhooks/spacelink",
  "events": ["telemetry.degraded", "telemetry.offline"]
}
```

## SDK Examples

### Python
```python
from spacelink import SpaceLinkClient

client = SpaceLinkClient(api_key="partner_key")
networks = client.list_networks(organization="Customer Corp")
```

### REST API
```bash
curl "http://api.spacelink.com/v1/telemetry/latest" \
  -H "Authorization: Bearer $TOKEN"
```

## Support

- Technical documentation: `/docs`
- API reference: `docs/api-reference.md`
- Partner portal: (Contact sales)

## Best Practices

1. Secure API key storage (environment variables)
2. Implement retry logic for API calls
3. Monitor webhook delivery status
4. Use batch telemetry submission for efficiency
5. Implement proper error handling
