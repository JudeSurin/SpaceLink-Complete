#!/usr/bin/env python3
"""SpaceLink IoT Gateway - Industrial/Remote Site"""

import requests
import subprocess
import platform
import re
import time
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IoTGateway:
    """IoT Gateway for industrial sites"""
    
    def __init__(self, device_id, api_key, api_url, site_name="Remote Site"):
        self.device_id = device_id
        self.api_key = api_key
        self.api_url = api_url
        self.organization = "Industrial IoT Corp"
        self.site_name = site_name
        self.system = platform.system()
        
        logger.info(f"🏭 IoT Gateway {device_id} at {site_name} initialized")
    
    def ping_test(self):
        """REAL ping test"""
        try:
            cmd = ['ping', '-n' if self.system == 'Windows' else '-c', '4', '1.1.1.1']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
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
        """Collect metrics"""
        latency, packet_loss = self.ping_test()
        
        if packet_loss > 15:
            status = "offline"
        elif packet_loss > 3 or (latency and latency > 120):
            status = "degraded"
        else:
            status = "active"
        
        return {
            "device_id": self.device_id,
            "organization": self.organization,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": 34.0522,
            "longitude": -118.2437,
            "signal_strength": -68,
            "latency_ms": latency,
            "packet_loss_percent": packet_loss,
            "throughput_mbps": 95,
            "jitter_ms": 2.8,
            "status": status,
            "firmware_version": "v1.2-iot"
        }
    
    def send(self, data):
        """Send to gateway"""
        try:
            headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
            r = requests.post(self.api_url, json=data, headers=headers, timeout=10)
            r.raise_for_status()
            logger.info(f"✅ [{self.device_id}] {self.site_name} - Latency: {data['latency_ms']}ms, Status: {data['status']}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            return False
    
    def run(self, interval=10):
        """Main loop"""
        logger.info(f"🚀 IoT Gateway {self.device_id} running")
        try:
            while True:
                telemetry = self.collect_telemetry()
                self.send(telemetry)
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info(f"\n🛑 Stopped")


if __name__ == "__main__":
    gateway = IoTGateway(
        device_id="iot-001",
        api_key="ok_device_003_ghi789rst",
        api_url="http://127.0.0.1:8000/v1/telemetry/send",
        site_name="Oil Rig Platform 7"
    )
    gateway.run()
