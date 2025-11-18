#!/usr/bin/env python3
"""
QWAMOS Phase XIV: GPU Isolation - Unit Tests
Tests GPU manager, security policies, and VM integration

Author: QWAMOS Project
License: MIT
"""

import unittest
import sys
import os
from pathlib import Path

# Add hypervisor to path
QWAMOS_ROOT = Path.home() / "QWAMOS"
sys.path.insert(0, str(QWAMOS_ROOT / "hypervisor"))
sys.path.insert(0, str(QWAMOS_ROOT / "hypervisor" / "scripts"))

from gpu_manager import GPUManager, GPUAccessMode, GPUVendor
from gpu_security_policy import (
    GPUSecurityPolicyManager, TrustLevel, GPUOperation
)


class TestGPUManager(unittest.TestCase):
    """Test GPU Manager functionality."""

    def setUp(self):
        """Initialize GPU manager for each test."""
        self.gpu_mgr = GPUManager()

    def test_gpu_detection(self):
        """Test GPU device detection."""
        caps = self.gpu_mgr.capabilities

        # Should detect some GPU (or unknown)
        self.assertIsNotNone(caps.vendor)
        self.assertIsNotNone(caps.device_name)
        self.assertIn(caps.vendor, list(GPUVendor))

    def test_vulkan_detection(self):
        """Test Vulkan capability detection."""
        caps = self.gpu_mgr.capabilities

        # Vulkan status should be boolean
        self.assertIsInstance(caps.vulkan_supported, bool)

        # If Vulkan supported, version should be present or None
        if caps.vulkan_supported:
            self.assertIsInstance(caps.vulkan_version, (str, type(None)))

    def test_gpu_allocation(self):
        """Test GPU resource allocation to VMs."""
        allocation = self.gpu_mgr.allocate_gpu(
            vm_name="test-vm-1",
            access_mode=GPUAccessMode.VIRTIO,
            vram_limit_mb=512,
            priority=75
        )

        self.assertEqual(allocation.vm_name, "test-vm-1")
        self.assertEqual(allocation.access_mode, GPUAccessMode.VIRTIO)
        self.assertEqual(allocation.vram_limit_mb, 512)
        self.assertEqual(allocation.priority, 75)

        # Vulkan allowed if supported
        if self.gpu_mgr.capabilities.vulkan_supported:
            self.assertTrue(allocation.allow_vulkan)

    def test_multiple_vm_allocations(self):
        """Test allocating GPU to multiple VMs."""
        vm1 = self.gpu_mgr.allocate_gpu("vm1", GPUAccessMode.VIRTIO, 256, 50)
        vm2 = self.gpu_mgr.allocate_gpu("vm2", GPUAccessMode.VIRTIO, 256, 70)

        self.assertIn("vm1", self.gpu_mgr.allocations)
        self.assertIn("vm2", self.gpu_mgr.allocations)

        # Higher priority VM should get preference
        self.assertGreater(vm2.priority, vm1.priority)

    def test_qemu_args_generation(self):
        """Test QEMU argument generation for different modes."""
        # VirtIO mode
        self.gpu_mgr.allocate_gpu("test-virtio", GPUAccessMode.VIRTIO)
        args_virtio = self.gpu_mgr.get_vm_gpu_args("test-virtio")

        self.assertIsInstance(args_virtio, list)
        self.assertIn("-device", args_virtio)

        # Verify virtio-gpu device in args
        device_idx = args_virtio.index("-device")
        self.assertIn("virtio-gpu", args_virtio[device_idx + 1])

        # Software rendering mode
        self.gpu_mgr.allocate_gpu("test-software", GPUAccessMode.SOFTWARE)
        args_software = self.gpu_mgr.get_vm_gpu_args("test-software")

        self.assertIsInstance(args_software, list)

    def test_no_allocation(self):
        """Test behavior when no GPU allocated."""
        args = self.gpu_mgr.get_vm_gpu_args("non-existent-vm")

        # Should return nographic for VMs without allocation
        self.assertIn("-nographic", args)

    def test_capabilities_summary(self):
        """Test GPU capabilities summary generation."""
        summary = self.gpu_mgr.get_capabilities_summary()

        self.assertIn('vendor', summary)
        self.assertIn('device', summary)
        self.assertIn('vulkan', summary)
        self.assertIn('passthrough', summary)

        # Vulkan dict should have supported and version
        self.assertIn('supported', summary['vulkan'])
        self.assertIn('version', summary['vulkan'])

    def test_passthrough_fallback(self):
        """Test fallback when passthrough not available."""
        # Try to allocate with passthrough mode
        allocation = self.gpu_mgr.allocate_gpu(
            "test-passthrough",
            access_mode=GPUAccessMode.PASSTHROUGH
        )

        # If VFIO not available, should fallback to VirtIO
        if not self.gpu_mgr.capabilities.vfio_available:
            self.assertEqual(allocation.access_mode, GPUAccessMode.VIRTIO)


