# SpaceLink Devices

**REAL Device Implementations with Actual Network Measurements**

## 📡 Available Devices

### 1. Satellite Terminal (`satellite_terminal.py`)
Fixed-location satellite dish (like Starlink)
- ✅ REAL ping tests
- ✅ Fixed GPS location
- ✅ Typical use: Office, remote site

**Run:**
```bash
python satellite_terminal.py
```

### 2. Mobile Unit (`mobile_unit.py`)
Vehicle/Ship/Aircraft device
- ✅ REAL ping tests
- ✅ GPS movement simulation
- ✅ Typical use: Fleet tracking

**Run:**
```bash
python mobile_unit.py
```

### 3. IoT Gateway (`iot_gateway.py`)
Industrial site gateway
- ✅ REAL ping tests
- ✅ Fixed location
- ✅ Typical use: Oil rigs, mines, factories

**Run:**
```bash
python iot_gateway.py
```

## ✨ Key Features

All devices use **REAL network measurements**:
- Actual `ping` command execution
- Real latency measurement  
- Real packet loss detection
- Status based on actual performance

**NOT simulated!** These collect real metrics from your network.

## 🚀 Quick Start

```bash
# Run a device
cd devices
python satellite_terminal.py

# Run multiple devices (different terminals)
python satellite_terminal.py   # Terminal 1
python mobile_unit.py          # Terminal 2
python iot_gateway.py          # Terminal 3
```

Dashboard will show all devices with real metrics!
