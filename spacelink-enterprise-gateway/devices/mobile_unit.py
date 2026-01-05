#!/usr/bin/env python3
"""SpaceLink Mobile Unit - Vehicle/Maritime/Aircraft"""

import requests
import subprocess
import platform
import re
import time
import random
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MobileUnit:
    """Mobile device with GPS simulation + REAL ping"""
    
    def __init__(self, device_id, api_key, api_url, start_location=(47.6, -122.3)):
        self.device_id = device_id
        self.api_key = api_key
        self.api_url = api_url
        self.organization = "Mobile Fleet Corp"
        self.lat, self.lon = start_location
        self.system = platform.system()
        
        logger.info(f"🚗 Mobile Unit {device_id} initialized")
    
    def update_gps(self):
        """Simulate movement"""
        self.lat += random.uniform(-0.001, 0.001)
        self.lon += random.uniform(-0.001, 0.001)
    
    def ping_test(self):
        """REAL ping test"""
        try:
            cmd = ['ping', '-n' if self.system == 'Windows' else '-c', '3', '8.8.8.8']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            
            if self.system == 'Windows':
                lat = re.search(r'Average = (\d+)ms', result.stdout)
                loss = re.search(r'\((\d+)% loss\)', result.stdout)
            else:
                lat = re.search(r'avg.*= [\d.]+/([\d.]+)/', result.stdout)
                loss = re.search(r'(\d+)% packet loss', result.stdout)
            
            return (float(lat.group(1)) if lat else None,
                   float(loss.group(1)) if loss else 0)
        except:
            return None, 100.0
    
    def collect_telemetry(self):
        """Collect with GPS"""
        self.update_gps()
        latency, packet_loss = self.ping_test()
        
        status = "active" if packet_loss < 5 and latency and latency < 100 else "degraded"
        
        return {
            "device_id": self.device_id,
            "organization": self.organization,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": round(self.lat, 6),
            "longitude": round(self.lon, 6),
            "signal_strength": -70,
            "latency_ms": latency,
            "packet_loss_percent": packet_loss,
            "throughput_mbps": 80,
            "jitter_ms": 3.2,
            "status": status,
            "firmware_version": "v1.5-mobile"
        }
    
    def send(self, data):
        """Send telemetry"""
        try:
            headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
            r = requests.post(self.api_url, json=data, headers=headers, timeout=10)
            r.raise_for_status()
            logger.info(f"✅ [{self.device_id}] GPS: ({data['latitude']:.4f}, {data['longitude']:.4f}) | Latency: {data['latency_ms']}ms")
            return True
        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            return False
    
    def run(self, interval=5):
        """Main loop"""
        logger.info(f"🚀 Mobile unit {self.device_id} running")
        try:
            while True:
                telemetry = self.collect_telemetry()
                self.send(telemetry)
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info(f"\n🛑 Stopped")


if __name__ == "__main__":
    unit = MobileUnit(
        device_id="mobile-001",
        api_key="ok_device_002_def456uvw",
        api_url="http://127.0.0.1:8000/v1/telemetry/send"
    )
    unit.run()