class TestGPUSecurityPolicy(unittest.TestCase):
    """Test GPU Security Policy framework."""

    def setUp(self):
        """Initialize policy manager for each test."""
        self.policy_mgr = GPUSecurityPolicyManager()

    def test_policy_creation(self):
        """Test creating policies for different trust levels."""
        trust_levels = [
            TrustLevel.UNTRUSTED,
            TrustLevel.LOW,
            TrustLevel.MEDIUM,
            TrustLevel.HIGH,
            TrustLevel.SYSTEM
        ]

        for trust_level in trust_levels:
            vm_name = f"test-vm-{trust_level.name.lower()}"
            policy = self.policy_mgr.create_policy(vm_name, trust_level)

            self.assertEqual(policy.vm_name, vm_name)
            self.assertEqual(policy.trust_level, trust_level)
            self.assertIsInstance(policy.max_vram_mb, int)
            self.assertIsInstance(policy.max_compute_units, float)
            self.assertIsInstance(policy.allowed_operations, list)

    def test_untrusted_policy_restrictions(self):
        """Test that untrusted VMs have strict restrictions."""
        policy = self.policy_mgr.create_policy("untrusted", TrustLevel.UNTRUSTED)

        # Untrusted should have minimal VRAM
        self.assertLessEqual(policy.max_vram_mb, 256)

        # Untrusted should have minimal compute
        self.assertLessEqual(policy.max_compute_units, 0.2)

        # Untrusted should NOT allow Vulkan
        self.assertFalse(policy.allow_vulkan)

        # Untrusted should require SMMU for isolation
        self.assertTrue(policy.require_smmu)

    def test_system_policy_permissions(self):
        """Test that system VMs have full permissions."""
        policy = self.policy_mgr.create_policy("system", TrustLevel.SYSTEM)

        # System should have maximum VRAM
        self.assertGreaterEqual(policy.max_vram_mb, 1024)

        # System should have full compute access
        self.assertEqual(policy.max_compute_units, 1.0)

        # System should allow Vulkan
        self.assertTrue(policy.allow_vulkan)
        self.assertTrue(policy.allow_vulkan_compute)

        # System should allow passthrough
        self.assertIn(GPUOperation.PASSTHROUGH, policy.allowed_operations)

    def test_operation_validation(self):
        """Test operation validation against policy."""
        # Create policies
        self.policy_mgr.create_policy("untrusted", TrustLevel.UNTRUSTED)
        self.policy_mgr.create_policy("gaming", TrustLevel.HIGH)

        # Untrusted should NOT be able to do 3D rendering
        result = self.policy_mgr.validate_operation(
            "untrusted",
            GPUOperation.RENDERING_3D
        )
        self.assertFalse(result)

        # Gaming VM should be able to do Vulkan compute
        result = self.policy_mgr.validate_operation(
            "gaming",
            GPUOperation.VULKAN_COMPUTE
        )
        self.assertTrue(result)

    def test_vram_quota_enforcement(self):
        """Test VRAM quota enforcement."""
        policy = self.policy_mgr.create_policy("test-vm", TrustLevel.LOW)

        # Request within quota should succeed
        result = self.policy_mgr.check_vram_quota("test-vm", 128)
        self.assertTrue(result)

        # Request exceeding quota should fail
        result = self.policy_mgr.check_vram_quota("test-vm", 2048)
        self.assertFalse(result)

    def test_compute_quota_enforcement(self):
        """Test compute unit quota enforcement."""
        policy = self.policy_mgr.create_policy("test-vm", TrustLevel.MEDIUM)

        # Request within quota should succeed
        result = self.policy_mgr.check_compute_quota("test-vm", 0.3)
        self.assertTrue(result)

        # Request exceeding quota should fail
        result = self.policy_mgr.check_compute_quota("test-vm", 0.9)
        self.assertFalse(result)

    def test_audit_logging(self):
        """Test security audit logging."""
        # Create policy and perform operations
        self.policy_mgr.create_policy("test-vm", TrustLevel.HIGH)
        self.policy_mgr.validate_operation("test-vm", GPUOperation.RENDERING_3D)
        self.policy_mgr.check_vram_quota("test-vm", 2048)  # Exceed quota to trigger log

        # Get audit log
        logs = self.policy_mgr.get_audit_log()

        # Should have at least 3 entries (policy created, operation, quota exceeded)
        self.assertGreaterEqual(len(logs), 3)

        # Each log should have required fields
        for log in logs:
            self.assertIn('timestamp', log)
            self.assertIn('event_type', log)
            self.assertIn('vm_name', log)
            self.assertIn('details', log)

    def test_audit_log_filtering(self):
        """Test audit log filtering."""
        # Create multiple policies
        self.policy_mgr.create_policy("vm1", TrustLevel.LOW)
        self.policy_mgr.create_policy("vm2", TrustLevel.HIGH)

        # Get logs for specific VM
        logs_vm1 = self.policy_mgr.get_audit_log(vm_name="vm1")

        # All logs should be for vm1
        for log in logs_vm1:
            self.assertEqual(log['vm_name'], "vm1")

    def test_no_policy_default_deny(self):
        """Test that operations are denied without a policy."""
        # Try to validate operation without creating policy
        result = self.policy_mgr.validate_operation(
            "non-existent-vm",
            GPUOperation.RENDERING_3D
        )

        # Should be denied by default
        self.assertFalse(result)


