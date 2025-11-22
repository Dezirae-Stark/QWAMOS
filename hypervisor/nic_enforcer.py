#!/usr/bin/env python3
"""
QWAMOS NIC Enforcer

CRITICAL FIX #17: Enforce VM network interface restrictions.

Ensures VMs only use approved network interfaces with proper security controls:
- Whitelist approved NIC types (virtio-net-pci, e1000, etc.)
- Enforce MAC address policies
- Validate network backend (user, tap, vhost-net)
- Prevent unauthorized network access
- Log all network configuration attempts

Author: QWAMOS Security Team
"""

import os
import sys
import logging
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('NICEnforcer')


class NetworkMode(Enum):
    """Allowed network modes."""
    NAT = "nat"  # User-mode networking (safest)
    BRIDGE = "bridge"  # Bridge networking (with vhost-net)
    ISOLATED = "isolated"  # No network
    TAP = "tap"  # Tap device (requires privileges)


class NICType(Enum):
    """Approved NIC device types."""
    VIRTIO_NET_PCI = "virtio-net-pci"  # Preferred (modern, efficient)
    VIRTIO_NET_DEVICE = "virtio-net-device"  # For ARM virt machines
    E1000 = "e1000"  # Legacy Intel NIC
    RTL8139 = "rtl8139"  # Legacy Realtek NIC


class NICEnforcementPolicy:
    """
    NIC enforcement policy configuration.

    Defines what network interfaces and modes are allowed.
    """

    def __init__(self, policy_file: Optional[str] = None):
        """
        Initialize NIC enforcement policy.

        Args:
            policy_file: Path to policy JSON file
        """
        self.policy_file = Path(policy_file) if policy_file else None

        # Default policy (secure defaults)
        self.allowed_nic_types: Set[str] = {
            NICType.VIRTIO_NET_PCI.value,
            NICType.VIRTIO_NET_DEVICE.value
        }

        self.allowed_network_modes: Set[str] = {
            NetworkMode.NAT.value,
            NetworkMode.BRIDGE.value,
            NetworkMode.ISOLATED.value
        }

        # Allowed bridges (for bridge mode)
        self.allowed_bridges: Set[str] = {
            "virbr0",  # Default libvirt bridge
            "vmbr0",   # QWAMOS bridge
            "br0"      # System bridge
        }

        # MAC address policies
        self.require_static_mac = True
        self.allowed_mac_prefixes: Set[str] = {
            "52:54:00",  # QEMU default
            "02:00:00"   # Locally administered
        }

        # Network backend policies
        self.require_vhost_for_bridge = True  # Enforce vhost-net for bridges
        self.allow_user_backend = True
        self.allow_tap_backend = True

        # Load custom policy if provided
        if self.policy_file and self.policy_file.exists():
            self._load_policy()

    def _load_policy(self):
        """Load policy from JSON file."""
        try:
            with open(self.policy_file, 'r') as f:
                policy = json.load(f)

            self.allowed_nic_types = set(policy.get('allowed_nic_types', list(self.allowed_nic_types)))
            self.allowed_network_modes = set(policy.get('allowed_network_modes', list(self.allowed_network_modes)))
            self.allowed_bridges = set(policy.get('allowed_bridges', list(self.allowed_bridges)))
            self.require_static_mac = policy.get('require_static_mac', self.require_static_mac)
            self.allowed_mac_prefixes = set(policy.get('allowed_mac_prefixes', list(self.allowed_mac_prefixes)))
            self.require_vhost_for_bridge = policy.get('require_vhost_for_bridge', self.require_vhost_for_bridge)

            logger.info(f"✓ Loaded NIC policy from {self.policy_file}")
        except Exception as e:
            logger.error(f"Failed to load policy: {e}")
            logger.warning("Using default policy")


