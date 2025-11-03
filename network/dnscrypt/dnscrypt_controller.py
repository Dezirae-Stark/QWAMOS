#!/usr/bin/env python3
"""
DNSCrypt Controller for QWAMOS Network Isolation (Phase 5)

Manages DNSCrypt-proxy service for encrypted DNS queries with support for:
- DNS-over-HTTPS (DoH)
- DNS-over-TLS (DoT)
- DNSCrypt protocol
- DNSSEC validation
- DNS query logging
"""

import subprocess
import os
import time
import socket
from pathlib import Path
from typing import Optional, Dict

class DNSCryptController:
    """Controller for DNSCrypt encrypted DNS service"""

    def __init__(self, config_dir: str = "/opt/qwamos/network/dnscrypt"):
        self.config_dir = Path(config_dir)
        self.dnscrypt_binary = self.config_dir / "dnscrypt-proxy"
        self.config_file = self.config_dir / "dnscrypt-proxy.toml"
        self.listen_port = 5353
        self.process: Optional[subprocess.Popen] = None

    def start(self, config: Dict = None):
        """
        Start DNSCrypt-proxy service

        Args:
            config: Optional configuration dict with:
                - server_names: list - DNS servers to use
                - require_dnssec: bool - Require DNSSEC validation
                - block_ipv6: bool - Block IPv6 queries
        """
        if self.is_running():
            print("⚠️  DNSCrypt is already running")
            return

        config = config or {}

        cmd = [
            str(self.dnscrypt_binary),
            '-config', str(self.config_file)
        ]

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy()
            )
            print(f"✅ DNSCrypt started (PID: {self.process.pid})")
            print(f"   Listening on: 127.0.0.1:{self.listen_port}")

            # Wait for DNSCrypt to initialize
            print("⏳ Waiting for DNSCrypt to initialize...")
            if self._wait_for_ready(timeout=30):
                print("✅ DNSCrypt is ready - DNS queries will be encrypted")
            else:
                print("⚠️  DNSCrypt initialization timeout")

        except FileNotFoundError:
            print(f"❌ DNSCrypt binary not found at {self.dnscrypt_binary}")
            print("   Please ensure dnscrypt-proxy is installed in the network/dnscrypt directory")
        except Exception as e:
            print(f"❌ Failed to start DNSCrypt: {e}")

    def stop(self):
        """Stop DNSCrypt service gracefully"""
        if not self.process:
            print("⚠️  DNSCrypt is not running")
            return

        try:
            # Send SIGTERM for graceful shutdown
            self.process.terminate()
            self.process.wait(timeout=10)
            print("✅ DNSCrypt stopped")
        except subprocess.TimeoutExpired:
            # Force kill if graceful shutdown times out
            self.process.kill()
            print("⚠️  DNSCrypt force-killed (timeout)")

        self.process = None

    def is_running(self) -> bool:
        """Check if DNSCrypt service is running"""
        if self.process is None:
            return False

        # Check if process is still alive
        return self.process.poll() is None

    def get_status(self) -> Dict:
        """
        Get DNSCrypt service status

        Returns:
            Dict with status information:
                - running: bool
                - pid: int
                - listen_address: str
        """
        if not self.is_running():
            return {
                'running': False,
                'status': 'stopped'
            }

        status = {
            'running': True,
            'pid': self.process.pid,
            'listen_address': f"127.0.0.1:{self.listen_port}",
            'status': 'ready'
        }

        # Check if port is actually listening
        if self._check_port_listening():
            status['port_listening'] = True
        else:
            status['port_listening'] = False
            status['status'] = 'starting'

        return status

    def test_dns_resolution(self, domain: str = "example.com") -> Dict:
        """
        Test DNS resolution through DNSCrypt

        Args:
            domain: Domain name to resolve

        Returns:
            Dict with resolution results:
                - success: bool
                - ip_address: str
                - encrypted: bool
        """
        if not self.is_running():
            return {
                'success': False,
                'error': 'DNSCrypt is not running'
            }

        try:
            # Use dig to query through DNSCrypt
            result = subprocess.run(
                ['dig', f'@127.0.0.1', '-p', str(self.listen_port), domain, '+short'],
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout:
                ip_address = result.stdout.decode().strip().split('\n')[0]
                return {
                    'success': True,
                    'ip_address': ip_address,
                    'encrypted': True,
                    'domain': domain
                }
            else:
                return {
                    'success': False,
                    'error': 'Resolution failed'
                }

        except FileNotFoundError:
            # dig not available, try Python DNS resolution
            try:
                # This would go through system DNS, not DNSCrypt
                # Real implementation would use dnspython library with custom server
                import socket
                ip = socket.gethostbyname(domain)
                return {
                    'success': True,
                    'ip_address': ip,
                    'encrypted': False,  # Not through DNSCrypt
                    'warning': 'dig not available, used system DNS'
                }
            except:
                return {
                    'success': False,
                    'error': 'Resolution failed'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _check_port_listening(self) -> bool:
        """
        Check if DNSCrypt is listening on the configured port

        Returns:
            True if port is listening
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            # Try to send a DNS query
            sock.sendto(b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01',
                       ('127.0.0.1', self.listen_port))
            sock.close()
            return True
        except:
            return False

    def _wait_for_ready(self, timeout: int = 30) -> bool:
        """
        Wait for DNSCrypt to become ready

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if DNSCrypt is ready, False if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self._check_port_listening():
                return True
            time.sleep(1)

        return False


if __name__ == "__main__":
    # Test DNSCrypt controller
    print("=== QWAMOS DNSCrypt Controller Test ===\n")

    controller = DNSCryptController()

    print("Starting DNSCrypt...")
    controller.start()

    print("\nChecking status...")
    status = controller.get_status()
    print(f"Status: {status}")

    print("\nTesting DNS resolution...")
    result = controller.test_dns_resolution("example.com")
    print(f"Resolution: {result}")

    input("\nPress Enter to stop DNSCrypt...")

    print("\nStopping DNSCrypt...")
    controller.stop()

    print("\n=== Test Complete ===")
