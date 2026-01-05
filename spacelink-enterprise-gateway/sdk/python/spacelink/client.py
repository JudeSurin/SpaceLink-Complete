# sdk/python/spacelink/client.py
"""
SpaceLink Enterprise SDK
Python client library for SpaceLink Enterprise Gateway
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime


class SpaceLinkClient:
    """
    SpaceLink API Client
    
    Example:
        client = SpaceLinkClient(api_key="your-api-key")
        client.send_telemetry(device_id="device-001", latency_ms=45.5)
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """
        Initialize SpaceLink client
        
        Args:
            base_url: API gateway URL
            api_key: Device API key for telemetry submission
            access_token: JWT token for enterprise APIs
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.access_token = access_token
        self.session = requests.Session()
    
    def authenticate(self, username: str, password: str) -> Dict:
        """
        Authenticate and obtain access token
        
        Args:
            username: User's username
            password: User's password
        
        Returns:
            Token response with access_token
        """
        response = self.session.post(
            f"{self.base_url}/v1/auth/token",
            data={"username": username, "password": password},
        )
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        return token_data
    
    def _get_headers(self, use_api_key: bool = False) -> Dict:
        """Get appropriate headers for request"""
        headers = {"Content-Type": "application/json"}
        
        if use_api_key and self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        return headers
    
    # ========================================================================
    # Telemetry Methods
    # ========================================================================
    
    def send_telemetry(
        self,
        device_id: str,
        organization: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        signal_strength: Optional[float] = None,
        latency_ms: Optional[float] = None,
        packet_loss_percent: Optional[float] = None,
        throughput_mbps: Optional[float] = None,
        jitter_ms: Optional[float] = None,
        status: str = "active",
        **kwargs,
    ) -> Dict:
        """
        Send telemetry data
        
        Requires API key authentication.
        """
        telemetry = {
            "device_id": device_id,
            "organization": organization,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": status,
        }
        
        if latitude is not None:
            telemetry["latitude"] = latitude
        if longitude is not None:
            telemetry["longitude"] = longitude
        if signal_strength is not None:
            telemetry["signal_strength"] = signal_strength
        if latency_ms is not None:
            telemetry["latency_ms"] = latency_ms
        if packet_loss_percent is not None:
            telemetry["packet_loss_percent"] = packet_loss_percent
        if throughput_mbps is not None:
            telemetry["throughput_mbps"] = throughput_mbps
        if jitter_ms is not None:
            telemetry["jitter_ms"] = jitter_ms
        
        telemetry.update(kwargs)
        
        response = self.session.post(
            f"{self.base_url}/v1/telemetry/send",
            json=telemetry,
            headers=self._get_headers(use_api_key=True),
        )
        response.raise_for_status()
        return response.json()
    
    def query_telemetry(
        self,
        device_id: Optional[str] = None,
        organization: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Query telemetry data
        
        Requires JWT authentication.
        """
        params = {"limit": limit}
        if device_id:
            params["device_id"] = device_id
        if organization:
            params["organization"] = organization
        if status:
            params["status"] = status
        
        response = self.session.get(
            f"{self.base_url}/v1/telemetry/",
            params=params,
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_latest_telemetry(self) -> List[Dict]:
        """Get latest telemetry for all devices"""
        response = self.session.get(
            f"{self.base_url}/v1/telemetry/latest",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_device_latest(self, device_id: str) -> Dict:
        """Get latest telemetry for specific device"""
        response = self.session.get(
            f"{self.base_url}/v1/telemetry/devices/{device_id}/latest",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_telemetry_summary(self) -> Dict:
        """Get telemetry statistics summary"""
        response = self.session.get(
            f"{self.base_url}/v1/telemetry/stats/summary",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()
    
    # ========================================================================
    # Network Methods
    # ========================================================================
    
    def create_network(
        self,
        name: str,
        organization: str,
        network_type: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> Dict:
        """Create new network configuration"""
        network = {
            "name": name,
            "organization": organization,
            "network_type": network_type,
        }
        if description:
            network["description"] = description
        network.update(kwargs)
        
        response = self.session.post(
            f"{self.base_url}/v1/networks/",
            json=network,
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def list_networks(self, organization: Optional[str] = None) -> List[Dict]:
        """List all networks"""
        params = {}
        if organization:
            params["organization"] = organization
        
        response = self.session.get(
            f"{self.base_url}/v1/networks/",
            params=params,
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_network(self, network_id: str) -> Dict:
        """Get network details"""
        response = self.session.get(
            f"{self.base_url}/v1/networks/{network_id}",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_network_health(self, network_id: str, hours: int = 24) -> Dict:
        """Get network health metrics"""
        response = self.session.get(
            f"{self.base_url}/v1/networks/{network_id}/health",
            params={"hours": hours},
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()
    
    # ========================================================================
    # Partner Methods
    # ========================================================================
    
    def list_partners(self) -> List[Dict]:
        """List all partners"""
        response = self.session.get(
            f"{self.base_url}/v1/partners/",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()
    
    def get_partner(self, partner_id: str) -> Dict:
        """Get partner details"""
        response = self.session.get(
            f"{self.base_url}/v1/partners/{partner_id}",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()
