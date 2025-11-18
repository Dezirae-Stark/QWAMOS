#!/usr/bin/env python3
"""
QWAMOS GPU Security Policy Framework
Phase XIV: GPU Isolation and Passthrough

Security policy enforcement for GPU resource access:
- VM isolation (prevent GPU resource exhaustion)
- Compute restriction (disable compute shaders for untrusted VMs)
- VRAM quotas and limits
- GPU operation auditing
- Vulkan API restrictions

Author: QWAMOS Project
License: MIT
"""

from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass, field
import time
import hashlib


class TrustLevel(Enum):
    """VM trust levels for GPU access."""
    UNTRUSTED = 0  # Minimal GPU access, no compute
    LOW = 1  # Basic 3D rendering only
    MEDIUM = 2  # 3D + limited compute
    HIGH = 3  # Full GPU access except passthrough
    SYSTEM = 4  # Full GPU access including passthrough


class GPUOperation(Enum):
    """GPU operations that can be restricted."""
    RENDERING_2D = "rendering_2d"
    RENDERING_3D = "rendering_3d"
    COMPUTE_SHADER = "compute_shader"
    VULKAN_COMPUTE = "vulkan_compute"
    VIDEO_DECODE = "video_decode"
    VIDEO_ENCODE = "video_encode"
    PASSTHROUGH = "passthrough"


@dataclass
class GPUSecurityPolicy:
    """Security policy for GPU access."""
    vm_name: str
    trust_level: TrustLevel

    # Resource limits
    max_vram_mb: int = 512
    max_compute_units: float = 0.5  # 0.0-1.0 fraction

    # Allowed operations
    allowed_operations: List[GPUOperation] = field(default_factory=list)

    # Vulkan restrictions
    allow_vulkan: bool = True
    allow_vulkan_compute: bool = False
    max_vulkan_queues: int = 4

    # Monitoring
    enable_audit_log: bool = True
    rate_limit_ms: int = 0  # Minimum ms between GPU calls (0 = no limit)

    # Isolation
    require_smmu: bool = False  # Require IOMMU/SMMU for isolation
    allow_shared_resources: bool = True  # Share GPU with other VMs


