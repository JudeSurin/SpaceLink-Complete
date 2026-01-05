# SpaceLink Enterprise Gateway - Quick Start Guide

## 🚀 Complete System Startup

This guide shows you how to run the **entire SpaceLink system** with API, agents, and dashboard.

---

## Prerequisites

- Python 3.12+
- pip
- 3 terminal windows

---

## Option 1: Quick Start (Recommended - 5 Minutes)

### Step 1: Install All Dependencies

```bash
# Navigate to project
cd spacelink-enterprise-gateway

# Install API dependencies
cd api-gateway
pip install -r requirements.txt
cd ..

# Install dashboard dependencies
pip install -r dashboard-requirements.txt

# Install agent dependencies
cd telemetry-agent
pip install requests pyyaml
cd ..
```

### Step 2: Start All Services

**Terminal 1 - API Gateway:**
```bash
cd spacelink-enterprise-gateway/api-gateway
uvicorn app.main:app --reload
```

✅ **Verify:** http://127.0.0.1:8000/health should return `{"status": "healthy"}`

**Terminal 2 - Telemetry Agent:**
```bash
cd spacelink-enterprise-gateway/telemetry-agent
python agent.py
```

✅ **Verify:** You should see telemetry being sent every 5 seconds

**Terminal 3 - Dashboard:**
```bash
cd spacelink-enterprise-gateway
streamlit run dashboard.py
```

✅ **Verify:** Dashboard opens at http://localhost:8501

---

## Option 2: Docker (Production - 1 Command)

```bash
cd spacelink-enterprise-gateway
docker-compose up
```

**Note:** Dashboard needs to be run separately if using Docker.

---

## 🎯 What You'll See

### API Gateway (Terminal 1)
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Telemetry Agent (Terminal 2)
```
🛰️  Initialized telemetry agent for device: device-001
📡 Target gateway: http://127.0.0.1:8000/v1/telemetry/send
⏱️  Collection interval: 5s

✅ [device-001] Latency: 45.1ms | Loss: 0.2% | Signal: -68.5dBm | Status: active
✅ [device-001] Latency: 52.3ms | Loss: 0.1% | Signal: -67.2dBm | Status: active
```

### Dashboard (Terminal 3)
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.x:8501
```

---

## 📊 Dashboard Features

Once running, the dashboard shows:

### Overview Tab
- ✅ Fleet summary (total devices, active devices)
- ✅ Real-time metrics (avg latency, throughput)
- ✅ Device status table with color coding
- ✅ Status distribution pie chart
- ✅ Signal strength bar chart

### Device Details Tab
- ✅ Individual device selection
- ✅ Current status metrics
- ✅ Historical performance charts:
  - Latency over time
  - Packet loss trends
  - Signal strength variations
  - Throughput history

### Network Health Tab
- ✅ Network configurations
- ✅ Health scores (0-100)
- ✅ SLA compliance status

### Analytics Tab
- ✅ Latency distribution histogram
- ✅ Signal strength distribution
- ✅ Metrics correlation heatmap

---

## 🔧 Configuration

### Change API URL
Edit `dashboard.py`:
```python
API_BASE = "http://127.0.0.1:8000"  # Change to your API URL
```

### Change Refresh Rate
In the dashboard sidebar:
- Enable/disable auto-refresh
- Adjust interval (5-60 seconds)

### Change Telemetry Frequency
Edit `telemetry-agent/config.yaml`:
```yaml
collection:
  interval_seconds: 5  # Change to desired interval
```

---

## 🎨 Dashboard Controls

### Sidebar
- **Auto-refresh:** Toggle automatic data refresh
- **Refresh interval:** Set update frequency (5-60 seconds)
- **Historical window:** Choose time range (1 hour - 7 days)
- **Quick stats:** See device counts at a glance

### Main Tabs
1. **Overview** - Fleet-wide status and health
2. **Device Details** - Deep dive into individual devices
3. **Network Health** - Network-level monitoring
4. **Analytics** - Statistical analysis and trends

---

## 🧪 Testing the System

### 1. Verify API is Running
```bash
curl http://127.0.0.1:8000/health
# Expected: {"status":"healthy"}
```

### 2. Check Telemetry Flow
```bash
curl http://127.0.0.1:8000/v1/telemetry/latest \
  -H "Authorization: Bearer $(curl -X POST http://127.0.0.1:8000/v1/auth/token \
  -d 'username=enterprise_admin&password=admin123' | jq -r .access_token)"
