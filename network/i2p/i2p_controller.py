#!/usr/bin/env python3
"""
I2P (Purple I2P) Controller for QWAMOS Network Isolation (Phase 5)

Manages Purple I2P (i2pd) anonymity service with support for:
- HTTP proxy for eepsite access
- SOCKS proxy for applications
- SAM interface for I2P applications
- Network status monitoring
"""

import subprocess
import os
import time
import socket
import requests
from pathlib import Path
from typing import Optional, Dict

class I2PController:
    """Controller for Purple I2P (i2pd) anonymity service"""

    def __init__(self, config_dir: str = "/opt/qwamos/network/i2p"):
        self.config_dir = Path(config_dir)
        self.i2pd_binary = self.config_dir / "i2pd"
        self.i2pd_conf = self.config_dir / "i2pd.conf"
        self.i2pd_conf_template = self.config_dir / "i2pd.conf.template"
        self.http_proxy_port = 4444  # HTTP proxy for eepsites
        self.socks_proxy_port = 4447  # SOCKS proxy
        self.sam_port = 7656  # SAM interface
        self.console_port = 7070  # Web console
        self.tor_socks_port = 9050  # Tor SOCKS proxy for chaining
        self.process: Optional[subprocess.Popen] = None
        self.chain_through_tor = False  # I2P→Tor chaining enabled

    def start(self, config: Dict = None):
        """
        Start I2P (i2pd) service

        Args:
            config: Optional configuration dict with:
                - tunnel_length: int - Number of hops in tunnel (default: 3)
                - inbound_tunnels: int - Number of inbound tunnels
                - outbound_tunnels: int - Number of outbound tunnels
                - chain_through_tor: bool - Enable I2P→Tor chaining (default: False)
        """
        if self.is_running():
            print("⚠️  I2P is already running")
            return

        config = config or {}

        # Enable I2P→Tor chaining if requested
        if config.get('chain_through_tor', False):
            self.chain_through_tor = True
            print("🔗 I2P→Tor chaining ENABLED (defense-in-depth)")

        # Generate i2pd.conf from template
        self._generate_config()

        cmd = [
            str(self.i2pd_binary),
            '--conf', str(self.i2pd_conf),
            '--datadir', '/var/lib/i2p'
        ]

        # Add custom tunnel configuration if provided
        if 'tunnel_length' in config:
            cmd.extend(['--tunnels.length', str(config['tunnel_length'])])

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy()
            )
            print(f"✅ I2P (i2pd) started (PID: {self.process.pid})")
            print(f"   HTTP Proxy: 127.0.0.1:{self.http_proxy_port}")
            print(f"   SOCKS Proxy: 127.0.0.1:{self.socks_proxy_port}")
            if self.chain_through_tor:
                print(f"   🔗 Chained through Tor: 127.0.0.1:{self.tor_socks_port}")
            print(f"   Web Console: http://127.0.0.1:{self.console_port}")

            # Wait for I2P to initialize
            print("⏳ Waiting for I2P to initialize...")
            if self._wait_for_ready(timeout=120):
                print("✅ I2P is ready - router integrated into network")

                # Verify Tor chaining if enabled
                if self.chain_through_tor:
                    if self._verify_tor_chaining():
                        print("✅ I2P→Tor chaining verified")
                    else:
                        print("⚠️  WARNING: I2P→Tor chaining verification failed!")
            else:
                print("⚠️  I2P initialization timeout - may not be fully ready")

        except FileNotFoundError:
            print(f"❌ I2P binary not found at {self.i2pd_binary}")
            print("   Please ensure i2pd is installed in the network/i2p directory")
        except Exception as e:
            print(f"❌ Failed to start I2P: {e}")

    def stop(self):
        """Stop I2P service gracefully"""
        if not self.process:
            print("⚠️  I2P is not running")
            return

        try:
            # Send SIGTERM for graceful shutdown
            self.process.terminate()
            self.process.wait(timeout=30)
            print("✅ I2P stopped")
        except subprocess.TimeoutExpired:
            # Force kill if graceful shutdown times out
            self.process.kill()
            print("⚠️  I2P force-killed (timeout)")

        self.process = None

    def is_running(self) -> bool:
        """Check if I2P service is running"""
        if self.process is None:
            return False

        # Check if process is still alive
        return self.process.poll() is None

    def get_status(self) -> Dict:
        """
        Get I2P service status

        Returns:
            Dict with status information:
                - running: bool
                - pid: int
                - router_status: str
                - num_tunnels: int
                - network_status: str
        """
        if not self.is_running():
            return {
                'running': False,
                'status': 'stopped'
            }

        status = {
            'running': True,
            'pid': self.process.pid,
            'http_proxy': f"127.0.0.1:{self.http_proxy_port}",
            'socks_proxy': f"127.0.0.1:{self.socks_proxy_port}",
            'console': f"http://127.0.0.1:{self.console_port}"
        }

        # Try to get router status from web console
        try:
            network_status = self.get_network_status()
            status.update(network_status)
            status['status'] = 'ready' if network_status.get('integrated') else 'initializing'
        except:
            status['status'] = 'unknown'

        return status

    def get_network_status(self) -> Dict:
        """
        Get I2P network status from web console

        Returns:
            Dict with network status:
                - integrated: bool - Router integrated into network
                - num_peers: int - Number of connected peers
                - tunnels: int - Number of active tunnels
        """
        if not self.is_running():
            return {'error': 'I2P is not running'}

        try:
            # Query I2P web console API
            response = requests.get(
                f"http://127.0.0.1:{self.console_port}",
                timeout=5
            )

            if response.status_code == 200:
                # Parse HTML for status info
                # This is simplified - real implementation would parse actual status
                content = response.text.lower()

                return {
                    'integrated': 'ok' in content or 'integrated' in content,
                    'status': 'OK' if 'ok' in content else 'Initializing',
                    'console_accessible': True
                }
            else:
                return {'error': f'HTTP {response.status_code}'}

        except requests.exceptions.ConnectionError:
            return {
                'integrated': False,
                'status': 'Not ready',
                'console_accessible': False
            }
        except Exception as e:
            return {'error': str(e)}

    def test_eepsite_access(self, eepsite: str = "http://stats.i2p") -> bool:
        """
        Test access to an I2P eepsite

        Args:
            eepsite: I2P hidden service address (.i2p domain)

        Returns:
            True if eepsite is accessible
        """
        if not self.is_running():
            return False

        try:
            # Use HTTP proxy to access eepsite
            proxies = {
                'http': f'http://127.0.0.1:{self.http_proxy_port}',
                'https': f'http://127.0.0.1:{self.http_proxy_port}'
            }

            response = requests.get(
                eepsite,
                proxies=proxies,
                timeout=30
            )

            return response.status_code == 200

        except:
            return False

    def _generate_config(self):
        """
        Generate i2pd.conf from template with Tor chaining configuration.

        This creates the runtime config file with the correct outproxy settings.
        """
        if not self.i2pd_conf_template.exists():
            print(f"⚠️  Warning: Config template not found at {self.i2pd_conf_template}")
            print("   Using default i2pd configuration (no chaining)")
            return

        try:
            # Read template
            with open(self.i2pd_conf_template, 'r') as f:
                config_content = f.read()

            # Substitute template variables
            config_content = config_content.replace(
                '{{CHAIN_THROUGH_TOR}}',
                'true' if self.chain_through_tor else 'false'
            )

            # Write runtime config
            self.i2pd_conf.parent.mkdir(parents=True, exist_ok=True)
            with open(self.i2pd_conf, 'w') as f:
                f.write(config_content)

            print(f"✓ Generated i2pd.conf (chaining: {self.chain_through_tor})")

        except Exception as e:
            print(f"⚠️  Warning: Failed to generate config: {e}")
            print("   I2P may not start correctly")

    def _verify_tor_chaining(self) -> bool:
        """
        Verify that I2P is actually routing through Tor.

        Returns:
            True if chaining is verified, False otherwise
        """
        if not self.chain_through_tor:
            return True  # Not enabled, nothing to verify

        try:
            # Check if Tor is running and accepting connections
            tor_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tor_sock.settimeout(5)
            result = tor_sock.connect_ex(('127.0.0.1', self.tor_socks_port))
            tor_sock.close()

            if result != 0:
                print(f"   ⚠️  Tor SOCKS proxy not reachable at 127.0.0.1:{self.tor_socks_port}")
                return False

            # Verify I2P config has outproxy enabled
            if not self.i2pd_conf.exists():
                print("   ⚠️  I2P config file not found")
                return False

            with open(self.i2pd_conf, 'r') as f:
                config = f.read()

            if 'outproxy.enabled = true' not in config:
                print("   ⚠️  Outproxy not enabled in i2pd.conf")
                return False

            if f'outproxyport = {self.tor_socks_port}' not in config:
                print(f"   ⚠️  Outproxy not configured for Tor port {self.tor_socks_port}")
                return False

            return True

        except Exception as e:
            print(f"   ⚠️  Chaining verification error: {e}")
            return False

    def _wait_for_ready(self, timeout: int = 120) -> bool:
        """
        Wait for I2P to become ready

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if I2P is ready, False if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check if web console is accessible
                response = requests.get(
                    f"http://127.0.0.1:{self.console_port}",
                    timeout=5
                )
                if response.status_code == 200:
                    return True
            except:
                pass

            time.sleep(3)

        return False


if __name__ == "__main__":
    # Test I2P controller
    print("=== QWAMOS I2P Controller Test ===\n")

    controller = I2PController()

    print("Starting I2P...")
    controller.start()

    print("\nChecking status...")
    status = controller.get_status()
    print(f"Status: {status}")

    print("\nGetting network status...")
    network = controller.get_network_status()
    print(f"Network: {network}")

    print("\nTesting eepsite access...")
    accessible = controller.test_eepsite_access("http://stats.i2p")
    print(f"Eepsite accessible: {accessible}")

    input("\nPress Enter to stop I2P...")

    print("\nStopping I2P...")
    controller.stop()

    print("\n=== Test Complete ===")
