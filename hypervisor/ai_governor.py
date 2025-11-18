#!/usr/bin/env python3
"""
QWAMOS AI Governor
Phase XV: Adaptive Resource Management

Intelligent resource governor for VMs:
- Workload classification (idle → critical)
- Adaptive resource allocation
- Threat-aware scheduling
- Power optimization
- Thermal management

Author: QWAMOS Project
License: MIT
"""

import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import statistics

# Add hypervisor to path
sys.path.insert(0, str(Path(__file__).parent))

from resource_monitor import ResourceMonitor, SystemMetrics, VMMetrics


class WorkloadClass(Enum):
    """Workload classification levels."""
    IDLE = "idle"  # Minimal activity
    LIGHT = "light"  # Web browsing, text editing
    MEDIUM = "medium"  # Development, moderate multitasking
    HEAVY = "heavy"  # Gaming, video encoding
    CRITICAL = "critical"  # System services, security analysis


class ThreatLevel(Enum):
    """System threat levels."""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class VMAllocation:
    """Resource allocation for a VM."""
    vm_name: str
    cpu_cores: int  # Number of vCPUs
    cpu_percent_limit: float  # Max CPU percentage
    memory_mb_limit: int  # Memory limit in MB
    io_priority: int  # I/O priority (0-7, 0 highest)
    network_bandwidth_mbps: Optional[int]  # Network bandwidth limit
    workload_class: WorkloadClass
    priority: int  # Overall priority (0-100)


@dataclass
class GovernorDecision:
    """Governor decision for resource allocation."""
    timestamp: float
    system_workload: WorkloadClass
    threat_level: ThreatLevel
    vm_allocations: Dict[str, VMAllocation]
    power_mode: str  # performance, balanced, powersave
    thermal_throttle: bool
    reasoning: str  # Explanation of decision


class WorkloadClassifier:
    """
    Classifies VM workloads based on resource usage patterns.

    Uses rule-based heuristics that can be replaced with ML models.
    """

    def __init__(self):
        """Initialize workload classifier."""
        pass

    def classify_vm_workload(self, vm_metrics: VMMetrics) -> WorkloadClass:
        """
        Classify VM workload based on metrics.

        Args:
            vm_metrics: VM resource metrics

        Returns:
            WorkloadClass
        """
        if vm_metrics.status != "running":
            return WorkloadClass.IDLE

        cpu = vm_metrics.cpu_percent
        memory_pct = vm_metrics.memory_percent
        threads = vm_metrics.threads

        # Rule-based classification
        if cpu < 5 and memory_pct < 10:
            return WorkloadClass.IDLE

        elif cpu < 20 and memory_pct < 30:
            return WorkloadClass.LIGHT

        elif cpu < 50 and memory_pct < 60:
            return WorkloadClass.MEDIUM

        elif cpu < 80 or memory_pct < 80:
            return WorkloadClass.HEAVY

        else:
            return WorkloadClass.CRITICAL

    def classify_system_workload(self, metrics: SystemMetrics) -> WorkloadClass:
        """
        Classify overall system workload.

        Args:
            metrics: System metrics

        Returns:
            WorkloadClass
        """
        cpu = metrics.cpu.system_percent
        memory_pct = metrics.memory.percent

        # System-level classification
        if cpu < 10 and memory_pct < 20:
            return WorkloadClass.IDLE

        elif cpu < 30 and memory_pct < 40:
            return WorkloadClass.LIGHT

        elif cpu < 60 and memory_pct < 70:
            return WorkloadClass.MEDIUM

        elif cpu < 85 or memory_pct < 85:
            return WorkloadClass.HEAVY

        else:
            return WorkloadClass.CRITICAL


