#!/usr/bin/env python3
"""
QWAMOS Network Status Monitoring Daemon

Continuously monitors network isolation services and detects issues:
- Tor/I2P/DNSCrypt service health
- Periodic IP leak testing
- Firewall rule integrity
- Kill switch activation on failure
- Network status logging and alerts

This daemon runs as a systemd service and provides real-time monitoring
of QWAMOS network isolation infrastructure.
"""

import subprocess
import time
import json
import logging
import sys
import signal
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

# Configuration
CONFIG_DIR = Path("/opt/qwamos/network")
LOG_FILE = Path("/var/log/qwamos/network-monitor.log")
STATE_FILE = Path("/var/lib/qwamos/network-monitor-state.json")
LEAK_TEST_SCRIPT = Path(__file__).parent.parent / "tests" / "test_ip_leak.py"

# Monitoring intervals (seconds)
SERVICE_CHECK_INTERVAL = 30      # Check service status every 30s
LEAK_TEST_INTERVAL = 600         # Run leak tests every 10 minutes
CONNECTIVITY_CHECK_INTERVAL = 60  # Check connectivity every 1 minute
FIREWALL_CHECK_INTERVAL = 120    # Check firewall rules every 2 minutes

# Service definitions
SERVICES = {
    'tor': 'qwamos-tor.service',
    'i2p': 'qwamos-i2p.service',
    'dnscrypt': 'qwamos-dnscrypt.service',
    'network_manager': 'qwamos-network-manager.service'
}