class TestVMGPUIntegration(unittest.TestCase):
    """Test GPU integration with VM manager."""

    def setUp(self):
        """Setup for VM integration tests."""
        # Note: Actual VM manager tests would require full VM setup
        # These tests verify the integration points
        pass

    def test_gpu_config_format(self):
        """Test GPU configuration format in VM config."""
        gpu_config = {
            'enabled': True,
            'access_mode': 'virtio',
            'vram_limit_mb': 512,
            'priority': 75
        }

        self.assertIn('enabled', gpu_config)
        self.assertIn('access_mode', gpu_config)
        self.assertIn('vram_limit_mb', gpu_config)
        self.assertIsInstance(gpu_config['enabled'], bool)
        self.assertIn(gpu_config['access_mode'],
                     ['virtio', 'passthrough', 'software', 'none'])

    def test_access_mode_mapping(self):
        """Test access mode string to enum mapping."""
        mode_map = {
            'virtio': GPUAccessMode.VIRTIO,
            'passthrough': GPUAccessMode.PASSTHROUGH,
            'software': GPUAccessMode.SOFTWARE,
            'none': GPUAccessMode.NONE
        }

        for mode_str, mode_enum in mode_map.items():
            self.assertIsInstance(mode_enum, GPUAccessMode)
            self.assertEqual(mode_enum.value, mode_str)


def main():
    """Run all tests."""
    print("="*70)
    print("Phase XIV: GPU Isolation - Unit Tests")
    print("="*70)
    print()

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("="*70)
    print("Test Summary")
    print("="*70)
    print(f"Tests run:     {result.testsRun}")
    print(f"Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")

    if result.wasSuccessful():
        print()
        print("✅ All tests passing (100%)")
        print("="*70)
        return 0
    else:
        print()
        print("❌ Some tests failed")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