class AIGovernor:
    """
    AI-powered resource governor for adaptive VM management.

    Features:
    - Workload classification
    - Adaptive resource allocation
    - Threat-aware scheduling
    - Power optimization
    - Thermal management
    """

    def __init__(self, resource_monitor: ResourceMonitor):
        """
        Initialize AI Governor.

        Args:
            resource_monitor: ResourceMonitor instance
        """
        self.monitor = resource_monitor
        self.classifier = WorkloadClassifier()

        # Decision history
        self.decision_history: deque = deque(maxlen=100)

        # Current threat level
        self.threat_level = ThreatLevel.NONE

        # Power mode
        self.power_mode = "balanced"  # performance, balanced, powersave

        # Thermal throttling
        self.thermal_threshold_c = 75.0  # Start throttling at 75°C
        self.thermal_critical_c = 85.0  # Emergency throttle at 85°C

        # Battery thresholds
        self.battery_low_percent = 20.0
        self.battery_critical_percent = 10.0

    def make_decision(self, vm_names: List[str]) -> GovernorDecision:
        """
        Make resource allocation decision based on current state.

        Args:
            vm_names: List of VM names to manage

        Returns:
            GovernorDecision
        """
        # Collect current metrics
        metrics = self.monitor.collect_all_metrics(vm_names=vm_names)

        # Classify workloads
        system_workload = self.classifier.classify_system_workload(metrics)

        # Determine power mode
        power_mode = self._determine_power_mode(metrics)

        # Check thermal throttling
        thermal_throttle = self._check_thermal_throttling(metrics)

        # Allocate resources to VMs
        vm_allocations = {}
        reasoning_parts = []

        for vm in metrics.vms:
            workload = self.classifier.classify_vm_workload(vm)

            # Calculate allocation based on workload, threat level, and system state
            allocation = self._calculate_vm_allocation(
                vm, workload, system_workload, power_mode, thermal_throttle, metrics
            )

            vm_allocations[vm.vm_name] = allocation

            reasoning_parts.append(
                f"{vm.vm_name}: {workload.value} workload → {allocation.cpu_cores} vCPUs, {allocation.memory_mb_limit} MB"
            )

        # Build reasoning
        reasoning = f"System: {system_workload.value}, Power: {power_mode}, Threat: {self.threat_level.value}"
        if thermal_throttle:
            reasoning += ", THERMAL THROTTLE"
        reasoning += ". " + "; ".join(reasoning_parts)

        decision = GovernorDecision(
            timestamp=time.time(),
            system_workload=system_workload,
            threat_level=self.threat_level,
            vm_allocations=vm_allocations,
            power_mode=power_mode,
            thermal_throttle=thermal_throttle,
            reasoning=reasoning
        )

        # Store decision
        self.decision_history.append(decision)

        return decision

    def _calculate_vm_allocation(
        self,
        vm: VMMetrics,
        workload: WorkloadClass,
        system_workload: WorkloadClass,
        power_mode: str,
        thermal_throttle: bool,
        metrics: SystemMetrics
    ) -> VMAllocation:
        """
        Calculate resource allocation for a VM.

        Args:
            vm: VM metrics
            workload: VM workload class
            system_workload: System workload class
            power_mode: Power mode
            thermal_throttle: Whether thermal throttling active
            metrics: System metrics

        Returns:
            VMAllocation
        """
        # Base allocation based on workload
        base_allocations = {
            WorkloadClass.IDLE: (1, 20, 256, 7, 10),  # cores, cpu%, mem MB, io_prio, priority
            WorkloadClass.LIGHT: (2, 40, 512, 5, 30),
            WorkloadClass.MEDIUM: (4, 60, 1024, 3, 50),
            WorkloadClass.HEAVY: (6, 80, 2048, 1, 70),
            WorkloadClass.CRITICAL: (8, 100, 4096, 0, 90)
        }

        cores, cpu_pct, mem_mb, io_prio, priority = base_allocations.get(
            workload, (2, 40, 512, 5, 30)
        )

        # Adjust for power mode
        if power_mode == "powersave":
            cores = max(1, cores // 2)
            cpu_pct = min(50, cpu_pct)
        elif power_mode == "performance":
            cores = min(8, cores + 2)
            cpu_pct = min(100, cpu_pct + 20)

        # Adjust for thermal throttling
        if thermal_throttle:
            cpu_pct = min(60, cpu_pct)  # Cap at 60% during throttling
            cores = max(1, cores - 1)

        # Adjust for threat level
        if self.threat_level.value >= ThreatLevel.HIGH.value:
            # Boost security VMs
            if "security" in vm.vm_name.lower() or "firewall" in vm.vm_name.lower():
                priority += 20
                cpu_pct = min(100, cpu_pct + 20)
                io_prio = max(0, io_prio - 2)

        # Adjust for available resources
        total_mem_mb = metrics.memory.total_mb
        available_mem_mb = metrics.memory.available_mb

        # Don't allocate more than 80% of total memory to any single VM
        mem_mb = min(mem_mb, int(total_mem_mb * 0.8))

        # If system under pressure, reduce allocations
        if system_workload == WorkloadClass.CRITICAL:
            mem_mb = int(mem_mb * 0.7)
            cpu_pct = int(cpu_pct * 0.7)

        return VMAllocation(
            vm_name=vm.vm_name,
            cpu_cores=cores,
            cpu_percent_limit=cpu_pct,
            memory_mb_limit=mem_mb,
            io_priority=io_prio,
            network_bandwidth_mbps=None,  # No limit by default
            workload_class=workload,
            priority=priority
        )

    def _determine_power_mode(self, metrics: SystemMetrics) -> str:
        """
        Determine optimal power mode based on battery and usage.

        Args:
            metrics: System metrics

        Returns:
            Power mode string
        """
        battery = metrics.battery

        # If charging, prefer performance
        if battery.is_charging:
            return "performance"

        # If battery low, force powersave
        if battery.percent is not None:
            if battery.percent < self.battery_critical_percent:
                return "powersave"
            elif battery.percent < self.battery_low_percent:
                # Use balanced unless system is idle
                if metrics.cpu.system_percent < 20:
                    return "powersave"
                else:
                    return "balanced"

        # Default to balanced
        return "balanced"

    def _check_thermal_throttling(self, metrics: SystemMetrics) -> bool:
        """
        Check if thermal throttling should be enabled.

        Args:
            metrics: System metrics

        Returns:
            True if should throttle
        """
        thermal = metrics.thermal

        # Check CPU temperature
        if thermal.cpu_temp_c:
            if thermal.cpu_temp_c >= self.thermal_critical_c:
                return True
            elif thermal.cpu_temp_c >= self.thermal_threshold_c:
                # Gradual throttling
                return True

        # Check battery temperature
        if thermal.battery_temp_c:
            if thermal.battery_temp_c >= 45.0:  # 45°C battery threshold
                return True

        return False

    def set_threat_level(self, level: ThreatLevel):
        """
        Update system threat level.

        Args:
            level: New threat level
        """
        self.threat_level = level

    def get_decision_history(self, limit: int = 10) -> List[GovernorDecision]:
        """
        Get recent governor decisions.

        Args:
            limit: Maximum number of decisions to return

        Returns:
            List of GovernorDecision
        """
        return list(self.decision_history)[-limit:]

    def print_decision(self, decision: GovernorDecision):
        """
        Print decision in human-readable format.

        Args:
            decision: GovernorDecision to print
        """
        print(f"\n{'='*70}")
        print(f"AI Governor Decision")
        print(f"{'='*70}")
        print(f"Timestamp:       {time.strftime('%H:%M:%S', time.localtime(decision.timestamp))}")
        print(f"System Workload: {decision.system_workload.value.upper()}")
        print(f"Threat Level:    {decision.threat_level.value}")
        print(f"Power Mode:      {decision.power_mode.upper()}")
        print(f"Thermal Throttle: {decision.thermal_throttle}")
        print(f"\nResource Allocations:")

        for vm_name, allocation in decision.vm_allocations.items():
            print(f"\n  {vm_name}:")
            print(f"    Workload:     {allocation.workload_class.value}")
            print(f"    vCPUs:        {allocation.cpu_cores}")
            print(f"    CPU Limit:    {allocation.cpu_percent_limit:.0f}%")
            print(f"    Memory:       {allocation.memory_mb_limit} MB")
            print(f"    I/O Priority: {allocation.io_priority}")
            print(f"    Priority:     {allocation.priority}/100")

        print(f"\nReasoning: {decision.reasoning}")
        print(f"{'='*70}\n")


def main():
    """Demo and testing."""
    print("="*70)
    print("QWAMOS AI Governor - Demo")
    print("="*70)

    # Initialize
    monitor = ResourceMonitor(history_size=10)
    governor = AIGovernor(monitor)

    print("\n1. Making resource allocation decisions...\n")

    # Test VMs
    test_vms = ["test-gpu-vm", "test-pqc-vm"]

    # Make decision
    decision = governor.make_decision(vm_names=test_vms)
    governor.print_decision(decision)

    # Simulate high threat
    print("\n2. Simulating HIGH threat level...\n")
    governor.set_threat_level(ThreatLevel.HIGH)

    decision = governor.make_decision(vm_names=test_vms)
    governor.print_decision(decision)

    # Simulate thermal throttling
    print("\n3. Testing thermal awareness...\n")
    print("   (Would throttle at CPU temp > 75°C)")

    print("\n" + "="*70)
    print("✅ AI Governor operational")
    print("="*70)


if __name__ == "__main__":
    main()
