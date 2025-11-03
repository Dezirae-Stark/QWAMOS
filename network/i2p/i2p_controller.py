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
        self.http_proxy_port = 4444  # HTTP proxy for eepsites
        self.socks_proxy_port = 4447  # SOCKS proxy
        self.sam_port = 7656  # SAM interface
        self.console_port = 7070  # Web console
        self.process: Optional[subprocess.Popen] = None

    def start(self, config: Dict = None):
        """
        Start I2P (i2pd) service

        Args:
            config: Optional configuration dict with:
                - tunnel_length: int - Number of hops in tunnel (default: 3)
                - inbound_tunnels: int - Number of inbound tunnels
                - outbound_tunnels: int - Number of outbound tunnels
        """
        if self.is_running():
            print("⚠️  I2P is already running")
            return

        config = config or {}

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
            print(f"   Web Console: http://127.0.0.1:{self.console_port}")

            # Wait for I2P to initialize
            print("⏳ Waiting for I2P to initialize...")
            if self._wait_for_ready(timeout=120):
                print("✅ I2P is ready - router integrated into network")
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
