"""
QWAMOS Mock Gateway Implementations
Mock implementations for testing Tor, I2P, and DNSCrypt without actual network services
"""

import socket
from typing import Optional, Dict, List
from enum import Enum


class GatewayType(Enum):
    """Gateway types"""
    TOR = "tor"
    I2P = "i2p"
    DNSCRYPT = "dnscrypt"
    VPN = "vpn"


class MockTorGateway:
    """Mock Tor gateway for testing"""

    def __init__(self, socks_port: int = 9050, control_port: int = 9051):
        self.socks_port = socks_port
        self.control_port = control_port
        self.is_connected = False
        self.circuits = []

    def connect(self) -> bool:
        """Mock Tor connection"""
        try:
            # Simulate connection check
            self.is_connected = True
            return True
        except Exception:
            self.is_connected = False
            return False

    def disconnect(self):
        """Mock Tor disconnection"""
        self.is_connected = False
        self.circuits = []

    def check_connectivity(self) -> bool:
        """Check if Tor is accessible"""
        return self.is_connected

    def get_new_circuit(self) -> str:
        """Request new Tor circuit"""
        if not self.is_connected:
            raise RuntimeError("Not connected to Tor")

        circuit_id = f"circuit_{len(self.circuits) + 1}"
        self.circuits.append(circuit_id)
        return circuit_id

    def get_exit_ip(self) -> str:
        """Get current Tor exit node IP"""
        if not self.is_connected:
            raise RuntimeError("Not connected to Tor")
        return "198.51.100.42"  # Mock exit IP

    def is_running(self) -> bool:
        """Check if Tor service is running"""
        return self.is_connected


class MockI2PGateway:
    """Mock I2P gateway for testing"""

    def __init__(self, sam_port: int = 7656, http_port: int = 4444):
        self.sam_port = sam_port
        self.http_port = http_port
        self.is_connected = False
        self.tunnels = []

    def connect(self) -> bool:
        """Mock I2P connection"""
        try:
            self.is_connected = True
            return True
        except Exception:
            self.is_connected = False
            return False

    def disconnect(self):
        """Mock I2P disconnection"""
        self.is_connected = False
        self.tunnels = []

    def check_connectivity(self) -> bool:
        """Check if I2P is accessible"""
        return self.is_connected

    def create_tunnel(self, tunnel_type: str = "client") -> str:
        """Create I2P tunnel"""
        if not self.is_connected:
            raise RuntimeError("Not connected to I2P")

        tunnel_id = f"{tunnel_type}_tunnel_{len(self.tunnels) + 1}"
        self.tunnels.append({"id": tunnel_id, "type": tunnel_type})
        return tunnel_id

    def get_tunnel_status(self, tunnel_id: str) -> Dict:
        """Get tunnel status"""
        for tunnel in self.tunnels:
            if tunnel["id"] == tunnel_id:
                return {"status": "active", "peers": 5}
        raise ValueError(f"Tunnel {tunnel_id} not found")

    def is_running(self) -> bool:
        """Check if I2P service is running"""
        return self.is_connected


class MockDNSCryptGateway:
    """Mock DNSCrypt gateway for testing"""

    def __init__(self, listen_port: int = 53):
        self.listen_port = listen_port
        self.is_running = False
        self.resolver = "cloudflare"
        self.queries = []

    def start(self) -> bool:
        """Start DNSCrypt proxy"""
        self.is_running = True
        return True

    def stop(self):
        """Stop DNSCrypt proxy"""
        self.is_running = False
        self.queries = []

    def set_resolver(self, resolver: str):
        """Set DNSCrypt resolver"""
        if not self.is_running:
            raise RuntimeError("DNSCrypt not running")
        self.resolver = resolver

    def query(self, domain: str) -> str:
        """Mock DNS query"""
        if not self.is_running:
            raise RuntimeError("DNSCrypt not running")

        self.queries.append(domain)
        # Return mock IP based on domain
        if "localhost" in domain:
            return "127.0.0.1"
        return "93.184.216.34"  # Mock IP

    def get_resolver_info(self) -> Dict:
        """Get current resolver info"""
        return {
            "name": self.resolver,
            "protocol": "DNSCrypt",
            "dnssec": True
        }

    def check_status(self) -> bool:
        """Check DNSCrypt status"""
        return self.is_running


class MockVPNGateway:
    """Mock VPN gateway for testing"""

    def __init__(self, interface: str = "tun0"):
        self.interface = interface
        self.is_connected = False
        self.tunnel_ip = None

    def connect(self, server: str, protocol: str = "wireguard") -> bool:
        """Mock VPN connection"""
        self.is_connected = True
        self.tunnel_ip = "10.8.0.2"
        return True

    def disconnect(self):
        """Mock VPN disconnection"""
        self.is_connected = False
        self.tunnel_ip = None

    def check_connectivity(self) -> bool:
        """Check if VPN is connected"""
        return self.is_connected

    def get_tunnel_ip(self) -> Optional[str]:
        """Get VPN tunnel IP"""
        return self.tunnel_ip

    def enforce_killswitch(self) -> bool:
        """Enable VPN killswitch"""
        if not self.is_connected:
            raise RuntimeError("VPN not connected")
        return True


class MockGatewayRouter:
    """Mock gateway router for managing multiple gateways"""

    def __init__(self):
        self.gateways = {
            GatewayType.TOR: MockTorGateway(),
            GatewayType.I2P: MockI2PGateway(),
            GatewayType.DNSCRYPT: MockDNSCryptGateway(),
            GatewayType.VPN: MockVPNGateway()
        }
        self.active_gateway = None

    def activate_gateway(self, gateway_type: GatewayType) -> bool:
        """Activate specific gateway"""
        if gateway_type not in self.gateways:
            raise ValueError(f"Unknown gateway type: {gateway_type}")

        gateway = self.gateways[gateway_type]

        if gateway_type == GatewayType.TOR:
            success = gateway.connect()
        elif gateway_type == GatewayType.I2P:
            success = gateway.connect()
        elif gateway_type == GatewayType.DNSCRYPT:
            success = gateway.start()
        elif gateway_type == GatewayType.VPN:
            success = gateway.connect("vpn.example.com")
        else:
            success = False

        if success:
            self.active_gateway = gateway_type

        return success

    def deactivate_gateway(self, gateway_type: GatewayType):
        """Deactivate specific gateway"""
        if gateway_type not in self.gateways:
            raise ValueError(f"Unknown gateway type: {gateway_type}")

        gateway = self.gateways[gateway_type]

        if gateway_type == GatewayType.TOR:
            gateway.disconnect()
        elif gateway_type == GatewayType.I2P:
            gateway.disconnect()
        elif gateway_type == GatewayType.DNSCRYPT:
            gateway.stop()
        elif gateway_type == GatewayType.VPN:
            gateway.disconnect()

        if self.active_gateway == gateway_type:
            self.active_gateway = None

    def get_gateway(self, gateway_type: GatewayType):
        """Get gateway instance"""
        return self.gateways.get(gateway_type)

    def get_active_gateway(self) -> Optional[GatewayType]:
        """Get currently active gateway"""
        return self.active_gateway

    def check_all_gateways(self) -> Dict[str, bool]:
        """Check status of all gateways"""
        return {
            "tor": self.gateways[GatewayType.TOR].is_running(),
            "i2p": self.gateways[GatewayType.I2P].is_running(),
            "dnscrypt": self.gateways[GatewayType.DNSCRYPT].check_status(),
            "vpn": self.gateways[GatewayType.VPN].check_connectivity()
        }
