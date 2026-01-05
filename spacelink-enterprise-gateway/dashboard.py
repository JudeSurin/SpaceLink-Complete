# dashboard.py
"""
SpaceLink Enterprise Gateway - Real-Time Telemetry Dashboard
Streamlit-based monitoring interface for network health and device status
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import time

# ============================================================================
# Configuration
# ============================================================================

API_BASE = "http://127.0.0.1:8000"
DEFAULT_USERNAME = "enterprise_admin"
DEFAULT_PASSWORD = "admin123"

# Page configuration
st.set_page_config(
    page_title="SpaceLink Enterprise Gateway",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .status-active {
        color: #28a745;
        font-weight: bold;
    }
    .status-degraded {
        color: #ffc107;
        font-weight: bold;
    }
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    .health-excellent {
        background-color: #d4edda;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .health-good {
        background-color: #d1ecf1;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .health-warning {
        background-color: #fff3cd;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .health-critical {
        background-color: #f8d7da;
        padding: 5px 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# API Client Functions
# ============================================================================

@st.cache_data(ttl=300)
def authenticate() -> Optional[str]:
    """Authenticate and get access token"""
    try:
        response = requests.post(
            f"{API_BASE}/v1/auth/token",
            data={
                "username": DEFAULT_USERNAME,
                "password": DEFAULT_PASSWORD
            },
            timeout=5
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return None


def get_headers(token: str) -> Dict:
    """Get authorization headers"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@st.cache_data(ttl=5)
