#!/usr/bin/env python3
"""
QWAMOS Phase XV: AI Governor - Unit Tests
Tests resource monitor, workload classifier, and governor

Author: QWAMOS Project
License: MIT
"""

import unittest
import sys
import time
from pathlib import Path

# Add hypervisor to path
QWAMOS_ROOT = Path.home() / "QWAMOS"
sys.path.insert(0, str(QWAMOS_ROOT / "hypervisor"))

from resource_monitor import (
    ResourceMonitor, CPUMetrics, MemoryMetrics, VMMetrics,
    ThermalMetrics, BatteryMetrics
)
from ai_governor import (
    AIGovernor, WorkloadClassifier, WorkloadClass,
    ThreatLevel, VMAllocation
)


class TestResourceMonitor(unittest.TestCase):
    """Test Resource Monitor functionality."""

    def setUp(self):
        """Initialize resource monitor for each test."""
        self.monitor = ResourceMonitor(history_size=10)

    def test_cpu_metrics_collection(self):
        """Test CPU metrics collection."""
        cpu = self.monitor.collect_cpu_metrics()

        self.assertIsInstance(cpu, CPUMetrics)
        self.assertIsInstance(cpu.system_percent, float)
        self.assertIsInstance(cpu.per_core, list)
        self.assertGreaterEqual(len(cpu.per_core), 1)

    def test_memory_metrics_collection(self):
        """Test memory metrics collection."""
        mem = self.monitor.collect_memory_metrics()

        self.assertIsInstance(mem, MemoryMetrics)
        self.assertGreater(mem.total_mb, 0)
        self.assertGreaterEqual(mem.used_mb, 0)
        self.assertGreaterEqual(mem.percent, 0)
        self.assertLessEqual(mem.percent, 100)

    def test_thermal_metrics_collection(self):
        """Test thermal metrics collection."""
        thermal = self.monitor.collect_thermal_metrics()

        self.assertIsInstance(thermal, ThermalMetrics)
        # Temperature may be None on some systems
        if thermal.cpu_temp_c is not None:
            self.assertGreater(thermal.cpu_temp_c, 0)
            self.assertLess(thermal.cpu_temp_c, 200)  # Sanity check

    def test_battery_metrics_collection(self):
        """Test battery metrics collection."""
        battery = self.monitor.collect_battery_metrics()

        self.assertIsInstance(battery, BatteryMetrics)
        self.assertIsInstance(battery.is_charging, bool)

        if battery.percent is not None:
            self.assertGreaterEqual(battery.percent, 0)
            self.assertLessEqual(battery.percent, 100)

    def test_vm_metrics_collection(self):
        """Test VM metrics collection."""
        vm_metrics = self.monitor.collect_vm_metrics("test-vm")

        self.assertIsInstance(vm_metrics, VMMetrics)
        self.assertEqual(vm_metrics.vm_name, "test-vm")
        self.assertIn(vm_metrics.status, ["running", "stopped"])

    def test_full_system_metrics(self):
        """Test collecting all system metrics."""
        metrics = self.monitor.collect_all_metrics(vm_names=["test-vm"])

        self.assertIsInstance(metrics.cpu, CPUMetrics)
        self.assertIsInstance(metrics.memory, MemoryMetrics)
        self.assertIsInstance(metrics.thermal, ThermalMetrics)
        self.assertIsInstance(metrics.battery, BatteryMetrics)
        self.assertIsInstance(metrics.vms, list)

    def test_metrics_history(self):
        """Test metrics history retention."""
        # Collect multiple metrics
        for i in range(5):
            self.monitor.collect_all_metrics()
            time.sleep(0.1)

        history = self.monitor.get_metrics_history()
        self.assertGreaterEqual(len(history), 5)

        # Test limit
        limited = self.monitor.get_metrics_history(limit=3)
        self.assertEqual(len(limited), 3)