class GPUSecurityPolicyManager:
    """
    Manages GPU security policies for VMs.

    Features:
    - Trust-based policy assignment
    - Operation validation
    - Resource quota enforcement
    - Audit logging
    """

    def __init__(self):
        """Initialize policy manager."""
        self.policies: Dict[str, GPUSecurityPolicy] = {}
        self.audit_log: List[Dict] = []
        self.operation_timestamps: Dict[str, float] = {}

    def create_policy(self, vm_name: str, trust_level: TrustLevel) -> GPUSecurityPolicy:
        """
        Create a security policy for a VM based on trust level.

        Args:
            vm_name: VM name
            trust_level: Trust level

        Returns:
            GPUSecurityPolicy
        """
        policy = GPUSecurityPolicy(
            vm_name=vm_name,
            trust_level=trust_level
        )

        # Configure policy based on trust level
        if trust_level == TrustLevel.UNTRUSTED:
            # Minimal access
            policy.max_vram_mb = 128
            policy.max_compute_units = 0.1
            policy.allowed_operations = [
                GPUOperation.RENDERING_2D
            ]
            policy.allow_vulkan = False
            policy.allow_vulkan_compute = False
            policy.require_smmu = True
            policy.allow_shared_resources = False
            policy.rate_limit_ms = 100

        elif trust_level == TrustLevel.LOW:
            # Basic 3D rendering
            policy.max_vram_mb = 256
            policy.max_compute_units = 0.25
            policy.allowed_operations = [
                GPUOperation.RENDERING_2D,
                GPUOperation.RENDERING_3D,
                GPUOperation.VIDEO_DECODE
            ]
            policy.allow_vulkan = True
            policy.allow_vulkan_compute = False
            policy.require_smmu = True
            policy.rate_limit_ms = 50

        elif trust_level == TrustLevel.MEDIUM:
            # 3D + limited compute
            policy.max_vram_mb = 512
            policy.max_compute_units = 0.5
            policy.allowed_operations = [
                GPUOperation.RENDERING_2D,
                GPUOperation.RENDERING_3D,
                GPUOperation.COMPUTE_SHADER,
                GPUOperation.VIDEO_DECODE,
                GPUOperation.VIDEO_ENCODE
            ]
            policy.allow_vulkan = True
            policy.allow_vulkan_compute = True
            policy.max_vulkan_queues = 4
            policy.require_smmu = False
            policy.rate_limit_ms = 10

        elif trust_level == TrustLevel.HIGH:
            # Full GPU access (no passthrough)
            policy.max_vram_mb = 1024
            policy.max_compute_units = 0.8
            policy.allowed_operations = [
                GPUOperation.RENDERING_2D,
                GPUOperation.RENDERING_3D,
                GPUOperation.COMPUTE_SHADER,
                GPUOperation.VULKAN_COMPUTE,
                GPUOperation.VIDEO_DECODE,
                GPUOperation.VIDEO_ENCODE
            ]
            policy.allow_vulkan = True
            policy.allow_vulkan_compute = True
            policy.max_vulkan_queues = 8
            policy.require_smmu = False
            policy.rate_limit_ms = 0

        elif trust_level == TrustLevel.SYSTEM:
            # Full GPU access including passthrough
            policy.max_vram_mb = 2048
            policy.max_compute_units = 1.0
            policy.allowed_operations = list(GPUOperation)  # All operations
            policy.allow_vulkan = True
            policy.allow_vulkan_compute = True
            policy.max_vulkan_queues = 16
            policy.require_smmu = False
            policy.rate_limit_ms = 0

        self.policies[vm_name] = policy
        self._audit("POLICY_CREATED", vm_name, f"Trust level: {trust_level.name}")

        return policy

    def validate_operation(self, vm_name: str, operation: GPUOperation) -> bool:
        """
        Validate if a VM is allowed to perform an operation.

        Args:
            vm_name: VM name
            operation: GPU operation

        Returns:
            True if allowed
        """
        policy = self.policies.get(vm_name)

        if not policy:
            # No policy = deny by default
            self._audit("OPERATION_DENIED", vm_name, f"No policy for {operation.value}")
            return False

        # Check if operation is allowed
        if operation not in policy.allowed_operations:
            self._audit("OPERATION_DENIED", vm_name,
                       f"{operation.value} not in allowed operations")
            return False

        # Check rate limiting
        if policy.rate_limit_ms > 0:
            current_time = time.time() * 1000  # Convert to ms
            key = f"{vm_name}:{operation.value}"
            last_time = self.operation_timestamps.get(key, 0)

            if current_time - last_time < policy.rate_limit_ms:
                self._audit("OPERATION_RATE_LIMITED", vm_name,
                           f"{operation.value} rate limit exceeded")
                return False

            self.operation_timestamps[key] = current_time

        self._audit("OPERATION_ALLOWED", vm_name, operation.value)
        return True

    def check_vram_quota(self, vm_name: str, requested_mb: int) -> bool:
        """
        Check if VRAM request is within quota.

        Args:
            vm_name: VM name
            requested_mb: Requested VRAM in MB

        Returns:
            True if within quota
        """
        policy = self.policies.get(vm_name)

        if not policy:
            return False

        allowed = requested_mb <= policy.max_vram_mb

        if not allowed:
            self._audit("VRAM_QUOTA_EXCEEDED", vm_name,
                       f"Requested {requested_mb} MB, limit {policy.max_vram_mb} MB")

        return allowed

    def check_compute_quota(self, vm_name: str, requested_share: float) -> bool:
        """
        Check if compute unit request is within quota.

        Args:
            vm_name: VM name
            requested_share: Requested compute share (0.0-1.0)

        Returns:
            True if within quota
        """
        policy = self.policies.get(vm_name)

        if not policy:
            return False

        allowed = requested_share <= policy.max_compute_units

        if not allowed:
            self._audit("COMPUTE_QUOTA_EXCEEDED", vm_name,
                       f"Requested {requested_share}, limit {policy.max_compute_units}")

        return allowed

    def get_policy(self, vm_name: str) -> Optional[GPUSecurityPolicy]:
        """
        Get policy for a VM.

        Args:
            vm_name: VM name

        Returns:
            GPUSecurityPolicy or None
        """
        return self.policies.get(vm_name)

    def _audit(self, event_type: str, vm_name: str, details: str):
        """
        Log security event.

        Args:
            event_type: Event type
            vm_name: VM name
            details: Event details
        """
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'vm_name': vm_name,
            'details': details,
            'event_hash': hashlib.sha256(
                f"{event_type}{vm_name}{details}{time.time()}".encode()
            ).hexdigest()[:16]
        }

        self.audit_log.append(event)

        # Keep last 1000 events
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    def get_audit_log(self, vm_name: Optional[str] = None,
                     event_type: Optional[str] = None,
                     limit: int = 100) -> List[Dict]:
        """
        Get audit log entries.

        Args:
            vm_name: Filter by VM name (optional)
            event_type: Filter by event type (optional)
            limit: Maximum entries to return

        Returns:
            List of audit log entries
        """
        logs = self.audit_log

        if vm_name:
            logs = [log for log in logs if log['vm_name'] == vm_name]

        if event_type:
            logs = [log for log in logs if log['event_type'] == event_type]

        return logs[-limit:]

    def print_policy_summary(self, vm_name: str):
        """
        Print policy summary for a VM.

        Args:
            vm_name: VM name
        """
        policy = self.policies.get(vm_name)

        if not policy:
            print(f"No policy found for VM: {vm_name}")
            return

        print(f"\n{'='*70}")
        print(f"GPU Security Policy: {vm_name}")
        print(f"{'='*70}")
        print(f"Trust Level:       {policy.trust_level.name}")
        print(f"\nResource Limits:")
        print(f"  VRAM:            {policy.max_vram_mb} MB")
        print(f"  Compute Share:   {policy.max_compute_units * 100:.0f}%")
        print(f"\nVulkan Access:")
        print(f"  Enabled:         {policy.allow_vulkan}")
        print(f"  Compute:         {policy.allow_vulkan_compute}")
        print(f"  Max Queues:      {policy.max_vulkan_queues}")
        print(f"\nSecurity:")
        print(f"  Require SMMU:    {policy.require_smmu}")
        print(f"  Shared GPU:      {policy.allow_shared_resources}")
        print(f"  Rate Limit:      {policy.rate_limit_ms} ms")
        print(f"  Audit Logging:   {policy.enable_audit_log}")
        print(f"\nAllowed Operations:")
        for op in policy.allowed_operations:
            print(f"  ✅ {op.value}")
        print(f"{'='*70}\n")


