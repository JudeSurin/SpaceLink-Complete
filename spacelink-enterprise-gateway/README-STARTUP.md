# SpaceLink Enterprise Gateway - Startup Guide

## Fixed Issues

1. **Password Hashing Error**: Fixed bcrypt compatibility issue by implementing lazy password hashing
2. **Command Not Found**: Fixed `uvicorn` and `streamlit` commands by using `python -m` syntax
3. **Config Path Issue**: Fixed telemetry agent config file path resolution

## Quick Start

### Option 1: Start All Services (Recommended)
```powershell
.\start-all.ps1
```

### Option 2: Start Services Individually

**Start API Gateway:**
```powershell
.\start-api.ps1
```

**Start Dashboard:**
```powershell
.\start-dashboard.ps1
```

### Option 3: Manual Start

**API Gateway:**
```powershell
cd api-gateway
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Dashboard:**
```powershell
python -m streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

## Test Services

Run the test script to verify services are running:
```powershell
.\TEST-SERVICES.ps1
```

## Access Points

- **API Gateway**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Dashboard**: http://127.0.0.1:8501

## Test Credentials

- **Admin**: `enterprise_admin` / `admin123`
- **Partner**: `acme_partner` / `partner123`
- **Customer**: `customer_user` / `customer123`

## Run Telemetry Agent

To generate test data:
```powershell
cd telemetry-agent
python agent.py
```

Or use device simulators:
```powershell
# Satellite Terminal
python devices\satellite_terminal.py

# Mobile Unit
python devices\mobile_unit.py

# IoT Gateway
python devices\iot_gateway.py
```

## Troubleshooting

If services don't start:
1. Check if ports 8000 and 8501 are already in use
2. Verify Python dependencies are installed: `pip install -r api-gateway/requirements.txt`
3. Check for error messages in the console windows

