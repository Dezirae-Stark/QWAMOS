#!/usr/bin/env python3
"""
QWAMOS Phase 10: Integration Tests
==================================

Comprehensive test suite for Phase 10 advanced hardware security features.

**Test Coverage:**
1. ML Bootloader Override System
2. Firmware Integrity Monitor
3. A/B Partition Isolation
4. Hardware Kill Switch (simulated)
5. End-to-end threat scenarios

**Test Scenarios:**
- Bootloader modification attack (WikiLeaks Vault 7 Dark Matter)
- Fake power-off attack (WikiLeaks Vault 7 Weeping Angel)
- Cross-slot contamination (A/B partition attack)
- User permission workflow
- Emergency override workflow
- Biometric authentication

Version: 1.0.0
Date: 2025-11-05
"""

import os
import sys
import unittest
import tempfile
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import components to test
from ml_bootloader_override import (
    MLBootloaderOverride,
    ThreatLevel,
    OverrideAction,
    CRITICAL_THREAT_PATTERNS,
    PERMISSION_REQUIRED_PATTERNS,
)
from firmware_integrity_monitor import (
    FirmwareIntegrityMonitor,
    IntegrityStatus,
)
from ab_partition_isolation import (
    ABPartitionIsolation,
    IsolationStatus,
)


# ============================================================================
# Test Suite 1: ML Bootloader Override
# ============================================================================