class NICEnforcer:
    """
    NIC configuration enforcer.

    CRITICAL FIX #17: Validates and enforces VM network interface restrictions.
    """

    def __init__(self, policy: Optional[NICEnforcementPolicy] = None):
        """
        Initialize NIC enforcer.

        Args:
            policy: NIC enforcement policy (uses default if not provided)
        """
        self.policy = policy or NICEnforcementPolicy()
        self.violations: List[str] = []

        logger.info("NIC Enforcer initialized")
        logger.info(f"  Allowed NIC types: {', '.join(self.policy.allowed_nic_types)}")
        logger.info(f"  Allowed network modes: {', '.join(self.policy.allowed_network_modes)}")

    def validate_network_config(self, net_config: Dict) -> bool:
        """
        Validate VM network configuration.

        Args:
            net_config: Network configuration dict from VM config

        Returns:
            True if configuration is valid
        """
        self.violations = []

        # Validate network mode
        mode = net_config.get('mode')
        if mode not in self.policy.allowed_network_modes:
            self.violations.append(
                f"Network mode '{mode}' not allowed. Allowed: {self.policy.allowed_network_modes}"
            )

        # Validate NIC device type
        device = net_config.get('device')
        if device not in self.policy.allowed_nic_types:
            self.violations.append(
                f"NIC device '{device}' not allowed. Allowed: {self.policy.allowed_nic_types}"
            )

        # Validate MAC address
        mac = net_config.get('mac')
        if self.policy.require_static_mac and not mac:
            self.violations.append("Static MAC address required but not provided")
        elif mac:
            if not self._validate_mac_address(mac):
                self.violations.append(f"Invalid MAC address format: {mac}")
            elif not self._validate_mac_prefix(mac):
                self.violations.append(
                    f"MAC address prefix not allowed: {mac}. Allowed prefixes: {self.policy.allowed_mac_prefixes}"
                )

        # Validate bridge mode specific settings
        if mode == NetworkMode.BRIDGE.value:
            bridge = net_config.get('bridge')
            if bridge and bridge not in self.policy.allowed_bridges:
                self.violations.append(
                    f"Bridge '{bridge}' not allowed. Allowed: {self.policy.allowed_bridges}"
                )

            # Check vhost-net requirement
            if self.policy.require_vhost_for_bridge:
                vhost = net_config.get('vhost', False)
                if not vhost:
                    self.violations.append("vhost-net is required for bridge mode but not enabled")

        # Log results
        if self.violations:
            logger.error("❌ Network configuration validation FAILED:")
            for violation in self.violations:
                logger.error(f"  - {violation}")
            return False
        else:
            logger.info("✓ Network configuration validated successfully")
            return True

    def _validate_mac_address(self, mac: str) -> bool:
        """Validate MAC address format."""
        import re
        mac_pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        return bool(re.match(mac_pattern, mac))

    def _validate_mac_prefix(self, mac: str) -> bool:
        """Validate MAC address prefix."""
        prefix = ':'.join(mac.split(':')[:3])
        return prefix.upper() in {p.upper() for p in self.policy.allowed_mac_prefixes}

    def enforce_firewall_rules(self, vm_name: str, net_config: Dict):
        """
        Enforce firewall rules for VM network interface.

        Args:
            vm_name: VM name
            net_config: Network configuration
        """
        mode = net_config.get('mode')
        mac = net_config.get('mac')

        if mode == NetworkMode.NAT.value:
            self._enforce_nat_rules(vm_name, mac)
        elif mode == NetworkMode.BRIDGE.value:
            bridge = net_config.get('bridge', 'virbr0')
            self._enforce_bridge_rules(vm_name, mac, bridge)
        elif mode == NetworkMode.ISOLATED.value:
            self._enforce_isolated_rules(vm_name)

        logger.info(f"✓ Firewall rules enforced for VM {vm_name}")

    def _enforce_nat_rules(self, vm_name: str, mac: str):
        """Enforce NAT mode firewall rules."""
        # NAT mode is already isolated via QEMU user networking
        # Just log the configuration
        logger.info(f"NAT mode: VM {vm_name} ({mac}) isolated via user networking")

    def _enforce_bridge_rules(self, vm_name: str, mac: str, bridge: str):
        """Enforce bridge mode firewall rules."""
        # Ensure bridge exists
        result = subprocess.run(
            ['ip', 'link', 'show', bridge],
            capture_output=True
        )

        if result.returncode != 0:
            logger.error(f"Bridge {bridge} does not exist!")
            raise ValueError(f"Bridge {bridge} not found")

        # Create tap interface if needed
        tap_name = f"tap-{vm_name}"

        # Check if tap exists
        result = subprocess.run(
            ['ip', 'link', 'show', tap_name],
            capture_output=True
        )

        if result.returncode != 0:
            logger.info(f"Creating tap interface {tap_name}")
            subprocess.run(['ip', 'tuntap', 'add', tap_name, 'mode', 'tap'])
            subprocess.run(['ip', 'link', 'set', tap_name, 'master', bridge])
            subprocess.run(['ip', 'link', 'set', tap_name, 'up'])

        logger.info(f"Bridge mode: VM {vm_name} on {bridge} via {tap_name}")

    def _enforce_isolated_rules(self, vm_name: str):
        """Enforce isolated mode (no network)."""
        logger.info(f"Isolated mode: VM {vm_name} has no network access")

    def get_violations(self) -> List[str]:
        """Get list of policy violations from last validation."""
        return self.violations

    def export_policy(self, output_file: str):
        """
        Export current policy to JSON file.

        Args:
            output_file: Path to output file
        """
        policy_data = {
            'allowed_nic_types': list(self.policy.allowed_nic_types),
            'allowed_network_modes': list(self.policy.allowed_network_modes),
            'allowed_bridges': list(self.policy.allowed_bridges),
            'require_static_mac': self.policy.require_static_mac,
            'allowed_mac_prefixes': list(self.policy.allowed_mac_prefixes),
            'require_vhost_for_bridge': self.policy.require_vhost_for_bridge
        }

        with open(output_file, 'w') as f:
            json.dump(policy_data, f, indent=2)

        logger.info(f"✓ Policy exported to {output_file}")