def main():
    """Demo and testing."""
    print("="*70)
    print("QWAMOS GPU Security Policy Framework - Demo")
    print("="*70)

    manager = GPUSecurityPolicyManager()

    # Create policies for different trust levels
    print("\n1. Creating policies for different trust levels...\n")

    test_vms = [
        ("untrusted-vm", TrustLevel.UNTRUSTED),
        ("web-browser-vm", TrustLevel.LOW),
        ("development-vm", TrustLevel.MEDIUM),
        ("gaming-vm", TrustLevel.HIGH),
        ("system-vm", TrustLevel.SYSTEM)
    ]

    for vm_name, trust_level in test_vms:
        policy = manager.create_policy(vm_name, trust_level)
        print(f"Created policy for '{vm_name}' (Trust: {trust_level.name})")

    # Test operation validation
    print("\n2. Testing operation validation...\n")

    test_operations = [
        ("untrusted-vm", GPUOperation.RENDERING_3D, False),
        ("untrusted-vm", GPUOperation.RENDERING_2D, True),
        ("gaming-vm", GPUOperation.VULKAN_COMPUTE, True),
        ("web-browser-vm", GPUOperation.COMPUTE_SHADER, False),
        ("system-vm", GPUOperation.PASSTHROUGH, True)
    ]

    for vm_name, operation, expected in test_operations:
        result = manager.validate_operation(vm_name, operation)
        status = "✅" if result == expected else "❌"
        print(f"{status} {vm_name}: {operation.value} -> {'ALLOWED' if result else 'DENIED'}")

    # Test quota checks
    print("\n3. Testing resource quotas...\n")

    quota_tests = [
        ("untrusted-vm", "VRAM", 256, False),
        ("untrusted-vm", "VRAM", 64, True),
        ("gaming-vm", "COMPUTE", 0.9, False),
        ("gaming-vm", "COMPUTE", 0.7, True)
    ]

    for vm_name, resource_type, amount, expected in quota_tests:
        if resource_type == "VRAM":
            result = manager.check_vram_quota(vm_name, amount)
        else:
            result = manager.check_compute_quota(vm_name, amount)

        status = "✅" if result == expected else "❌"
        print(f"{status} {vm_name}: {resource_type} {amount} -> {'ALLOWED' if result else 'DENIED'}")

    # Show policy details
    print("\n4. Policy Details:\n")
    manager.print_policy_summary("gaming-vm")

    # Show audit log
    print("\n5. Recent Audit Log (last 10 entries):\n")
    recent_logs = manager.get_audit_log(limit=10)
    for log in recent_logs[-10:]:
        timestamp = time.strftime('%H:%M:%S', time.localtime(log['timestamp']))
        print(f"[{timestamp}] {log['event_type']:25} {log['vm_name']:20} - {log['details']}")

    print("\n" + "="*70)
    print("✅ GPU Security Policy Framework operational")
    print("="*70)


if __name__ == "__main__":
    main()
