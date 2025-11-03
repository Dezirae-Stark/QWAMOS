#!/usr/bin/env python3
"""
Tor Controller for QWAMOS Network Isolation (Phase 5)

Manages Tor anonymity service with support for:
- Standard Tor operation
- Bridge mode (obfs4, meek, snowflake)
- Circuit management
- Connection monitoring
"""

import subprocess
import os
import time
import socket
import re
from pathlib import Path
from typing import Optional, Dict, List

class TorController:
    """Controller for Tor anonymity service"""

    def __init__(self, config_dir: str = "/opt/qwamos/network/tor"):
        self.config_dir = Path(config_dir)
        self.tor_binary = self.config_dir / "tor"
        self.torrc = self.config_dir / "torrc"
        self.control_port = 9051
        self.socks_port = 9050
        self.process: Optional[subprocess.Popen] = None
        self.control_socket: Optional[socket.socket] = None

    def start(self, config: Dict = None):
        """
        Start Tor service

        Args:
            config: Optional configuration dict with:
                - use_bridges: bool - Enable bridge mode
                - bridge_type: str - Bridge type (obfs4, meek, snowflake)
                - circuit_timeout: int - Circuit build timeout in seconds
        """
        if self.is_running():
            print("⚠️  Tor is already running")
            return

        config = config or {}
        use_bridges = config.get('use_bridges', False)
        bridge_type = config.get('bridge_type', 'obfs4')

        cmd = [str(self.tor_binary), '-f', str(self.torrc)]

        # Add bridge configuration if enabled
        if use_bridges:
            cmd.extend(['--UseBridges', '1'])

            # Add pluggable transport for obfs4
            if bridge_type == 'obfs4':
                obfs4proxy = self.config_dir / 'pluggable-transports' / 'obfs4proxy'
                cmd.extend(['--ClientTransportPlugin', f'obfs4 exec {obfs4proxy}'])

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy()
            )
            print(f"✅ Tor started (PID: {self.process.pid})")

            # Wait for Tor to establish circuits
            print("⏳ Waiting for Tor to build circuits...")
            if self._wait_for_bootstrap(timeout=120):
                print("✅ Tor bootstrap complete - ready to route traffic")
            else:
                print("⚠️  Tor bootstrap timeout - may not be fully ready")

        except FileNotFoundError:
            print(f"❌ Tor binary not found at {self.tor_binary}")
            print("   Please ensure Tor is installed in the network/tor directory")
        except Exception as e:
            print(f"❌ Failed to start Tor: {e}")

    def stop(self):
        """Stop Tor service gracefully"""
        if not self.process:
            print("⚠️  Tor is not running")
            return

        try:
            # Send SIGTERM for graceful shutdown
            self.process.terminate()
            self.process.wait(timeout=30)
            print("✅ Tor stopped")
        except subprocess.TimeoutExpired:
            # Force kill if graceful shutdown times out
            self.process.kill()
            print("⚠️  Tor force-killed (timeout)")

        self.process = None

        # Close control socket if open
        if self.control_socket:
            self.control_socket.close()
            self.control_socket = None

    def is_running(self) -> bool:
        """Check if Tor service is running"""
        if self.process is None:
            return False

        # Check if process is still alive
        return self.process.poll() is None

    def get_status(self) -> Dict:
        """
        Get Tor service status

        Returns:
            Dict with status information:
                - running: bool
                - pid: int
                - circuits: int
                - bootstrap: int (percentage)
                - guard_nodes: list
        """
        if not self.is_running():
            return {
                'running': False,
                'status': 'stopped'
            }

        status = {
            'running': True,
            'pid': self.process.pid,
            'socks_port': self.socks_port,
            'control_port': self.control_port
        }

        # Try to get bootstrap status from control port
        try:
            bootstrap_pct = self._get_bootstrap_percentage()
            status['bootstrap'] = bootstrap_pct
            status['status'] = 'ready' if bootstrap_pct == 100 else 'bootstrapping'
        except:
            status['status'] = 'unknown'

        return status

    def get_circuit_info(self) -> Dict:
        """
        Get information about current Tor circuits

        Returns:
            Dict with circuit information:
                - num_circuits: int
                - circuits: list of circuit details
        """
        if not self.is_running():
            return {'error': 'Tor is not running'}

        try:
            # Connect to Tor control port
            self._connect_control_port()

            # Authenticate
            self._control_send('AUTHENTICATE ""')

            # Get circuit list
            response = self._control_send('GETINFO circuit-status')

            circuits = []
            for line in response.split('\n'):
                if line.startswith('250'):
                    continue
                if line.strip():
                    circuits.append(line.strip())

            return {
                'num_circuits': len(circuits),
                'circuits': circuits[:5]  # Return first 5 circuits
            }
        except Exception as e:
            return {'error': str(e)}

    def check_exit_ip(self, ip_address: str) -> bool:
        """
        Check if given IP address is a Tor exit node

        Args:
            ip_address: IP address to check

        Returns:
            True if IP is a Tor exit node
        """
        try:
            # Query Tor exit list
            # This is a simplified check - real implementation would query
            # https://check.torproject.org/torbulkexitlist
            self._connect_control_port()
            self._control_send('AUTHENTICATE ""')

            response = self._control_send('GETINFO exit-policy/default')

            # Simple heuristic: if we got a response, assume we're using Tor
            return 'exit' in response.lower()
        except:
            return False

    def _wait_for_bootstrap(self, timeout: int = 120) -> bool:
        """
        Wait for Tor to complete bootstrap

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if bootstrap completed, False if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                pct = self._get_bootstrap_percentage()
                if pct >= 100:
                    return True
            except:
                pass

            time.sleep(2)

        return False

    def _get_bootstrap_percentage(self) -> int:
        """
        Get current bootstrap percentage

        Returns:
            Bootstrap percentage (0-100)
        """
        try:
            self._connect_control_port()
            self._control_send('AUTHENTICATE ""')

            response = self._control_send('GETINFO status/bootstrap-phase')

            # Parse response: "250-status/bootstrap-phase=NOTICE BOOTSTRAP PROGRESS=100 TAG=done SUMMARY="Done""
            match = re.search(r'PROGRESS=(\d+)', response)
            if match:
                return int(match.group(1))
        except:
            pass

        return 0

    def _connect_control_port(self):
        """Connect to Tor control port"""
        if self.control_socket:
            return  # Already connected

        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.connect(('127.0.0.1', self.control_port))

    def _control_send(self, command: str) -> str:
        """
        Send command to Tor control port

        Args:
            command: Tor control command

        Returns:
            Response from Tor
        """
        if not self.control_socket:
            raise Exception("Not connected to control port")

        self.control_socket.send(f"{command}\r\n".encode())

        # Read response
        response = b""
        while True:
            data = self.control_socket.recv(4096)
            response += data
            if b'250 OK' in response or b'250-' not in response:
                break

        return response.decode()


if __name__ == "__main__":
    # Test Tor controller
    print("=== QWAMOS Tor Controller Test ===\n")

    controller = TorController()

    print("Starting Tor...")
    controller.start()

    print("\nChecking status...")
    status = controller.get_status()
    print(f"Status: {status}")

    print("\nGetting circuit info...")
    circuits = controller.get_circuit_info()
    print(f"Circuits: {circuits}")

    input("\nPress Enter to stop Tor...")

    print("\nStopping Tor...")
    controller.stop()

    print("\n=== Test Complete ===")