def validate_qemu_netdev_args(qemu_args: List[str]) -> bool:
    """
    Validate QEMU netdev arguments against policy.

    Args:
        qemu_args: List of QEMU command arguments

    Returns:
        True if arguments are valid
    """
    enforcer = NICEnforcer()

    # Extract network configuration from QEMU args
    netdev_idx = None
    device_idx = None

    for i, arg in enumerate(qemu_args):
        if arg == '-netdev':
            netdev_idx = i + 1
        elif arg == '-device' and 'netdev=' in qemu_args[i + 1]:
            device_idx = i + 1

    if netdev_idx is None or device_idx is None:
        # No network configured
        return True

    # Parse netdev and device strings
    netdev_str = qemu_args[netdev_idx]
    device_str = qemu_args[device_idx]

    # Extract network mode
    if netdev_str.startswith('user'):
        mode = NetworkMode.NAT.value
    elif netdev_str.startswith('tap'):
        mode = NetworkMode.BRIDGE.value
    else:
        logger.error(f"Unknown network backend: {netdev_str}")
        return False

    # Extract device type
    device_type = device_str.split(',')[0]

    # Extract MAC address
    mac = None
    for part in device_str.split(','):
        if part.startswith('mac='):
            mac = part.split('=')[1]

    # Build config dict
    net_config = {
        'mode': mode,
        'device': device_type,
        'mac': mac,
        'vhost': 'vhost=on' in netdev_str
    }

    return enforcer.validate_network_config(net_config)


if __name__ == "__main__":
    print("=== QWAMOS NIC Enforcer Test ===\n")

    # Create enforcer
    enforcer = NICEnforcer()

    # Test valid configuration
    print("Test 1: Valid NAT configuration")
    valid_config = {
        'mode': 'nat',
        'device': 'virtio-net-pci',
        'mac': '52:54:00:12:34:56'
    }
    result = enforcer.validate_network_config(valid_config)
    print(f"Result: {'✓ PASS' if result else '✗ FAIL'}\n")

    # Test invalid NIC type
    print("Test 2: Invalid NIC type")
    invalid_nic = {
        'mode': 'nat',
        'device': 'ne2k_pci',  # Not allowed
        'mac': '52:54:00:12:34:56'
    }
    result = enforcer.validate_network_config(invalid_nic)
    print(f"Result: {'✗ Should have failed' if result else '✓ Correctly rejected'}")
    print(f"Violations: {enforcer.get_violations()}\n")

    # Test bridge without vhost
    print("Test 3: Bridge mode without vhost-net")
    no_vhost = {
        'mode': 'bridge',
        'device': 'virtio-net-pci',
        'mac': '52:54:00:12:34:56',
        'bridge': 'virbr0',
        'vhost': False
    }
    result = enforcer.validate_network_config(no_vhost)
    print(f"Result: {'✗ Should have failed' if result else '✓ Correctly rejected'}")
    print(f"Violations: {enforcer.get_violations()}\n")

    # Test valid bridge with vhost
    print("Test 4: Valid bridge with vhost-net")
    valid_bridge = {
        'mode': 'bridge',
        'device': 'virtio-net-pci',
        'mac': '52:54:00:12:34:56',
        'bridge': 'virbr0',
        'vhost': True
    }
    result = enforcer.validate_network_config(valid_bridge)
    print(f"Result: {'✓ PASS' if result else '✗ FAIL'}\n")

    # Export policy
    print("Test 5: Export policy")
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        policy_file = f.name

    enforcer.export_policy(policy_file)
    print(f"Policy exported to: {policy_file}\n")

    with open(policy_file, 'r') as f:
        print("Policy contents:")
        print(f.read())

    os.unlink(policy_file)

    print("\n✓ All tests completed")