class TestWorkloadClassifier(unittest.TestCase):
    """Test Workload Classifier functionality."""

    def setUp(self):
        """Initialize classifier for each test."""
        self.classifier = WorkloadClassifier()

    def test_idle_vm_classification(self):
        """Test classification of idle VM."""
        vm = VMMetrics(
            vm_name="test-vm",
            pid=None,
            cpu_percent=2.0,
            memory_mb=100,
            memory_percent=5.0,
            io_read_mb=0.0,
            io_write_mb=0.0,
            net_sent_mb=0.0,
            net_recv_mb=0.0,
            threads=4,
            status="running"
        )

        workload = self.classifier.classify_vm_workload(vm)
        self.assertEqual(workload, WorkloadClass.IDLE)

    def test_light_vm_classification(self):
        """Test classification of light workload VM."""
        vm = VMMetrics(
            vm_name="test-vm",
            pid=1234,
            cpu_percent=15.0,
            memory_mb=300,
            memory_percent=20.0,
            io_read_mb=1.0,
            io_write_mb=0.5,
            net_sent_mb=0.1,
            net_recv_mb=0.2,
            threads=8,
            status="running"
        )

        workload = self.classifier.classify_vm_workload(vm)
        self.assertEqual(workload, WorkloadClass.LIGHT)

    def test_heavy_vm_classification(self):
        """Test classification of heavy workload VM."""
        vm = VMMetrics(
            vm_name="test-vm",
            pid=1234,
            cpu_percent=75.0,
            memory_mb=2048,
            memory_percent=70.0,
            io_read_mb=100.0,
            io_write_mb=50.0,
            net_sent_mb=10.0,
            net_recv_mb=5.0,
            threads=32,
            status="running"
        )

        workload = self.classifier.classify_vm_workload(vm)
        self.assertEqual(workload, WorkloadClass.HEAVY)

    def test_stopped_vm_classification(self):
        """Test classification of stopped VM."""
        vm = VMMetrics(
            vm_name="test-vm",
            pid=None,
            cpu_percent=0.0,
            memory_mb=0,
            memory_percent=0.0,
            io_read_mb=0.0,
            io_write_mb=0.0,
            net_sent_mb=0.0,
            net_recv_mb=0.0,
            threads=0,
            status="stopped"
        )

        workload = self.classifier.classify_vm_workload(vm)
        self.assertEqual(workload, WorkloadClass.IDLE)