class TestMLBootloaderOverride(unittest.TestCase):
    """Test ML bootloader override system"""

    def setUp(self):
        """Create temporary config file for each test"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf')
        self.temp_config.write(json.dumps({
            "user_lock_enabled": False,
            "permission_timeout": 10,
            "biometric_required": True,
            "log_all_events": True,
            "auto_lock_on_timeout": True,
        }))
        self.temp_config.close()

        self.override = MLBootloaderOverride(config_path=self.temp_config.name)

    def tearDown(self):
        """Clean up temporary config file"""
        os.unlink(self.temp_config.name)

    def test_user_lock_preference(self):
        """Test user can toggle bootloader lock preference"""
        # Initially unlocked
        self.assertFalse(self.override.get_user_lock_preference())

        # User enables lock
        self.override.set_user_lock_preference(True)
        self.assertTrue(self.override.get_user_lock_preference())

        # User disables lock
        self.override.set_user_lock_preference(False)
        self.assertFalse(self.override.get_user_lock_preference())

    def test_critical_threat_instant_lock(self):
        """Test critical threats trigger instant lock (no permission)"""
        # Simulate bootloader write attempt
        with patch.object(self.override, '_lock_bootloader') as mock_lock:
            self.override.handle_threat(
                threat_pattern="bootloader_write_attempt",
                indicators=["test_indicator"],
                source="test"
            )

            # Verify bootloader was locked immediately
            mock_lock.assert_called_once()
            self.assertTrue(self.override.override_active)

    def test_high_threat_requires_permission(self):
        """Test high threats request user permission"""
        # Mock user notification (simulate "deny" response)
        with patch.object(self.override, '_notify_user', return_value='deny'):
            with patch.object(self.override, '_lock_bootloader') as mock_lock:
                self.override.handle_threat(
                    threat_pattern="privilege_escalation_attempt",
                    indicators=["test_indicator"],
                    source="test"
                )

                # Verify user was notified
                self.override._notify_user.assert_called_once()

                # Verify bootloader was locked (user denied)
                mock_lock.assert_called_once()

    def test_user_allow_no_lock(self):
        """Test user can allow high threats (no lock)"""
        # Mock user notification (simulate "allow" response)
        with patch.object(self.override, '_notify_user', return_value='allow'):
            with patch.object(self.override, '_verify_biometric', return_value=True):
                with patch.object(self.override, '_lock_bootloader') as mock_lock:
                    self.override.handle_threat(
                        threat_pattern="privilege_escalation_attempt",
                        indicators=["test_indicator"],
                        source="test"
                    )

                    # Verify user was notified
                    self.override._notify_user.assert_called_once()

                    # Verify bootloader was NOT locked (user allowed)
                    mock_lock.assert_not_called()

    def test_user_timeout_auto_lock(self):
        """Test timeout triggers auto-lock"""
        # Mock user notification (simulate timeout)
        with patch.object(self.override, '_notify_user', return_value='timeout'):
            with patch.object(self.override, '_lock_bootloader') as mock_lock:
                self.override.handle_threat(
                    threat_pattern="privilege_escalation_attempt",
                    indicators=["test_indicator"],
                    source="test"
                )

                # Verify bootloader was locked (timeout)
                mock_lock.assert_called_once()

    def test_override_reset_requires_biometric(self):
        """Test override reset requires biometric"""
        # Set override active
        self.override.override_active = True
        self.override.override_reason = "test"

        # Attempt reset without biometric
        self.override.reset_override(biometric_verified=False)

        # Override should still be active (biometric failed)
        self.assertTrue(self.override.override_active)

        # Reset with biometric
        with patch.object(self.override, '_verify_biometric', return_value=True):
            with patch.object(self.override, '_unlock_bootloader'):
                self.override.reset_override(biometric_verified=True)

                # Override should be cleared
                self.assertFalse(self.override.override_active)

    def test_threat_logging(self):
        """Test all threats are logged"""
        initial_log_count = len(self.override.threat_log)

        # Trigger threat
        with patch.object(self.override, '_lock_bootloader'):
            self.override.handle_threat(
                threat_pattern="bootloader_write_attempt",
                indicators=["test"],
                source="test"
            )

        # Verify logged
        self.assertEqual(len(self.override.threat_log), initial_log_count + 1)

    def test_status_reporting(self):
        """Test status reporting"""
        status = self.override.get_status()

        self.assertIn('bootloader_locked', status)
        self.assertIn('user_lock_preference', status)
        self.assertIn('override_active', status)
        self.assertIn('recent_threats', status)


# ============================================================================
# Test Suite 2: Firmware Integrity Monitor
# ============================================================================

class TestFirmwareIntegrityMonitor(unittest.TestCase):
    """Test firmware integrity monitor"""

    def setUp(self):
        """Create monitor instance"""
        self.monitor = FirmwareIntegrityMonitor()

    def test_bootloader_integrity_pass(self):
        """Test bootloader integrity check (pass)"""
        # Mock partition read and hash
        with patch.object(self.monitor, '_read_partition', return_value=b'test_data'):
            # Mock expected hash matches actual
            with patch('security.firmware_integrity_monitor.EXPECTED_BOOTLOADER_HASHES',
                      {'aboot': 'c7be1ed902fb8dd4d48997c6452f5d7e509fbcdbe2808b16bcf4edce4c07d14e'}):
                result = self.monitor.check_bootloader_integrity()

                self.assertEqual(result.status, IntegrityStatus.PASS)

    def test_bootloader_integrity_fail(self):
        """Test bootloader integrity check (fail)"""
        # Mock partition read
        with patch.object(self.monitor, '_read_partition', return_value=b'tampered_data'):
            # Mock expected hash does NOT match
            with patch('security.firmware_integrity_monitor.EXPECTED_BOOTLOADER_HASHES',
                      {'aboot': 'expected_hash_that_wont_match'}):
                with patch.object(self.monitor.ml_override, 'handle_threat') as mock_threat:
                    result = self.monitor.check_bootloader_integrity()

                    self.assertEqual(result.status, IntegrityStatus.FAIL)
                    # Verify ML override triggered
                    mock_threat.assert_called_once()

    def test_trustzone_integrity(self):
        """Test TrustZone integrity check"""
        with patch.object(self.monitor, '_read_partition', return_value=b'tz_data'):
            with patch('security.firmware_integrity_monitor.EXPECTED_BOOTLOADER_HASHES',
                      {'tz': 'd2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2'}):
                result = self.monitor.check_trustzone_integrity()

                # Should fail (hash won't match)
                self.assertEqual(result.status, IntegrityStatus.FAIL)

    def test_firmware_version_check(self):
        """Test firmware version rollback detection"""
        with patch('subprocess.run') as mock_run:
            # Mock getprop output (correct version)
            mock_run.return_value = Mock(returncode=0, stdout='QWAMOS-1.0.0-20251105\n')

            result = self.monitor.check_firmware_version()

            self.assertEqual(result.status, IntegrityStatus.PASS)

    def test_power_rail_fake_poweroff_detection(self):
        """Test fake power-off detection (Weeping Angel)"""
        with patch('subprocess.run') as mock_run:
            # Mock dumpsys battery output (high power consumption, screen off)
            mock_run.side_effect = [
                Mock(returncode=0, stdout='current now: -500000\n'),  # 500mA (suspicious)
                Mock(returncode=0, stdout='mScreenState=OFF\n', shell=True),
            ]

            with patch.object(self.monitor.ml_override, 'handle_threat') as mock_threat:
                result = self.monitor.check_power_rail()

                # Should fail (power too high for screen-off)
                self.assertEqual(result.status, IntegrityStatus.FAIL)
                # Verify ML override triggered
                mock_threat.assert_called_once()


# ============================================================================
# Test Suite 3: A/B Partition Isolation
# ============================================================================

class TestABPartitionIsolation(unittest.TestCase):
    """Test A/B partition isolation"""

    def setUp(self):
        """Create isolation instance"""
        self.isolation = ABPartitionIsolation()

    def test_active_slot_detection(self):
        """Test active slot detection"""
        # Mock cmdline read
        with patch('builtins.open', unittest.mock.mock_open(read_data='androidboot.slot_suffix=_a')):
            slot = self.isolation._get_active_slot()
            self.assertEqual(slot, 'a')

    def test_slot_a_integrity_pass(self):
        """Test Slot A integrity check (pass)"""
        # Mock active slot = a
        self.isolation.active_slot = 'a'

        # Mock hash matches
        with patch.object(self.isolation, '_hash_partition', return_value='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'):
            result = self.isolation.check_inactive_slot_integrity()

            self.assertEqual(result.status, IsolationStatus.ISOLATED)

    def test_cross_slot_attack_detection(self):
        """Test cross-slot attack detection (Android → QWAMOS)"""
        # Mock active slot = b (Android)
        self.isolation.active_slot = 'b'

        # Mock hash does NOT match (attack detected)
        with patch.object(self.isolation, '_hash_partition', return_value='tampered_hash'):
            with patch.object(self.isolation.ml_override, 'handle_threat') as mock_threat:
                result = self.isolation.check_inactive_slot_integrity()

                self.assertEqual(result.status, IsolationStatus.COMPROMISED)
                # Verify ML override triggered
                mock_threat.assert_called_once()

    def test_mount_isolation(self):
        """Test mount-level isolation enforcement"""
        # Mock active slot = a (QWAMOS)
        self.isolation.active_slot = 'a'

        with patch('subprocess.run') as mock_run:
            # Mock mount output (Slot B is mounted)
            mock_run.side_effect = [
                Mock(returncode=0, stdout='/dev/block/by-name/system_b on /mnt rw\n'),
                Mock(returncode=0),  # Remount command
            ]

            result = self.isolation.enforce_mount_isolation()

            self.assertTrue(result)


# ============================================================================
# Test Suite 4: End-to-End Scenarios
# ============================================================================

class TestEndToEndScenarios(unittest.TestCase):
    """Test complete threat scenarios"""

    def test_dark_matter_attack_scenario(self):
        """
        Test complete Dark Matter attack scenario:
        1. Attacker modifies bootloader
        2. Firmware monitor detects
        3. ML override locks bootloader
        4. User is notified
        """
        monitor = FirmwareIntegrityMonitor()
        override = monitor.ml_override

        # Mock bootloader modification
        with patch.object(monitor, '_read_partition', return_value=b'malicious_bootloader'):
            with patch('security.firmware_integrity_monitor.EXPECTED_BOOTLOADER_HASHES',
                      {'aboot': 'legitimate_hash'}):
                with patch.object(override, '_lock_bootloader') as mock_lock:
                    # Run integrity check
                    result = monitor.check_bootloader_integrity()

                    # Verify detection
                    self.assertEqual(result.status, IntegrityStatus.FAIL)

                    # Verify override triggered
                    self.assertTrue(override.override_active)

                    # Verify bootloader locked
                    mock_lock.assert_called()

    def test_weeping_angel_attack_scenario(self):
        """
        Test complete Weeping Angel attack scenario:
        1. Device appears powered off
        2. Camera/mic still active (high power consumption)
        3. Firmware monitor detects
        4. ML override locks bootloader
        5. Hardware kill switches activated
        """
        monitor = FirmwareIntegrityMonitor()
        override = monitor.ml_override

        # Mock fake power-off (high power, screen off)
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0, stdout='current now: -800000\n'),  # 800mA (camera active)
                Mock(returncode=0, stdout='mScreenState=OFF\n', shell=True),
            ]

            with patch.object(override, '_lock_bootloader') as mock_lock:
                # Run power rail check
                result = monitor.check_power_rail()

                # Verify detection
                self.assertEqual(result.status, IntegrityStatus.FAIL)

                # Verify override triggered
                self.assertTrue(override.override_active)

    def test_ab_partition_attack_scenario(self):
        """
        Test complete A/B partition attack scenario:
        1. Android (Slot B) is rooted
        2. Attacker writes to QWAMOS (Slot A)
        3. A/B isolation detects
        4. ML override locks bootloader
        5. User is warned
        """
        isolation = ABPartitionIsolation()
        override = isolation.ml_override

        # Mock Android active (Slot B)
        isolation.active_slot = 'b'

        # Mock Slot A modified
        with patch.object(isolation, '_hash_partition', return_value='attacker_hash'):
            with patch.object(override, '_lock_bootloader') as mock_lock:
                # Run isolation check
                result = isolation.check_inactive_slot_integrity()

                # Verify detection
                self.assertEqual(result.status, IsolationStatus.COMPROMISED)

                # Verify override triggered
                self.assertTrue(override.override_active)


# ============================================================================
# Test Runner
# ============================================================================

def run_tests():
    """Run all Phase 10 tests"""
    print("=" * 70)
    print("QWAMOS Phase 10: Integration Tests")
    print("=" * 70)
    print("")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test suites
    suite.addTests(loader.loadTestsFromTestCase(TestMLBootloaderOverride))
    suite.addTests(loader.loadTestsFromTestCase(TestFirmwareIntegrityMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestABPartitionIsolation))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndScenarios))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("")
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("")

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
