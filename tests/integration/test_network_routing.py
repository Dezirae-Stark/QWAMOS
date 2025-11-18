"""
QWAMOS Network Routing Integration Tests
Tests for network routing through Tor, I2P, VPN, and gateway combinations
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
from tests.helpers.mock_vm import (
    MockQEMUVM,
    MockVMIsolation
)


class TestTorRouting:
    """Test Tor network routing"""

    def test_tor_routing_basic(self):
        """Test basic Tor routing"""
        tor = MockTorGateway()
        vm = MockQEMUVM("test_vm")
        vm.start()

        # Connect Tor
        assert tor.connect() is True

        # Verify connectivity
        assert tor.check_connectivity() is True
        assert tor.get_exit_ip() is not None

    def test_tor_routing_with_circuit_change(self):
        """Test Tor routing with circuit changes"""
        tor = MockTorGateway()
        tor.connect()

        circuit1 = tor.get_new_circuit()
        circuit2 = tor.get_new_circuit()

        assert circuit1 != circuit2
        assert len(tor.circuits) == 2

    def test_tor_routing_with_vm_isolation(self):
        """Test Tor routing with VM network isolation"""
        tor = MockTorGateway()
        vm = MockQEMUVM("test_vm")
        isolation = MockVMIsolation(vm)

        # Enable network isolation
        isolation.enable_network_isolation()

        # Allow Tor exit nodes
        isolation.add_allowed_host("tor-exit-node")

        tor.connect()

        assert isolation.check_network_access("tor-exit-node") is True
        assert isolation.check_network_access("direct-internet") is False

    def test_tor_routing_multiple_vms(self):
        """Test Tor routing with multiple VMs"""
        tor = MockTorGateway()
        tor.connect()

        vms = [MockQEMUVM(f"vm_{i}") for i in range(3)]
        for vm in vms:
            vm.start()

        # All VMs should be able to use same Tor gateway
        assert tor.is_running() is True
        for vm in vms:
            assert vm.state.value == "running"


class TestI2PRouting:
    """Test I2P network routing"""

    def test_i2p_routing_basic(self):
        """Test basic I2P routing"""
        i2p = MockI2PGateway()
        vm = MockQEMUVM("test_vm")
        vm.start()

        # Connect I2P
        assert i2p.connect() is True

        # Create tunnel
        tunnel = i2p.create_tunnel("client")
        assert tunnel is not None

        # Verify tunnel status
        status = i2p.get_tunnel_status(tunnel)
        assert status["status"] == "active"

    def test_i2p_routing_with_multiple_tunnels(self):
        """Test I2P routing with multiple tunnels"""
        i2p = MockI2PGateway()
        i2p.connect()

        client_tunnel = i2p.create_tunnel("client")
        server_tunnel = i2p.create_tunnel("server")

        assert client_tunnel != server_tunnel
        assert len(i2p.tunnels) == 2

    def test_i2p_routing_with_vm_isolation(self):
        """Test I2P routing with VM network isolation"""
        i2p = MockI2PGateway()
        vm = MockQEMUVM("test_vm")
        isolation = MockVMIsolation(vm)

        # Enable network isolation
        isolation.enable_network_isolation()

        # Allow I2P
        isolation.add_allowed_host("i2p-router")

        i2p.connect()
        tunnel = i2p.create_tunnel()

        assert isolation.check_network_access("i2p-router") is True


class TestVPNRouting:
    """Test VPN network routing"""

    def test_vpn_routing_basic(self):
        """Test basic VPN routing"""
        vpn = MockVPNGateway()
        vm = MockQEMUVM("test_vm")
        vm.start()

        # Connect VPN
        assert vpn.connect("vpn.example.com") is True

        # Verify tunnel IP
        tunnel_ip = vpn.get_tunnel_ip()
        assert tunnel_ip is not None
        assert tunnel_ip.startswith("10.")

    def test_vpn_routing_with_killswitch(self):
        """Test VPN routing with killswitch"""
        vpn = MockVPNGateway()
        vpn.connect("vpn.example.com")

        # Enable killswitch
        assert vpn.enforce_killswitch() is True

        # Killswitch should prevent non-VPN traffic
        assert vpn.is_connected is True

    def test_vpn_routing_with_vm_isolation(self):
        """Test VPN routing with VM network isolation"""
        vpn = MockVPNGateway()
        vm = MockQEMUVM("test_vm")
        isolation = MockVMIsolation(vm)

        # Enable network isolation
        isolation.enable_network_isolation()

        # Allow VPN gateway
        isolation.add_allowed_host("vpn.example.com")

        vpn.connect("vpn.example.com")

        assert isolation.check_network_access("vpn.example.com") is True
        assert isolation.check_network_access("other.com") is False


class TestDNSCryptRouting:
    """Test DNSCrypt routing"""

    def test_dnscrypt_routing_basic(self):
        """Test basic DNSCrypt routing"""
        dnscrypt = MockDNSCryptGateway()

        # Start DNSCrypt
        assert dnscrypt.start() is True

        # Query domain
        ip = dnscrypt.query("example.com")
        assert ip is not None

    def test_dnscrypt_routing_with_resolver_change(self):
        """Test DNSCrypt routing with resolver changes"""
        dnscrypt = MockDNSCryptGateway()
        dnscrypt.start()

        dnscrypt.set_resolver("cloudflare")
        assert dnscrypt.resolver == "cloudflare"

        dnscrypt.set_resolver("quad9")
        assert dnscrypt.resolver == "quad9"

    def test_dnscrypt_routing_with_vm(self):
        """Test DNSCrypt routing with VM"""
        dnscrypt = MockDNSCryptGateway()
        vm = MockQEMUVM("test_vm")

        dnscrypt.start()
        vm.start()

        # VM should use DNSCrypt for DNS queries
        ip = dnscrypt.query("internal.vm.local")
        assert ip is not None


class TestGatewayRouting:
    """Test gateway routing with multiple gateways"""

    def test_single_gateway_routing(self):
        """Test routing through single gateway"""
        router = MockGatewayRouter()

        # Activate Tor
        router.activate_gateway(GatewayType.TOR)

        assert router.active_gateway == GatewayType.TOR
        tor = router.get_gateway(GatewayType.TOR)
        assert tor.is_running() is True

    def test_gateway_switching(self):
        """Test switching between gateways"""
        router = MockGatewayRouter()

        # Start with Tor
        router.activate_gateway(GatewayType.TOR)
        assert router.active_gateway == GatewayType.TOR

        # Switch to I2P
        router.activate_gateway(GatewayType.I2P)
        assert router.active_gateway == GatewayType.I2P

    def test_multiple_gateway_routing(self):
        """Test routing through multiple gateways simultaneously"""
        router = MockGatewayRouter()

        # Activate multiple gateways
        router.activate_gateway(GatewayType.TOR)
        router.activate_gateway(GatewayType.DNSCRYPT)
        router.activate_gateway(GatewayType.VPN)

        # Verify all active
        status = router.check_all_gateways()
        assert status["tor"] is True
        assert status["dnscrypt"] is True
        assert status["vpn"] is True

    def test_layered_gateway_routing(self):
        """Test layered gateway routing (VPN -> Tor -> I2P)"""
        router = MockGatewayRouter()

        # Layer 1: VPN
        vpn = router.get_gateway(GatewayType.VPN)
        router.activate_gateway(GatewayType.VPN)
        assert vpn.check_connectivity() is True

        # Layer 2: Tor over VPN
        tor = router.get_gateway(GatewayType.TOR)
        router.activate_gateway(GatewayType.TOR)
        assert tor.is_running() is True

        # Layer 3: I2P over Tor over VPN
        i2p = router.get_gateway(GatewayType.I2P)
        router.activate_gateway(GatewayType.I2P)
        assert i2p.is_running() is True

    def test_gateway_failover(self):
        """Test gateway failover"""
        router = MockGatewayRouter()

        # Primary: Tor
        router.activate_gateway(GatewayType.TOR)

        # Deactivate Tor
        router.deactivate_gateway(GatewayType.TOR)

        # Fallback: I2P
        router.activate_gateway(GatewayType.I2P)

        assert router.active_gateway == GatewayType.I2P


class TestVMNetworkRouting:
    """Test VM network routing integration"""

    def test_vm_routing_through_tor(self):
        """Test VM routing through Tor"""
        router = MockGatewayRouter()
        vm = MockQEMUVM("test_vm")
        isolation = MockVMIsolation(vm)

        # Setup
        vm.start()
        isolation.enable_network_isolation()
        isolation.add_allowed_host("tor-gateway")

        # Route through Tor
        router.activate_gateway(GatewayType.TOR)

        assert isolation.check_network_access("tor-gateway") is True

    def test_vm_routing_with_dns(self):
        """Test VM routing with DNSCrypt"""
        router = MockGatewayRouter()
        vm = MockQEMUVM("test_vm")
        vm.start()

        # Activate DNSCrypt
        router.activate_gateway(GatewayType.DNSCRYPT)

        dnscrypt = router.get_gateway(GatewayType.DNSCRYPT)
        ip = dnscrypt.query("vm.local")

        assert ip is not None

    def test_vm_routing_multiple_gateways(self):
        """Test VM routing through multiple gateways"""
        router = MockGatewayRouter()
        vm = MockQEMUVM("test_vm")
        isolation = MockVMIsolation(vm)

        vm.start()
        isolation.enable_network_isolation()

        # Allow multiple gateways
        isolation.add_allowed_host("vpn-gateway")
        isolation.add_allowed_host("tor-gateway")

        # Activate both
        router.activate_gateway(GatewayType.VPN)
        router.activate_gateway(GatewayType.TOR)

        assert isolation.check_network_access("vpn-gateway") is True
        assert isolation.check_network_access("tor-gateway") is True

    def test_vm_routing_isolation_enforcement(self):
        """Test VM routing with strict isolation"""
        router = MockGatewayRouter()
        vm = MockQEMUVM("test_vm")
        isolation = MockVMIsolation(vm)

        vm.start()
        isolation.enable_network_isolation()

        # Only allow Tor
        isolation.add_allowed_host("tor-gateway")

        # Activate Tor
        router.activate_gateway(GatewayType.TOR)

        # Verify isolation
        assert isolation.check_network_access("tor-gateway") is True
        assert isolation.check_network_access("direct-internet") is False
        assert isolation.check_network_access("i2p-gateway") is False


class TestNetworkRoutingPerformance:
    """Test network routing performance and reliability"""

    def test_routing_connection_stability(self):
        """Test routing connection stability"""
        tor = MockTorGateway()
        tor.connect()

        # Simulate multiple connections
        for _ in range(10):
            assert tor.is_running() is True
            assert tor.check_connectivity() is True

    def test_routing_gateway_recovery(self):
        """Test routing gateway recovery after failure"""
        tor = MockTorGateway()

        # Connect
        tor.connect()
        assert tor.is_running() is True

        # Disconnect (simulated failure)
        tor.disconnect()
        assert tor.is_running() is False

        # Reconnect (recovery)
        tor.connect()
        assert tor.is_running() is True

    def test_routing_multiple_vms_load(self):
        """Test routing with multiple VMs under load"""
        router = MockGatewayRouter()
        router.activate_gateway(GatewayType.TOR)

        # Create multiple VMs
        vms = [MockQEMUVM(f"vm_{i}") for i in range(10)]

        # Start all VMs
        for vm in vms:
            vm.start()

        # Verify all VMs are running
        assert all(vm.state.value == "running" for vm in vms)

        # Verify Tor is still operational
        tor = router.get_gateway(GatewayType.TOR)
        assert tor.is_running() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
