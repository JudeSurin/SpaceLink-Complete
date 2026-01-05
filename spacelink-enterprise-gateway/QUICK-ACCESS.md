# SpaceLink Enterprise Gateway - Quick Access Guide

## 🌐 Access URLs

### ✅ CORRECT URLs (Use These):
- **Dashboard**: http://127.0.0.1:8501 or http://localhost:8501
- **API Gateway**: http://127.0.0.1:8000 or http://localhost:8000
- **API Documentation**: http://127.0.0.1:8000/docs

### ❌ INCORRECT URLs (Don't Use):
- ~~http://0.0.0.0:8501~~ - This won't work in browsers!
- ~~http://0.0.0.0:8000~~ - This won't work in browsers!

## Why?

`0.0.0.0` is a special address that means "listen on all network interfaces" when used as a server bind address. However, you **cannot** use it as a URL in your browser. 

When services are configured to listen on `0.0.0.0`, they accept connections from:
- `127.0.0.1` (localhost)
- `localhost`
- Your local IP address (e.g., `192.168.x.x`)

But you must access them using one of these addresses, not `0.0.0.0`.

## Quick Start

### Option 1: Use the Script
```powershell
.\OPEN-DASHBOARD.ps1
```

### Option 2: Manual Access
1. Make sure services are running
2. Open your browser
3. Navigate to: **http://127.0.0.1:8501**

## Troubleshooting

If you see "This site can't be reached":
1. Check if the dashboard is running: `.\check-status.ps1`
2. If not running, start it: `.\START-COMPLETE-SYSTEM.ps1`
3. Wait 5-10 seconds for services to start
4. Try accessing again: http://127.0.0.1:8501

## All Access Points

| Service | URL |
|---------|-----|
| Dashboard | http://127.0.0.1:8501 |
| API Gateway | http://127.0.0.1:8000 |
| API Docs (Swagger) | http://127.0.0.1:8000/docs |
| API Docs (ReDoc) | http://127.0.0.1:8000/redoc |
| Health Check | http://127.0.0.1:8000/health |

