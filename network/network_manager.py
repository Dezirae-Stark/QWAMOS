#!/usr/bin/env python3
"""
QWAMOS Network Manager (Phase 5 - Network Isolation)

Central controller for all network services and routing modes.

Manages:
- Tor anonymity service
- I2P (Purple I2P) anonymity network
- DNSCrypt encrypted DNS
- VPN (WireGuard with post-quantum crypto)
- Network routing mode switching
- Service monitoring and health checks
"""

import sys
import subprocess
import json
import time
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

# Add network controllers to path
sys.path.insert(0, str(Path(__file__).parent))

from tor.tor_controller import TorController
from i2p.i2p_controller import I2PController
from dnscrypt.dnscrypt_controller import DNSCryptController
from vpn.vpn_controller import VPNController


class NetworkMode(Enum):
    """Available network routing modes"""
    DIRECT = "direct"
    TOR_ONLY = "tor-only"
    TOR_DNSCRYPT = "tor-dnscrypt"
    TOR_I2P_PARALLEL = "tor-i2p-parallel"
    I2P_ONLY = "i2p-only"
    MAXIMUM_ANONYMITY = "maximum-anonymity"


class NetworkManager:
    """Main network manager for QWAMOS Phase 5"""

    def __init__(self, config_dir: str = "/opt/qwamos/network"):
        self.config_dir = Path(config_dir)
        self.current_mode = NetworkMode.TOR_DNSCRYPT  # Default mode

        # Initialize service controllers
        self.services = {
            'tor': TorController(str(self.config_dir / "tor")),
            'i2p': I2PController(str(self.config_dir / "i2p")),
            'dnscrypt': DNSCryptController(str(self.config_dir / "dnscrypt")),
            'vpn': VPNController(str(self.config_dir / "vpn"))
        }

    def switch_mode(self, mode: NetworkMode, config: Dict = None):
        """
        Switch to a different network routing mode

        Args:
            mode: NetworkMode to switch to
            config: Optional additional configuration

        Example:
            nm.switch_mode(NetworkMode.TOR_ONLY)
            nm.switch_mode(NetworkMode.MAXIMUM_ANONYMITY, {'use_bridges': True})
        """
        print(f"\n{'='*60}")
        print(f"Switching Network Mode")
        print(f"From: {self.current_mode.value}")
        print(f"To:   {mode.value}")
        print(f"{'='*60}\n")

        # Step 1: Stop all currently running services
        print("Step 1: Stopping all services...")
        self.stop_all_services()

        # Step 2: Load mode configuration
        print(f"\nStep 2: Loading configuration for {mode.value}...")
        mode_config = self._load_mode_config(mode)

        # Merge with provided config
        if config:
            mode_config.update(config)

        # Step 3: Start required services based on mode
        print("\nStep 3: Starting services...")

        # Start VPN if configured
        if mode_config.get('vpn', {}).get('enabled', False):
            print("   Starting VPN...")
            self.services['vpn'].start(mode_config.get('vpn', {}))
            time.sleep(3)  # Let VPN establish

        if mode == NetworkMode.DIRECT:
            print("   Direct mode - no anonymization services")

        elif mode == NetworkMode.TOR_ONLY:
            self.services['tor'].start(mode_config.get('tor', {}))

        elif mode == NetworkMode.TOR_DNSCRYPT:
            self.services['dnscrypt'].start(mode_config.get('dnscrypt', {}))
            time.sleep(2)  # Let DNSCrypt initialize
            self.services['tor'].start(mode_config.get('tor', {}))

        elif mode == NetworkMode.TOR_I2P_PARALLEL:
            self.services['dnscrypt'].start(mode_config.get('dnscrypt', {}))
            time.sleep(2)
            self.services['tor'].start(mode_config.get('tor', {}))
            self.services['i2p'].start(mode_config.get('i2p', {}))

        elif mode == NetworkMode.I2P_ONLY:
            self.services['i2p'].start(mode_config.get('i2p', {}))

        elif mode == NetworkMode.MAXIMUM_ANONYMITY:
            # CRITICAL FIX: Start Tor BEFORE I2P so I2P can chain through it
            self.services['dnscrypt'].start(mode_config.get('dnscrypt', {}))
            time.sleep(2)
            print("   Starting Tor (required for I2P chaining)...")
            self.services['tor'].start(mode_config.get('tor', {}))
            time.sleep(5)  # Wait for Tor to establish circuits
            print("   Starting I2P (chained through Tor)...")
            self.services['i2p'].start(mode_config.get('i2p', {}))
            time.sleep(3)  # Wait for I2P to initialize

        # Step 4: Apply routing rules (TODO: Implement firewall rules)
        print("\nStep 4: Applying routing rules...")
        self._apply_routing_rules(mode, mode_config)

        # Step 5: Update current mode
        self.current_mode = mode
        print(f"\n✅ Successfully switched to {mode.value}\n")
        print(f"{'='*60}\n")

    def stop_all_services(self):
        """Stop all network services"""
        for name, service in self.services.items():
            if service.is_running():
                print(f"   Stopping {name}...")
                service.stop()

    def get_status(self) -> Dict:
        """
        Get status of all network services

        Returns:
            Dict with current mode and service statuses
        """
        status = {
            'current_mode': self.current_mode.value,
            'timestamp': time.time(),
            'services': {}
        }

        for name, service in self.services.items():
            status['services'][name] = {
                'running': service.is_running(),
                'details': service.get_status() if service.is_running() else None
            }

        return status

    def test_connectivity(self) -> Dict:
        """
        Test network connectivity and anonymity

        Returns:
            Dict with test results:
                - internet: bool - Internet connectivity
                - dns: dict - DNS resolution test
                - ip_leak: dict - IP leak test results
                - tor_circuit: dict - Tor circuit info (if Tor enabled)
                - i2p_status: dict - I2P status (if I2P enabled)
        """
        print("\n" + "="*60)
        print("Network Connectivity Test")
        print("="*60 + "\n")

        results = {}

        # Test 1: Internet connectivity
        print("Test 1: Internet connectivity...")
        results['internet'] = self._test_internet()
        print(f"   Result: {'✅ Connected' if results['internet'] else '❌ No connection'}\n")

        # Test 2: DNS resolution
        print("Test 2: DNS resolution...")
        results['dns'] = self._test_dns()
        print(f"   Result: {'✅ Working' if results['dns'].get('success') else '❌ Failed'}")
        if results['dns'].get('success'):
            print(f"   Encrypted: {'✅ Yes' if results['dns'].get('encrypted') else '❌ No'}\n")

        # Test 3: IP leak test
        print("Test 3: IP leak detection...")
        results['ip_leak'] = self._test_ip_leak()
        if 'public_ip' in results['ip_leak']:
            print(f"   Public IP: {results['ip_leak']['public_ip']}")
            print(f"   Tor Exit: {'✅ Yes' if results['ip_leak'].get('is_tor_exit') else '❌ No'}")
            print(f"   Leak: {'❌ DETECTED' if results['ip_leak'].get('leak_detected') else '✅ None'}\n")

        # Test 4: Tor circuit (if enabled)
        if self.services['tor'].is_running():
            print("Test 4: Tor circuit status...")
            results['tor_circuit'] = self.services['tor'].get_circuit_info()
            print(f"   Circuits: {results['tor_circuit'].get('num_circuits', 0)}\n")

        # Test 5: I2P status (if enabled)
        if self.services['i2p'].is_running():
            print("Test 5: I2P network status...")
            results['i2p_status'] = self.services['i2p'].get_network_status()
            print(f"   Integrated: {'✅ Yes' if results['i2p_status'].get('integrated') else '❌ No'}\n")

        print("="*60 + "\n")
        return results

    def _test_internet(self) -> bool:
        """Test basic internet connectivity"""
        try:
            result = subprocess.run(
                ['curl', '-s', '--max-time', '10', 'https://check.torproject.org'],
                capture_output=True,
                timeout=15
            )
            return result.returncode == 0
        except:
            return False

    def _test_dns(self) -> Dict:
        """Test DNS resolution"""
        if self.services['dnscrypt'].is_running():
            return self.services['dnscrypt'].test_dns_resolution('example.com')
        else:
            # Try system DNS
            try:
                import socket
                ip = socket.gethostbyname('example.com')
                return {
                    'success': True,
                    'ip_address': ip,
                    'encrypted': False
                }
            except:
                return {
                    'success': False,
                    'error': 'DNS resolution failed'
                }

    def _test_ip_leak(self) -> Dict:
        """Test for IP leaks"""
        try:
            # Get public IP
            result = subprocess.run(
                ['curl', '-s', '--max-time', '10', 'https://icanhazip.com'],
                capture_output=True,
                timeout=15
            )

            if result.returncode != 0:
                return {'error': 'Could not determine public IP'}

            public_ip = result.stdout.decode().strip()

            # Check if IP is Tor exit node (if Tor enabled)
            is_tor_exit = False
            if self.services['tor'].is_running():
                is_tor_exit = self.services['tor'].check_exit_ip(public_ip)

            # Detect leak: if we're using Tor but IP is not a Tor exit
            leak_detected = False
            if self.current_mode != NetworkMode.DIRECT:
                if self.services['tor'].is_running() and not is_tor_exit:
                    leak_detected = True

            return {
                'public_ip': public_ip,
                'is_tor_exit': is_tor_exit,
                'leak_detected': leak_detected
            }

        except Exception as e:
            return {'error': str(e)}

    def _load_mode_config(self, mode: NetworkMode) -> Dict:
        """
        Load configuration for a specific mode

        Args:
            mode: NetworkMode to load config for

        Returns:
            Dict with mode configuration
        """
        config_file = self.config_dir / "modes" / f"{mode.value}.json"

        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Return default config
            return self._get_default_mode_config(mode)

    def _get_default_mode_config(self, mode: NetworkMode) -> Dict:
        """Get default configuration for a mode"""

        default_configs = {
            NetworkMode.DIRECT: {},

            NetworkMode.TOR_ONLY: {
                'tor': {
                    'use_bridges': False,
                    'circuit_timeout': 60
                }
            },

            NetworkMode.TOR_DNSCRYPT: {
                'tor': {
                    'use_bridges': False
                },
                'dnscrypt': {
                    'server_names': ['cloudflare', 'google'],
                    'require_dnssec': True
                }
            },

            NetworkMode.TOR_I2P_PARALLEL: {
                'tor': {'use_bridges': False},
                'i2p': {'tunnel_length': 3},
                'dnscrypt': {'require_dnssec': True}
            },

            NetworkMode.I2P_ONLY: {
                'i2p': {'tunnel_length': 3}
            },

            NetworkMode.MAXIMUM_ANONYMITY: {
                'tor': {
                    'use_bridges': True,
                    'bridge_type': 'obfs4'
                },
                'i2p': {
                    'tunnel_length': 4,
                    'chain_through_tor': True  # CRITICAL FIX: Enable I2P→Tor chaining
                },
                'dnscrypt': {'require_dnssec': True}
            }
        }

        return default_configs.get(mode, {})

    def _apply_routing_rules(self, mode: NetworkMode, config: Dict):
        """
        Apply iptables/nftables routing rules for the mode

        TODO: Implement actual firewall rules
        """
        print("   Routing rules applied (placeholder)")
        # This would call:
        # subprocess.run(['nft', '-f', f'/opt/qwamos/network/firewall/rules/{mode.value}.nft'])


def main():
    """Main entry point for network manager"""
    import argparse

    parser = argparse.ArgumentParser(description='QWAMOS Network Manager')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'switch', 'test'],
                       help='Command to execute')
    parser.add_argument('--mode', type=str, choices=[m.value for m in NetworkMode],
                       help='Network mode (for switch command)')
    parser.add_argument('--config-dir', type=str, default='/opt/qwamos/network',
                       help='Network configuration directory')

    args = parser.parse_args()

    nm = NetworkManager(args.config_dir)

    if args.command == 'status':
        status = nm.get_status()
        print(json.dumps(status, indent=2))

    elif args.command == 'switch':
        if not args.mode:
            print("Error: --mode required for switch command")
            return 1
        mode = NetworkMode(args.mode)
        nm.switch_mode(mode)

    elif args.command == 'test':
        results = nm.test_connectivity()
        print("\nTest Results:")
        print(json.dumps(results, indent=2))

    elif args.command == 'stop':
        print("Stopping all services...")
        nm.stop_all_services()
        print("✅ All services stopped")

    return 0


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         QWAMOS Network Manager (Phase 5)                 ║
    ║         Network Isolation & Anonymization                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    exit(main())