def fetch_latest_telemetry(token: str) -> List[Dict]:
    """Fetch latest telemetry for all devices"""
    try:
        response = requests.get(
            f"{API_BASE}/v1/telemetry/latest",
            headers=get_headers(token),
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch telemetry: {e}")
        return []


@st.cache_data(ttl=5)
def fetch_telemetry_summary(token: str) -> Dict:
    """Fetch telemetry statistics summary"""
    try:
        response = requests.get(
            f"{API_BASE}/v1/telemetry/stats/summary",
            headers=get_headers(token),
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch summary: {e}")
        return {}


@st.cache_data(ttl=10)
def fetch_device_history(token: str, device_id: str, hours: int = 24) -> List[Dict]:
    """Fetch historical telemetry for a device"""
    try:
        response = requests.get(
            f"{API_BASE}/v1/telemetry/devices/{device_id}/history",
            headers=get_headers(token),
            params={"hours": hours},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch device history: {e}")
        return []


@st.cache_data(ttl=30)
def fetch_networks(token: str) -> List[Dict]:
    """Fetch all networks"""
    try:
        response = requests.get(
            f"{API_BASE}/v1/networks/",
            headers=get_headers(token),
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return []


# ============================================================================
# Helper Functions
# ============================================================================

def get_status_emoji(status: str) -> str:
    """Get emoji for device status"""
    status_map = {
        "active": "✅",
        "degraded": "⚠️",
        "offline": "🔴",
        "maintenance": "🔧"
    }
    return status_map.get(status, "❓")


def get_health_class(health_score: float) -> str:
    """Get CSS class for health score"""
    if health_score >= 90:
        return "health-excellent"
    elif health_score >= 75:
        return "health-good"
    elif health_score >= 50:
        return "health-warning"
    else:
        return "health-critical"


def calculate_health_status(signal: float, latency: float, packet_loss: float) -> str:
    """Calculate overall health status"""
    issues = 0
    
    if signal and signal < -80:
        issues += 1
    if latency and latency > 100:
        issues += 1
    if packet_loss and packet_loss > 1:
        issues += 1
    
    if issues == 0:
        return "Excellent"
    elif issues == 1:
        return "Good"
    elif issues == 2:
        return "Warning"
    else:
        return "Critical"


# ============================================================================
# Main Dashboard
# ============================================================================

def main():
    # Header
    st.markdown("# 🛰️ SpaceLink Enterprise Gateway")
    st.markdown("### Real-Time Network Telemetry & Monitoring Dashboard")
    
    # Authenticate
    token = authenticate()
    if not token:
        st.error("❌ Unable to authenticate. Check API connection.")
        st.stop()
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("## ⚙️ Dashboard Controls")
        
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        refresh_interval = st.slider(
            "Refresh interval (seconds)",
            min_value=5,
            max_value=60,
            value=10,
            step=5
        )
        
        st.markdown("---")
        
        history_hours = st.selectbox(
            "Historical data window",
            options=[1, 6, 12, 24, 48, 168],
            index=3,
            format_func=lambda x: f"{x} hours" if x < 24 else f"{x//24} days"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        # Fetch summary
        summary = fetch_telemetry_summary(token)
        if summary:
            st.metric("Total Devices", summary.get("total_devices", 0))
            st.metric("Active Devices", summary.get("active_devices", 0))
            st.metric("Offline Devices", summary.get("offline_devices", 0))
        
        st.markdown("---")
        st.markdown(f"**Last updated:** {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC")
    
    # Main content
    tabs = st.tabs(["📡 Overview", "📈 Device Details", "🌐 Network Health", "📊 Analytics"])
    
    # ========================================================================
    # Tab 1: Overview
    # ========================================================================
    with tabs[0]:
        st.markdown("## 📡 Fleet Overview")
        
        # Fetch latest telemetry
        telemetry_data = fetch_latest_telemetry(token)
        
        if not telemetry_data:
            st.warning("No telemetry data available. Start the telemetry agent to begin receiving data.")
            st.code("python telemetry-agent/agent.py", language="bash")
            st.stop()
        
        # Summary metrics
        summary = fetch_telemetry_summary(token)
        if summary:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Devices",
                    summary.get("total_devices", 0),
                    delta=None
                )
            
            with col2:
                active = summary.get("active_devices", 0)
                st.metric(
                    "Active Devices",
                    active,
                    delta=f"{active}/{summary.get('total_devices', 0)}"
                )
            
            with col3:
                metrics = summary.get("last_24h_metrics", {})
                avg_latency = metrics.get("avg_latency_ms")
                st.metric(
                    "Avg Latency",
                    f"{avg_latency:.1f} ms" if avg_latency else "N/A",
                    delta=None
                )
            
            with col4:
                avg_throughput = metrics.get("avg_throughput_mbps")
                st.metric(
                    "Avg Throughput",
                    f"{avg_throughput:.1f} Mbps" if avg_throughput else "N/A",
                    delta=None
                )
        
        st.markdown("---")
        
        # Device status table
        st.markdown("### 🖥️ Device Status")
        
        df = pd.DataFrame(telemetry_data)
        
        # Format dataframe
        display_df = df[[
            "device_id", "status", "signal_strength", "latency_ms",
            "packet_loss_percent", "throughput_mbps", "timestamp"
        ]].copy()
        
        display_df["timestamp"] = pd.to_datetime(display_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        display_df = display_df.rename(columns={
            "device_id": "Device ID",
            "status": "Status",
            "signal_strength": "Signal (dBm)",
            "latency_ms": "Latency (ms)",
            "packet_loss_percent": "Packet Loss (%)",
            "throughput_mbps": "Throughput (Mbps)",
            "timestamp": "Last Seen"
        })
        
        # Apply styling
        def highlight_status(row):
            if row["Status"] == "active":
                return ["background-color: #d4edda"] * len(row)
            elif row["Status"] == "degraded":
                return ["background-color: #fff3cd"] * len(row)
            elif row["Status"] == "offline":
                return ["background-color: #f8d7da"] * len(row)
            return [""] * len(row)
        
        st.dataframe(
            display_df.style.apply(highlight_status, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        # Status distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Status Distribution")
            status_counts = df["status"].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                color=status_counts.index,
                color_discrete_map={
                    "active": "#28a745",
                    "degraded": "#ffc107",
                    "offline": "#dc3545",
                    "maintenance": "#6c757d"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📶 Average Signal Strength")
            fig = go.Figure(data=[
                go.Bar(
                    x=df["device_id"],
                    y=df["signal_strength"],
                    marker_color=["#28a745" if s > -70 else "#ffc107" if s > -80 else "#dc3545" 
                                  for s in df["signal_strength"]],
                    text=df["signal_strength"].round(1),
                    textposition="outside"
                )
            ])
            fig.update_layout(
                xaxis_title="Device",
                yaxis_title="Signal Strength (dBm)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # Tab 2: Device Details
    # ========================================================================
    with tabs[1]:
        st.markdown("## 📈 Device Details")
        
        # Device selector
        devices = [d["device_id"] for d in telemetry_data]
        selected_device = st.selectbox("Select Device", devices)
        
        if selected_device:
            # Fetch device history
            history = fetch_device_history(token, selected_device, history_hours)
            
            if history:
                hist_df = pd.DataFrame(history)
                hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])
                hist_df = hist_df.sort_values("timestamp")
                
                # Current status
                current = telemetry_data[[d["device_id"] for d in telemetry_data].index(selected_device)]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    status_emoji = get_status_emoji(current["status"])
                    st.metric("Status", f"{status_emoji} {current['status'].title()}")
                
                with col2:
                    st.metric("Signal Strength", f"{current['signal_strength']:.1f} dBm")
                
                with col3:
                    st.metric("Latency", f"{current['latency_ms']:.1f} ms")
                
                with col4:
                    st.metric("Packet Loss", f"{current['packet_loss_percent']:.2f}%")
                
                st.markdown("---")
                
                # Time series charts
                st.markdown("### 📊 Performance Metrics Over Time")
                
                # Latency chart
                fig1 = px.line(
                    hist_df,
                    x="timestamp",
                    y="latency_ms",
                    title="Latency (ms)",
                    labels={"latency_ms": "Latency (ms)", "timestamp": "Time"}
                )
                fig1.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="SLA Target")
                st.plotly_chart(fig1, use_container_width=True)
                
                # Packet loss chart
                fig2 = px.line(
                    hist_df,
                    x="timestamp",
                    y="packet_loss_percent",
                    title="Packet Loss (%)",
                    labels={"packet_loss_percent": "Packet Loss (%)", "timestamp": "Time"}
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Signal strength chart
                fig3 = px.line(
                    hist_df,
                    x="timestamp",
                    y="signal_strength",
                    title="Signal Strength (dBm)",
                    labels={"signal_strength": "Signal (dBm)", "timestamp": "Time"}
                )
                st.plotly_chart(fig3, use_container_width=True)
                
                # Throughput chart
                fig4 = px.line(
                    hist_df,
                    x="timestamp",
                    y="throughput_mbps",
                    title="Throughput (Mbps)",
                    labels={"throughput_mbps": "Throughput (Mbps)", "timestamp": "Time"}
                )
                st.plotly_chart(fig4, use_container_width=True)
            
            else:
                st.info(f"No historical data available for {selected_device}")
    
    # ========================================================================
    # Tab 3: Network Health
    # ========================================================================
    with tabs[2]:
        st.markdown("## 🌐 Network Health")
        
        networks = fetch_networks(token)
        
        if networks:
            for network in networks:
                with st.expander(f"🌐 {network['name']} ({network['network_id']})", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Type", network["network_type"].upper())
                    
                    with col2:
                        health = network.get("health_score", 0)
                        st.metric("Health Score", f"{health:.1f}/100")
                    
                    with col3:
                        st.metric("Status", network["status"].title())
                    
                    if network.get("description"):
                        st.info(network["description"])
        else:
            st.info("No networks configured. Create networks via the API.")
    
    # ========================================================================
    # Tab 4: Analytics
    # ========================================================================
    with tabs[3]:
        st.markdown("## 📊 Fleet Analytics")
        
        if telemetry_data:
            df = pd.DataFrame(telemetry_data)
            
            # Latency distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Latency Distribution")
                fig = px.histogram(
                    df,
                    x="latency_ms",
                    nbins=20,
                    title="Latency Distribution",
                    labels={"latency_ms": "Latency (ms)"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### Signal Strength Distribution")
                fig = px.histogram(
                    df,
                    x="signal_strength",
                    nbins=20,
                    title="Signal Strength Distribution",
                    labels={"signal_strength": "Signal (dBm)"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Correlation heatmap
            st.markdown("### 📈 Metrics Correlation")
            corr_df = df[["signal_strength", "latency_ms", "packet_loss_percent", "throughput_mbps"]].corr()
            fig = px.imshow(
                corr_df,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    main()