class ServiceStatus(Enum):
    """Service status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    UNKNOWN = "unknown"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class NetworkMonitor:
    """Network monitoring daemon"""

    def __init__(self):
        """Initialize network monitor"""
        self.running = False
        self.state = {
            'start_time': time.time(),
            'last_leak_test': 0,
            'last_connectivity_check': 0,
            'last_firewall_check': 0,
            'service_status': {},
            'alerts': [],
            'leak_test_results': None,
            'killswitch_active': False
        }

        # Setup logging
        self._setup_logging()

        # Load previous state if exists
        self._load_state()

        # CRITICAL SECURITY: Pre-load kill switch rules at startup
        # This eliminates race condition during activation
        self._load_killswitch_rules()

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _setup_logging(self):
        """Configure logging"""
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_state(self):
        """Load previous monitoring state"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    saved_state = json.load(f)
                    self.state.update(saved_state)
                self.logger.info("Loaded previous monitoring state")
            except Exception as e:
                self.logger.warning(f"Could not load previous state: {e}")

    def _save_state(self):
        """Save current monitoring state"""
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Could not save state: {e}")

    def _handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def start(self):
        """Start monitoring daemon"""
        self.logger.info("="*60)
        self.logger.info("QWAMOS Network Monitor Starting")
        self.logger.info("="*60)

        self.running = True

        # Initial checks
        self.logger.info("Running initial system checks...")
        self._check_all_services()
        self._check_connectivity()
        self._check_firewall_rules()

        self.logger.info("Monitoring daemon active")
        self.logger.info(f"Service check interval: {SERVICE_CHECK_INTERVAL}s")
        self.logger.info(f"Leak test interval: {LEAK_TEST_INTERVAL}s")
        self.logger.info(f"Connectivity check interval: {CONNECTIVITY_CHECK_INTERVAL}s")
        self.logger.info("")

        # Main monitoring loop
        while self.running:
            try:
                current_time = time.time()

                # Check services every interval
                if current_time % SERVICE_CHECK_INTERVAL < 1:
                    self._check_all_services()

                # Run leak tests periodically
                if current_time - self.state['last_leak_test'] >= LEAK_TEST_INTERVAL:
                    self._run_leak_test()
                    self.state['last_leak_test'] = current_time

                # Check connectivity
                if current_time - self.state['last_connectivity_check'] >= CONNECTIVITY_CHECK_INTERVAL:
                    self._check_connectivity()
                    self.state['last_connectivity_check'] = current_time

                # Check firewall rules
                if current_time - self.state['last_firewall_check'] >= FIREWALL_CHECK_INTERVAL:
                    self._check_firewall_rules()
                    self.state['last_firewall_check'] = current_time

                # Save state periodically
                self._save_state()

                # Sleep for 1 second
                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

        # Cleanup on shutdown
        self.logger.info("Network monitor shutting down")
        self._save_state()

    def _check_all_services(self):
        """Check status of all network services"""
        for service_name, systemd_unit in SERVICES.items():
            status = self._check_service_status(systemd_unit)

            previous_status = self.state['service_status'].get(service_name)
            self.state['service_status'][service_name] = status.value

            # Alert on status changes
            if previous_status and previous_status != status.value:
                if status == ServiceStatus.FAILED:
                    self._alert(
                        AlertLevel.CRITICAL,
                        f"Service {service_name} has FAILED"
                    )
                    self._activate_killswitch()
                elif status == ServiceStatus.INACTIVE:
                    self._alert(
                        AlertLevel.WARNING,
                        f"Service {service_name} is INACTIVE"
                    )
                elif status == ServiceStatus.ACTIVE and previous_status == ServiceStatus.FAILED.value:
                    self._alert(
                        AlertLevel.INFO,
                        f"Service {service_name} has RECOVERED"
                    )

    def _check_service_status(self, unit: str) -> ServiceStatus:
        """Check systemd service status"""
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', unit],
                capture_output=True,
                timeout=5
            )

            output = result.stdout.decode().strip()

            if output == 'active':
                return ServiceStatus.ACTIVE
            elif output == 'inactive':
                return ServiceStatus.INACTIVE
            elif output == 'failed':
                return ServiceStatus.FAILED
            else:
                return ServiceStatus.UNKNOWN

        except Exception as e:
            self.logger.error(f"Error checking service {unit}: {e}")
            return ServiceStatus.UNKNOWN

    def _run_leak_test(self):
        """Run IP leak detection tests"""
        self.logger.info("Running IP leak detection tests...")

        if not LEAK_TEST_SCRIPT.exists():
            self.logger.warning(f"Leak test script not found: {LEAK_TEST_SCRIPT}")
            return

        try:
            result = subprocess.run(
                ['python3', str(LEAK_TEST_SCRIPT)],
                capture_output=True,
                timeout=120
            )

            # Parse results
            try:
                with open('/tmp/qwamos_leak_test_results.json', 'r') as f:
                    test_results = json.load(f)
                    self.state['leak_test_results'] = test_results

                    # Check for leaks
                    if test_results.get('leaks_detected'):
                        self._alert(
                            AlertLevel.CRITICAL,
                            f"IP LEAKS DETECTED: {len(test_results['leaks_detected'])} leaks"
                        )
                        for leak in test_results['leaks_detected']:
                            self.logger.error(f"  LEAK: {leak}")
                    else:
                        self.logger.info("✅ Leak test passed - no leaks detected")

            except Exception as e:
                self.logger.error(f"Could not parse leak test results: {e}")

        except subprocess.TimeoutExpired:
            self.logger.error("Leak test timed out")
            self._alert(AlertLevel.WARNING, "Leak test timed out")
        except Exception as e:
            self.logger.error(f"Error running leak test: {e}")

    def _check_connectivity(self):
        """Check basic network connectivity"""
        try:
            # Try to connect to Tor check service
            result = subprocess.run(
                ['curl', '-s', '--max-time', '10', 'https://check.torproject.org/api/ip'],
                capture_output=True,
                timeout=15
            )

            if result.returncode == 0:
                response = json.loads(result.stdout.decode())

                if response.get('IsTor', False):
                    self.logger.debug(f"✅ Connected via Tor: {response.get('IP')}")
                else:
                    self._alert(
                        AlertLevel.CRITICAL,
                        f"NOT using Tor! IP: {response.get('IP')}"
                    )
                    self._activate_killswitch()
            else:
                self.logger.warning("Could not verify Tor connectivity")

        except Exception as e:
            self.logger.error(f"Connectivity check failed: {e}")

    def _check_firewall_rules(self):
        """Check firewall rule integrity"""
        try:
            # Verify nftables rules are loaded
            result = subprocess.run(
                ['nft', 'list', 'ruleset'],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                ruleset = result.stdout.decode()

                # Check for QWAMOS tables
                if 'qwamos_filter' not in ruleset:
                    self._alert(
                        AlertLevel.CRITICAL,
                        "Firewall rules missing - QWAMOS tables not found!"
                    )
                    self._activate_killswitch()
                else:
                    self.logger.debug("✅ Firewall rules intact")
            else:
                self.logger.error("Could not check firewall rules")

        except Exception as e:
            self.logger.error(f"Firewall check failed: {e}")

    def _load_killswitch_rules(self):
        """Pre-load kill switch rules at startup (INACTIVE state)"""
        try:
            killswitch_rules = Path(__file__).parent.parent / 'firewall' / 'rules' / 'killswitch-base.nft'

            if not killswitch_rules.exists():
                self.logger.error(f"Kill switch rules not found: {killswitch_rules}")
                return False

            # Load pre-configured kill switch (policy=accept, inactive)
            result = subprocess.run(
                ['nft', '-f', str(killswitch_rules)],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.logger.error(f"Failed to load kill switch rules: {result.stderr}")
                return False

            self.logger.info("✓ Kill switch rules pre-loaded (inactive)")
            return True

        except Exception as e:
            self.logger.error(f"Exception loading kill switch: {e}")
            return False

    def _activate_killswitch(self):
        """
        Activate network kill switch ATOMICALLY.

        This changes the pre-loaded kill switch policy from ACCEPT to DROP.
        Atomic operation - no race condition, instant activation.
        """
        if self.state['killswitch_active']:
            return  # Already active

        self.logger.critical("🚨 ACTIVATING NETWORK KILL SWITCH 🚨")

        try:
            # ATOMIC ACTIVATION: Change policy to DROP (single command)
            # This happens instantly - no traffic can leak during activation
            result = subprocess.run([
                'nft', 'chain', 'inet', 'qwamos_killswitch', 'output',
                '{', 'policy', 'drop', ';', '}'
            ], capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                self.logger.error(f"Kill switch activation failed: {result.stderr}")
                return

            # Also block input and forward chains
            subprocess.run([
                'nft', 'chain', 'inet', 'qwamos_killswitch', 'input',
                '{', 'policy', 'drop', ';', '}'
            ], timeout=5)

            subprocess.run([
                'nft', 'chain', 'inet', 'qwamos_killswitch', 'forward',
                '{', 'policy', 'drop', ';', '}'
            ], timeout=5)

            self.state['killswitch_active'] = True
            self.logger.critical("✓ Kill switch activated - ALL traffic blocked")

        except Exception as e:
            self.logger.error(f"Failed to activate kill switch: {e}")

    def _deactivate_killswitch(self):
        """Deactivate kill switch (restore normal operation)"""
        if not self.state['killswitch_active']:
            return

        self.logger.warning("Deactivating kill switch...")

        try:
            # Change policies back to ACCEPT
            subprocess.run([
                'nft', 'chain', 'inet', 'qwamos_killswitch', 'output',
                '{', 'policy', 'accept', ';', '}'
            ], timeout=5)

            subprocess.run([
                'nft', 'chain', 'inet', 'qwamos_killswitch', 'input',
                '{', 'policy', 'accept', ';', '}'
            ], timeout=5)

            subprocess.run([
                'nft', 'chain', 'inet', 'qwamos_killswitch', 'forward',
                '{', 'policy', 'accept', ';', '}'
            ], timeout=5)

            self.state['killswitch_active'] = False
            self.logger.info("Kill switch deactivated")

        except Exception as e:
            self.logger.error(f"Failed to deactivate kill switch: {e}")

    def _alert(self, level: AlertLevel, message: str):
        """Log and store alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level.value,
            'message': message
        }

        self.state['alerts'].append(alert)

        # Keep only last 100 alerts
        if len(self.state['alerts']) > 100:
            self.state['alerts'] = self.state['alerts'][-100:]

        # Log with appropriate level
        if level == AlertLevel.CRITICAL:
            self.logger.critical(f"🚨 {message}")
        elif level == AlertLevel.WARNING:
            self.logger.warning(f"⚠️  {message}")
        else:
            self.logger.info(f"ℹ️  {message}")

    def get_status(self) -> Dict:
        """Get current monitoring status"""
        uptime = time.time() - self.state['start_time']

        return {
            'uptime_seconds': uptime,
            'services': self.state['service_status'],
            'recent_alerts': self.state['alerts'][-10:],
            'killswitch_active': self.state['killswitch_active'],
            'last_leak_test': self.state['leak_test_results']
        }


def main():
    """Main entry point"""
    monitor = NetworkMonitor()

    try:
        monitor.start()
    except KeyboardInterrupt:
        monitor.logger.info("Received keyboard interrupt")
    except Exception as e:
        monitor.logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