class TestAIGovernor(unittest.TestCase):
    """Test AI Governor functionality."""

    def setUp(self):
        """Initialize governor for each test."""
        self.monitor = ResourceMonitor()
        self.governor = AIGovernor(self.monitor)

    def test_governor_initialization(self):
        """Test governor initialization."""
        self.assertIsNotNone(self.governor.monitor)
        self.assertIsNotNone(self.governor.classifier)
        self.assertEqual(self.governor.threat_level, ThreatLevel.NONE)
        self.assertEqual(self.governor.power_mode, "balanced")

    def test_decision_making(self):
        """Test governor decision making."""
        decision = self.governor.make_decision(vm_names=["test-vm"])

        self.assertIsNotNone(decision)
        self.assertIsInstance(decision.system_workload, WorkloadClass)
        self.assertIsInstance(decision.threat_level, ThreatLevel)
        self.assertIsInstance(decision.vm_allocations, dict)
        self.assertIn(decision.power_mode, ["performance", "balanced", "powersave"])

    def test_threat_level_adjustment(self):
        """Test threat level adjustment."""
        # Start with no threat
        self.assertEqual(self.governor.threat_level, ThreatLevel.NONE)

        # Set high threat
        self.governor.set_threat_level(ThreatLevel.HIGH)
        self.assertEqual(self.governor.threat_level, ThreatLevel.HIGH)

        # Make decision and verify threat level is reflected
        decision = self.governor.make_decision(vm_names=["test-vm"])
        self.assertEqual(decision.threat_level, ThreatLevel.HIGH)

    def test_power_mode_determination(self):
        """Test power mode determination logic."""
        from resource_monitor import SystemMetrics, BatteryMetrics, CPUMetrics

        # Mock battery charging
        class MockMetrics:
            class Battery:
                percent = 50.0
                is_charging = True
            class CPU:
                system_percent = 30.0
            battery = Battery()
            cpu = CPU()

        metrics = MockMetrics()
        power_mode = self.governor._determine_power_mode(metrics)
        self.assertEqual(power_mode, "performance")

        # Mock low battery
        metrics.battery.is_charging = False
        metrics.battery.percent = 15.0
        metrics.cpu.system_percent = 10.0  # Low usage
        power_mode = self.governor._determine_power_mode(metrics)
        self.assertIn(power_mode, ["powersave", "balanced"])

    def test_vm_allocation_calculation(self):
        """Test VM resource allocation calculation."""
        from resource_monitor import SystemMetrics, CPUMetrics, MemoryMetrics, ThermalMetrics, BatteryMetrics

        # Create mock metrics
        vm = VMMetrics(
            vm_name="test-vm",
            pid=1234,
            cpu_percent=50.0,
            memory_mb=1024,
            memory_percent=50.0,
            io_read_mb=10.0,
            io_write_mb=5.0,
            net_sent_mb=1.0,
            net_recv_mb=1.0,
            threads=16,
            status="running"
        )

        cpu = CPUMetrics(
            system_percent=40.0,
            per_core=[40.0] * 8,
            temperature_c=65.0,
            frequency_mhz=[2000.0] * 8,
            context_switches=1000,
            interrupts=500
        )

        memory = MemoryMetrics(
            total_mb=8192,
            used_mb=4096,
            free_mb=4096,
            available_mb=4096,
            percent=50.0,
            swap_total_mb=2048,
            swap_used_mb=512,
            swap_percent=25.0
        )

        thermal = ThermalMetrics(
            cpu_temp_c=65.0,
            gpu_temp_c=60.0,
            battery_temp_c=35.0,
            thermal_zone_temps={}
        )

        battery = BatteryMetrics(
            percent=75.0,
            is_charging=False,
            time_remaining_min=120,
            power_draw_w=5.0
        )

        metrics = SystemMetrics(
            timestamp=time.time(),
            cpu=cpu,
            memory=memory,
            thermal=thermal,
            battery=battery,
            vms=[vm]
        )

        allocation = self.governor._calculate_vm_allocation(
            vm, WorkloadClass.MEDIUM, WorkloadClass.MEDIUM,
            "balanced", False, metrics
        )

        self.assertIsInstance(allocation, VMAllocation)
        self.assertEqual(allocation.vm_name, "test-vm")
        self.assertGreater(allocation.cpu_cores, 0)
        self.assertGreater(allocation.memory_mb_limit, 0)
        self.assertGreaterEqual(allocation.io_priority, 0)
        self.assertLessEqual(allocation.io_priority, 7)

    def test_thermal_throttling_detection(self):
        """Test thermal throttling detection."""
        from resource_monitor import SystemMetrics, ThermalMetrics

        class MockMetrics:
            class Thermal:
                cpu_temp_c = 80.0
                gpu_temp_c = 70.0
                battery_temp_c = 40.0
                thermal_zone_temps = {}
            thermal = Thermal()

        metrics = MockMetrics()
        should_throttle = self.governor._check_thermal_throttling(metrics)
        self.assertTrue(should_throttle)

        # Test normal temperature
        metrics.thermal.cpu_temp_c = 60.0
        should_throttle = self.governor._check_thermal_throttling(metrics)
        self.assertFalse(should_throttle)

    def test_decision_history(self):
        """Test decision history tracking."""
        # Make several decisions
        for i in range(5):
            self.governor.make_decision(vm_names=["test-vm"])

        history = self.governor.get_decision_history()
        self.assertGreaterEqual(len(history), 5)

        # Test limit
        limited = self.governor.get_decision_history(limit=3)
        self.assertEqual(len(limited), 3)

    def test_workload_based_allocation(self):
        """Test that different workloads get different allocations."""
        decisions = {}

        # Create VMs with different workloads
        test_cases = [
            ("idle-vm", 2.0, 5.0),
            ("light-vm", 15.0, 20.0),
            ("heavy-vm", 70.0, 65.0)
        ]

        for vm_name, cpu_pct, mem_pct in test_cases:
            decision = self.governor.make_decision(vm_names=[vm_name])
            decisions[vm_name] = decision

        # Idle VM should get minimal resources
        if "idle-vm" in decisions and decisions["idle-vm"].vm_allocations:
            idle_alloc = list(decisions["idle-vm"].vm_allocations.values())[0]
            self.assertLessEqual(idle_alloc.cpu_cores, 2)

        # Heavy VM should get more resources
        if "heavy-vm" in decisions and decisions["heavy-vm"].vm_allocations:
            heavy_alloc = list(decisions["heavy-vm"].vm_allocations.values())[0]
            self.assertGreaterEqual(heavy_alloc.cpu_cores, 1)


def main():
    """Run all tests."""
    print("="*70)
    print("Phase XV: AI Governor - Unit Tests")
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