```

### 3. View API Documentation
Open: http://127.0.0.1:8000/docs

---

## 🎯 Simulating Different Scenarios

### Multiple Devices
Edit `telemetry-agent/config.yaml` and run multiple agents:

**Terminal 2a - Device 1:**
```bash
python agent.py
```

**Terminal 2b - Device 2:**
```bash
# Edit config.yaml to change device_id to "device-002"
python agent.py
```

The dashboard will show both devices!

### Network Issues
The agent automatically simulates:
- ✅ Random latency spikes (5% chance)
- ✅ Packet loss events (3% chance)
- ✅ Signal strength variations
- ✅ Occasional offline status (1% chance)

---

## 📈 Production Deployment

### Environment Variables
Create `.env` file:
```env
DATABASE_URL=postgresql://user:pass@localhost/spacelink
API_SECRET_KEY=your-secret-key-change-in-production
DASHBOARD_API_URL=https://api.spacelink.com
```

### HTTPS Configuration
Update dashboard API URL for production:
```python
API_BASE = "https://api.spacelink.com"
```

---

## 🛑 Stopping the System

Press `Ctrl+C` in each terminal:
1. Stop Dashboard (Terminal 3)
2. Stop Agent (Terminal 2)
3. Stop API (Terminal 1)

Or if using Docker:
```bash
docker-compose down
```

---

## ❓ Troubleshooting

### Dashboard Shows "No telemetry data"
**Solution:** Make sure API and agent are running first
```bash
# Check API
curl http://127.0.0.1:8000/health

# Check telemetry
curl http://127.0.0.1:8000/v1/telemetry/latest \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### "Connection refused" in dashboard
**Solution:** Update API_BASE in dashboard.py to match your API URL

### Agent shows "Connection error"
**Solution:** 
1. Verify API is running: `curl http://127.0.0.1:8000/health`
2. Check API URL in `config.yaml`
3. Verify API key is correct

### Dashboard authentication failed
**Solution:** Check default credentials in dashboard.py:
- Username: `enterprise_admin`
- Password: `admin123`

---

## 📊 What This Demonstrates

This complete system showcases:

✅ **Full-Stack Architecture**
- Backend API (FastAPI)
- Data agents (Python)
- Frontend dashboard (Streamlit)

✅ **Real-Time Data Flow**
- Devices → API → Database → Dashboard
- Live metrics updates
- Auto-refresh capabilities

✅ **Production Patterns**
- Authentication & authorization
- Multi-device monitoring
- Health scoring algorithms
- SLA tracking
- Data visualization

✅ **Enterprise Features**
- Multi-tenant architecture
- Role-based access control
- Comprehensive analytics
- Historical trending

---

## 🎓 Interview Talking Points

*"I built a complete satellite connectivity monitoring platform with three components: a FastAPI backend for telemetry ingestion, Python agents simulating network devices, and a Streamlit dashboard for real-time visualization. The system handles authentication, stores time-series data, and provides interactive analytics with auto-refresh capabilities. It demonstrates full-stack development, real-time data pipelines, and production-ready monitoring patterns."*

**Tech Stack:**
- Backend: FastAPI, SQLAlchemy, OAuth2/JWT
- Frontend: Streamlit, Plotly, Pandas
- Data Flow: REST APIs, real-time polling
- Deployment: Docker, multi-process orchestration

---

## 🌟 Next Steps

1. ✅ Add more devices (modify config.yaml)
2. ✅ Create custom networks via API
3. ✅ Set up alerts and webhooks
4. ✅ Deploy to cloud (AWS, Azure, GCP)
5. ✅ Add Grafana for advanced dashboards
6. ✅ Implement WebSocket for real-time updates

---

**You now have a production-grade observability platform! 🚀**
