"""
QWAMOS Gateway Unit Tests
Tests for Tor, I2P, DNSCrypt, and VPN gateway implementations
"""

import pytest
from tests.helpers.mock_gateway import (
    MockTorGateway,
    MockI2PGateway,
    MockDNSCryptGateway,
    MockVPNGateway,
    MockGatewayRouter,
    GatewayType
)


class TestTorGateway:
    """Test Tor gateway functionality"""

    def test_tor_connection(self):
        """Test Tor connection"""
        tor = MockTorGateway()
        assert tor.connect() is True
        assert tor.is_connected is True
        assert tor.is_running() is True

    def test_tor_disconnection(self):
        """Test Tor disconnection"""
        tor = MockTorGateway()
        tor.connect()
        tor.disconnect()
        assert tor.is_connected is False
        assert tor.is_running() is False

    def test_tor_connectivity_check(self):
        """Test Tor connectivity check"""
        tor = MockTorGateway()
        assert tor.check_connectivity() is False

        tor.connect()
        assert tor.check_connectivity() is True

    def test_tor_new_circuit(self):
        """Test Tor new circuit request"""
        tor = MockTorGateway()
        tor.connect()

        circuit1 = tor.get_new_circuit()
        circuit2 = tor.get_new_circuit()

        assert circuit1 != circuit2
        assert len(tor.circuits) == 2

    def test_tor_new_circuit_fails_when_disconnected(self):
        """Test new circuit fails when not connected"""
        tor = MockTorGateway()

        with pytest.raises(RuntimeError, match="Not connected to Tor"):
            tor.get_new_circuit()

    def test_tor_exit_ip(self):
        """Test Tor exit IP retrieval"""
        tor = MockTorGateway()
        tor.connect()

        exit_ip = tor.get_exit_ip()
        assert exit_ip is not None
        assert len(exit_ip) > 0

    def test_tor_exit_ip_fails_when_disconnected(self):
        """Test exit IP fails when not connected"""
        tor = MockTorGateway()

        with pytest.raises(RuntimeError, match="Not connected to Tor"):
            tor.get_exit_ip()

    def test_tor_custom_ports(self):
        """Test Tor with custom ports"""
        tor = MockTorGateway(socks_port=9150, control_port=9151)
        assert tor.socks_port == 9150
        assert tor.control_port == 9151


class TestI2PGateway:
    """Test I2P gateway functionality"""

    def test_i2p_connection(self):
        """Test I2P connection"""
        i2p = MockI2PGateway()
        assert i2p.connect() is True
        assert i2p.is_connected is True
        assert i2p.is_running() is True

    def test_i2p_disconnection(self):
        """Test I2P disconnection"""
        i2p = MockI2PGateway()
        i2p.connect()
        i2p.disconnect()
        assert i2p.is_connected is False
        assert i2p.is_running() is False

    def test_i2p_connectivity_check(self):
        """Test I2P connectivity check"""
        i2p = MockI2PGateway()
        assert i2p.check_connectivity() is False

        i2p.connect()
        assert i2p.check_connectivity() is True

    def test_i2p_create_tunnel(self):
        """Test I2P tunnel creation"""
        i2p = MockI2PGateway()
        i2p.connect()

        tunnel1 = i2p.create_tunnel("client")
        tunnel2 = i2p.create_tunnel("server")

        assert tunnel1 != tunnel2
        assert len(i2p.tunnels) == 2
        assert "client" in tunnel1
        assert "server" in tunnel2

    def test_i2p_create_tunnel_fails_when_disconnected(self):
        """Test tunnel creation fails when not connected"""
        i2p = MockI2PGateway()

        with pytest.raises(RuntimeError, match="Not connected to I2P"):
            i2p.create_tunnel()

    def test_i2p_tunnel_status(self):
        """Test I2P tunnel status"""
        i2p = MockI2PGateway()
        i2p.connect()

        tunnel_id = i2p.create_tunnel()
        status = i2p.get_tunnel_status(tunnel_id)

        assert status["status"] == "active"
        assert status["peers"] > 0

    def test_i2p_tunnel_status_not_found(self):
        """Test tunnel status for non-existent tunnel"""
        i2p = MockI2PGateway()
        i2p.connect()

        with pytest.raises(ValueError, match="not found"):
            i2p.get_tunnel_status("nonexistent_tunnel")

    def test_i2p_custom_ports(self):
        """Test I2P with custom ports"""
        i2p = MockI2PGateway(sam_port=7777, http_port=4445)
        assert i2p.sam_port == 7777
        assert i2p.http_port == 4445


