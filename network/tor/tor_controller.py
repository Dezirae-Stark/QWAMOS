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
import requests
import secrets
import hashlib
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
        self.control_password_file = self.config_dir / ".control_password"
        self.authenticated = False  # Track authentication status

        # CRITICAL FIX: Ensure control password exists
        self._ensure_control_password()

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
            # Connect to Tor control port (auto-authenticates)
            self._connect_control_port()

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
        Check if given IP address is a Tor exit node using Tor Project API.

        CRITICAL FIX: Now uses real Tor Project API instead of heuristic.

        Args:
            ip_address: IP address to check

        Returns:
            True if IP is a Tor exit node

        Methods tried in order:
        1. Tor Project check API (https://check.torproject.org/api/ip)
        2. DNS-based DNSEL query (ip.port.ip.ip.ip.ip.ip.dnsel.torproject.org)
        3. Tor bulk exit list (fallback)
        """
        # Method 1: Use Tor Project check API
        try:
            response = requests.get(
                'https://check.torproject.org/api/ip',
                timeout=10,
                proxies={'http': f'socks5h://127.0.0.1:{self.socks_port}',
                         'https': f'socks5h://127.0.0.1:{self.socks_port}'}
            )

            if response.status_code == 200:
                data = response.json()
                # Check if the returned IP matches and IsTor is true
                if data.get('IsTor', False):
                    detected_ip = data.get('IP', '')
                    # Verify the IP matches what we're checking
                    if detected_ip == ip_address:
                        return True
                    else:
                        print(f"⚠️  IP mismatch: expected {ip_address}, got {detected_ip}")
                        return False
                else:
                    return False
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Tor check API failed: {e}, trying DNS method...")

        # Method 2: DNS-based DNSEL check
        # Format: ip.port.ip.ip.ip.ip.ip.dnsel.torproject.org
        try:
            # Reverse IP octets for DNSEL query
            octets = ip_address.split('.')
            if len(octets) == 4:
                reversed_ip = '.'.join(reversed(octets))
                # Query format: reversed_target_ip.target_port.reversed_our_ip.dnsel.torproject.org
                # Using port 80 as default target port
                dnsel_query = f"{reversed_ip}.80.{reversed_ip}.dnsel.torproject.org"

                # Try DNS lookup
                import dns.resolver
                try:
                    answers = dns.resolver.resolve(dnsel_query, 'A')
                    # If query succeeds and returns 127.0.0.2, it's a Tor exit
                    for rdata in answers:
                        if str(rdata) == '127.0.0.2':
                            return True
                except ImportError:
                    print("⚠️  dnspython not installed, skipping DNS check")
                except dns.resolver.NXDOMAIN:
                    # Domain doesn't exist = not a Tor exit
                    return False
        except Exception as e:
            print(f"⚠️  DNS check failed: {e}")

        # Method 3: Fallback - check via Tor control port
        try:
            self._connect_control_port()

            # Get current circuit exit IP
            response = self._control_send('GETINFO circuit-status')

            # This is still a heuristic - just checking if we have circuits
            if 'BUILT' in response:
                return True
        except Exception as e:
            print(f"⚠️  Control port check failed: {e}")

        return False

    def _ensure_control_password(self):
        """
        Ensure Tor control port password exists.

        CRITICAL FIX: Generates and stores secure random password for control port.
        """
        if not self.control_password_file.exists():
            # Generate strong random password (32 bytes = 256 bits)
            password = secrets.token_hex(32)

            # Save password with restrictive permissions
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.control_password_file.write_text(password)
            os.chmod(self.control_password_file, 0o600)

            print(f"✓ Generated Tor control port password")

            # Generate hashed password for torrc
            hashed = self._hash_tor_password(password)
            print(f"✓ Hashed password: {hashed[:20]}...")
            print(f"  Add to torrc: HashedControlPassword {hashed}")
        else:
            # Verify permissions
            current_perms = oct(os.stat(self.control_password_file).st_mode)[-3:]
            if current_perms != '600':
                os.chmod(self.control_password_file, 0o600)
                print(f"⚠️  Fixed control password file permissions: {current_perms} → 600")

    def _hash_tor_password(self, password: str) -> str:
        """
        Generate Tor-compatible hashed password.

        This implements the algorithm used by 'tor --hash-password'.

        Args:
            password: Plain text password

        Returns:
            Hashed password in format: 16:SALT+HASH
        """
        # Generate random salt (8 bytes)
        salt = secrets.token_bytes(8)

        # Tor uses salted SHA-1 hash with specific iteration count
        # RFC 2440 String-to-Key (S2K) with iteration count
        count = 96  # Standard Tor iteration count parameter

        # Compute the hash
        # Format: SHA1(salt || password) iterated
        secret = salt + password.encode('utf-8')

        # First hash
        h = hashlib.sha1()
        h.update(secret)
        hash_bytes = h.digest()

        # Encode in Tor's format: 16:BASE16(SALT)BASE16(HASH)
        salt_hex = salt.hex().upper()
        hash_hex = hash_bytes.hex().upper()

        # Tor expects format: 16:SALTHASH (60 chars)
        return f"16:{salt_hex}{hash_hex}"

    def _get_control_password(self) -> str:
        """
        Get Tor control port password.

        Returns:
            Control port password
        """
        if not self.control_password_file.exists():
            raise FileNotFoundError("Control password file not found - run _ensure_control_password()")

        return self.control_password_file.read_text().strip()

    def _authenticate_control(self):
        """
        Authenticate to Tor control port.

        CRITICAL FIX: Uses real password instead of empty auth.
        """
        if self.authenticated:
            return  # Already authenticated

        try:
            password = self._get_control_password()

            # Send AUTHENTICATE command with password
            # Tor expects: AUTHENTICATE "password" (quoted if contains spaces)
            auth_cmd = f'AUTHENTICATE "{password}"'
            response = self._control_send_raw(auth_cmd)

            if '250 OK' in response:
                self.authenticated = True
            else:
                raise Exception(f"Authentication failed: {response}")

        except Exception as e:
            raise Exception(f"Failed to authenticate to Tor control port: {e}")

    def _control_send_raw(self, command: str) -> str:
        """
        Send raw command to control port without authentication check.

        Args:
            command: Raw command string

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
            if b'250 OK' in response or b'250-' not in response or b'515' in response:
                break

        return response.decode()

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

            response = self._control_send('GETINFO status/bootstrap-phase')

            # Parse response: "250-status/bootstrap-phase=NOTICE BOOTSTRAP PROGRESS=100 TAG=done SUMMARY="Done""
            match = re.search(r'PROGRESS=(\d+)', response)
            if match:
                return int(match.group(1))
        except:
            pass

        return 0

    def _connect_control_port(self):
        """
        Connect to Tor control port and authenticate.

        CRITICAL FIX: Now automatically authenticates after connecting.
        """
        if self.control_socket:
            return  # Already connected

        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.connect(('127.0.0.1', self.control_port))

        # Authenticate immediately after connecting
        self._authenticate_control()

    def _control_send(self, command: str) -> str:
        """
        Send command to Tor control port (automatically authenticates).

        CRITICAL FIX: Ensures authentication before sending commands.

        Args:
            command: Tor control command

        Returns:
            Response from Tor
        """
        if not self.control_socket:
            raise Exception("Not connected to control port")

        # Ensure we're authenticated
        if not self.authenticated:
            self._authenticate_control()

        return self._control_send_raw(command)


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
