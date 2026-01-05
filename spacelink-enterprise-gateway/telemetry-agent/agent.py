#!/usr/bin/env python3
"""
SpaceLink Telemetry Agent
Simulates satellite terminal sending network metrics to enterprise gateway
"""

import requests
import time
import random
import yaml
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
import sys
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TelemetryAgent:
    """Network telemetry collection and transmission agent"""
    
    def __init__(self, config_path: str = None):
        """Initialize agent with configuration"""
        if config_path is None:
            # Try to find config.yaml in the same directory as this script
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "config.yaml")
        self.config = self.load_config(config_path)
        self.api_url = self.config['gateway']['url']
        self.api_key = self.config['device']['api_key']
        self.device_id = self.config['device']['device_id']
        self.organization = self.config['device']['organization']
        self.interval = self.config['collection']['interval_seconds']
        
        # Simulated device state
        self.base_latency = self.config['simulation'].get('base_latency_ms', 50)
        self.base_signal = self.config['simulation'].get('base_signal_dbm', -70)
        self.session_start = datetime.now(timezone.utc)
        
        logger.info(f"🛰️  Initialized telemetry agent for device: {self.device_id}")
        logger.info(f"📡 Target gateway: {self.api_url}")
        logger.info(f"⏱️  Collection interval: {self.interval}s")
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"✅ Loaded configuration from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"❌ Config file not found: {config_path}")
            logger.info("Using default configuration...")
            return self.get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"❌ Invalid YAML configuration: {e}")
            sys.exit(1)
    
    def get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'gateway': {
                'url': 'http://127.0.0.1:8000/v1/telemetry/send',
            },
            'device': {
                'api_key': 'ok_device_001_abc123xyz',
                'device_id': 'device-001',
                'organization': 'ACME Corporation',
            },
            'collection': {
                'interval_seconds': 5,
            },
            'simulation': {
                'base_latency_ms': 50,
                'base_signal_dbm': -70,
            },
        }
    
    def collect_telemetry(self) -> Dict:
        """
        Collect network telemetry metrics
        In production, this would interface with actual network hardware
        """
        # Simulate realistic network conditions with some variance
        latency = self.base_latency + random.uniform(-10, 30)
        
        # Occasional latency spikes
        if random.random() < 0.05:  # 5% chance
            latency += random.uniform(50, 200)
        
        # Signal strength variation
        signal_strength = self.base_signal + random.uniform(-5, 5)
        
        # Packet loss (usually low, occasional spikes)
        packet_loss = random.uniform(0, 0.5)
        if random.random() < 0.03:  # 3% chance of degradation
            packet_loss = random.uniform(2, 10)
        
        # Throughput simulation
        throughput = random.uniform(80, 150)  # Mbps
        
        # Jitter
        jitter = random.uniform(1, 5)
        
        # Status determination
        if packet_loss > 5:
            status = "degraded"
        elif latency > 150:
            status = "degraded"
        elif random.random() < 0.01:  # 1% chance of offline
            status = "offline"
        else:
            status = "active"
        
        # Simulated GPS coordinates (slight drift)
        base_lat, base_lon = 47.6062, -122.3321  # Seattle area
        latitude = base_lat + random.uniform(-0.01, 0.01)
        longitude = base_lon + random.uniform(-0.01, 0.01)
        
        telemetry = {
            "device_id": self.device_id,
            "organization": self.organization,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "signal_strength": round(signal_strength, 2),
            "latency_ms": round(latency, 2),
            "packet_loss_percent": round(packet_loss, 2),
            "throughput_mbps": round(throughput, 2),
            "jitter_ms": round(jitter, 2),
            "status": status,
            "firmware_version": "v2.4.1",
        }
        
        if status == "degraded":
            telemetry["error_message"] = "Network performance degradation detected"
        elif status == "offline":
            telemetry["error_message"] = "Connection lost"
        
        return telemetry
    
    def send_telemetry(self, telemetry: Dict) -> bool:
        """
        Send telemetry data to the gateway API
        Returns True if successful, False otherwise
        """
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=telemetry,
                headers=headers,
                timeout=10,
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Log with status indicator
            status_emoji = {
                "active": "✅",
                "degraded": "⚠️ ",
                "offline": "🔴",
                "maintenance": "🔧"
            }.get(telemetry['status'], "📡")
            
            logger.info(
                f"{status_emoji} [{telemetry['device_id']}] "
                f"Latency: {telemetry['latency_ms']:.1f}ms | "
                f"Loss: {telemetry['packet_loss_percent']:.1f}% | "
                f"Signal: {telemetry['signal_strength']:.1f}dBm | "
                f"Status: {telemetry['status']}"
            )
            
            return True
            
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Connection error - gateway unreachable at {self.api_url}")
            return False
        except requests.exceptions.Timeout:
            logger.error(f"⏱️  Request timeout - gateway not responding")
            return False
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP error: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def run(self, iterations: Optional[int] = None):
        """
        Main agent loop
        
        Args:
            iterations: Number of iterations to run. None for infinite.
        """
        logger.info("🚀 Starting telemetry agent...")
        logger.info("Press Ctrl+C to stop\n")
        
        iteration = 0
        failures = 0
        max_consecutive_failures = 5
        
        try:
            while iterations is None or iteration < iterations:
                iteration += 1
                
                # Collect and send telemetry
                telemetry = self.collect_telemetry()
                success = self.send_telemetry(telemetry)
                
                if success:
                    failures = 0  # Reset failure counter
                else:
                    failures += 1
                    if failures >= max_consecutive_failures:
                        logger.error(
                            f"❌ {max_consecutive_failures} consecutive failures. "
                            "Check gateway connectivity and API key."
                        )
                        break
                
                # Wait before next collection
                if iterations is None or iteration < iterations:
                    time.sleep(self.interval)
        
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Telemetry agent stopped by user")
        except Exception as e:
            logger.error(f"💥 Fatal error: {e}")
            sys.exit(1)
        
        # Summary
        logger.info(f"\n📊 Session summary:")
        logger.info(f"   Total iterations: {iteration}")
        logger.info(f"   Success rate: {((iteration-failures)/iteration*100):.1f}%")
        logger.info(f"   Duration: {datetime.now(timezone.utc) - self.session_start}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="SpaceLink Telemetry Agent - Satellite terminal network monitor"
    )
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '-n', '--iterations',
        type=int,
        default=None,
        help='Number of iterations to run (default: infinite)'
    )
    
    args = parser.parse_args()
    
    # Create and run agent
    agent = TelemetryAgent(config_path=args.config)
    agent.run(iterations=args.iterations)


if __name__ == "__main__":
    main()