class TestDNSCryptGateway:
    """Test DNSCrypt gateway functionality"""

    def test_dnscrypt_start(self):
        """Test DNSCrypt start"""
        dnscrypt = MockDNSCryptGateway()
        assert dnscrypt.start() is True
        assert dnscrypt.is_running is True
        assert dnscrypt.check_status() is True

    def test_dnscrypt_stop(self):
        """Test DNSCrypt stop"""
        dnscrypt = MockDNSCryptGateway()
        dnscrypt.start()
        dnscrypt.stop()
        assert dnscrypt.is_running is False
        assert dnscrypt.check_status() is False

    def test_dnscrypt_set_resolver(self):
        """Test DNSCrypt resolver setting"""
        dnscrypt = MockDNSCryptGateway()
        dnscrypt.start()

        dnscrypt.set_resolver("quad9")
        assert dnscrypt.resolver == "quad9"

    def test_dnscrypt_set_resolver_fails_when_stopped(self):
        """Test set resolver fails when not running"""
        dnscrypt = MockDNSCryptGateway()

        with pytest.raises(RuntimeError, match="not running"):
            dnscrypt.set_resolver("cloudflare")

    def test_dnscrypt_query(self):
        """Test DNSCrypt query"""
        dnscrypt = MockDNSCryptGateway()
        dnscrypt.start()

        ip = dnscrypt.query("example.com")
        assert ip is not None
        assert len(ip) > 0
        assert "example.com" in dnscrypt.queries

    def test_dnscrypt_query_fails_when_stopped(self):
        """Test query fails when not running"""
        dnscrypt = MockDNSCryptGateway()

        with pytest.raises(RuntimeError, match="not running"):
            dnscrypt.query("example.com")

    def test_dnscrypt_resolver_info(self):
        """Test DNSCrypt resolver info"""
        dnscrypt = MockDNSCryptGateway()
        dnscrypt.start()

        info = dnscrypt.get_resolver_info()
        assert info["protocol"] == "DNSCrypt"
        assert info["dnssec"] is True

    def test_dnscrypt_custom_port(self):
        """Test DNSCrypt with custom port"""
        dnscrypt = MockDNSCryptGateway(listen_port=5353)
        assert dnscrypt.listen_port == 5353


class TestVPNGateway:
    """Test VPN gateway functionality"""

    def test_vpn_connection(self):
        """Test VPN connection"""
        vpn = MockVPNGateway()
        assert vpn.connect("vpn.example.com") is True
        assert vpn.is_connected is True
        assert vpn.check_connectivity() is True

    def test_vpn_disconnection(self):
        """Test VPN disconnection"""
        vpn = MockVPNGateway()
        vpn.connect("vpn.example.com")
        vpn.disconnect()
        assert vpn.is_connected is False
        assert vpn.check_connectivity() is False

    def test_vpn_tunnel_ip(self):
        """Test VPN tunnel IP"""
        vpn = MockVPNGateway()
        assert vpn.get_tunnel_ip() is None

        vpn.connect("vpn.example.com")
        tunnel_ip = vpn.get_tunnel_ip()
        assert tunnel_ip is not None
        assert tunnel_ip.startswith("10.")

    def test_vpn_killswitch(self):
        """Test VPN killswitch"""
        vpn = MockVPNGateway()
        vpn.connect("vpn.example.com")

        assert vpn.enforce_killswitch() is True

    def test_vpn_killswitch_fails_when_disconnected(self):
        """Test killswitch fails when not connected"""
        vpn = MockVPNGateway()

        with pytest.raises(RuntimeError, match="not connected"):
            vpn.enforce_killswitch()

    def test_vpn_custom_interface(self):
        """Test VPN with custom interface"""
        vpn = MockVPNGateway(interface="wg0")
        assert vpn.interface == "wg0"


class TestGatewayRouter:
    """Test gateway router functionality"""

    def test_gateway_router_initialization(self):
        """Test gateway router initialization"""
        router = MockGatewayRouter()
        assert len(router.gateways) == 4
        assert router.active_gateway is None

    def test_activate_tor_gateway(self):
        """Test activating Tor gateway"""
        router = MockGatewayRouter()
        assert router.activate_gateway(GatewayType.TOR) is True
        assert router.active_gateway == GatewayType.TOR

    def test_activate_i2p_gateway(self):
        """Test activating I2P gateway"""
        router = MockGatewayRouter()
        assert router.activate_gateway(GatewayType.I2P) is True
        assert router.active_gateway == GatewayType.I2P

    def test_activate_dnscrypt_gateway(self):
        """Test activating DNSCrypt gateway"""
        router = MockGatewayRouter()
        assert router.activate_gateway(GatewayType.DNSCRYPT) is True
        assert router.active_gateway == GatewayType.DNSCRYPT

    def test_activate_vpn_gateway(self):
        """Test activating VPN gateway"""
        router = MockGatewayRouter()
        assert router.activate_gateway(GatewayType.VPN) is True
        assert router.active_gateway == GatewayType.VPN

    def test_deactivate_gateway(self):
        """Test deactivating gateway"""
        router = MockGatewayRouter()
        router.activate_gateway(GatewayType.TOR)
        router.deactivate_gateway(GatewayType.TOR)
        assert router.active_gateway is None

    def test_get_gateway(self):
        """Test getting gateway instance"""
        router = MockGatewayRouter()
        tor = router.get_gateway(GatewayType.TOR)
        assert isinstance(tor, MockTorGateway)

    def test_get_active_gateway(self):
        """Test getting active gateway"""
        router = MockGatewayRouter()
        assert router.get_active_gateway() is None

        router.activate_gateway(GatewayType.TOR)
        assert router.get_active_gateway() == GatewayType.TOR

    def test_check_all_gateways(self):
        """Test checking all gateway statuses"""
        router = MockGatewayRouter()
        status = router.check_all_gateways()

        assert "tor" in status
        assert "i2p" in status
        assert "dnscrypt" in status
        assert "vpn" in status
        assert all(s is False for s in status.values())

    def test_multiple_gateway_activation(self):
        """Test activating multiple gateways"""
        router = MockGatewayRouter()

        router.activate_gateway(GatewayType.TOR)
        router.activate_gateway(GatewayType.DNSCRYPT)

        # Both should be active
        tor = router.get_gateway(GatewayType.TOR)
        dnscrypt = router.get_gateway(GatewayType.DNSCRYPT)

        assert tor.is_running() is True
        assert dnscrypt.check_status() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
