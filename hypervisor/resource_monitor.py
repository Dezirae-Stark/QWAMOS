#!/usr/bin/env python3
"""
QWAMOS Resource Monitor
Phase XV: AI Governor

Real-time resource monitoring for adaptive VM management:
- CPU usage per VM and system-wide
- Memory utilization tracking
- I/O statistics
- Thermal sensor readings
- Battery status monitoring
- Network bandwidth usage

Author: QWAMOS Project
License: MIT
"""

import os
import time
import psutil
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import deque
import subprocess


@dataclass
class CPUMetrics:
    """CPU usage metrics."""
    system_percent: float  # Overall CPU usage
    per_core: List[float]  # Per-core usage
    temperature_c: Optional[float]  # CPU temperature
    frequency_mhz: List[float]  # Per-core frequency
    context_switches: int  # Context switches per second
    interrupts: int  # Interrupts per second


@dataclass
class MemoryMetrics:
    """Memory usage metrics."""
    total_mb: int
    used_mb: int
    free_mb: int
    available_mb: int
    percent: float
    swap_total_mb: int
    swap_used_mb: int
    swap_percent: float


@dataclass
class VMMetrics:
    """Per-VM resource metrics."""
    vm_name: str
    pid: Optional[int]
    cpu_percent: float
    memory_mb: int
    memory_percent: float
    io_read_mb: float
    io_write_mb: float
    net_sent_mb: float
    net_recv_mb: float
    threads: int
    status: str  # running, stopped, paused


@dataclass
class ThermalMetrics:
    """Thermal sensor metrics."""
    cpu_temp_c: Optional[float]
    gpu_temp_c: Optional[float]
    battery_temp_c: Optional[float]
    thermal_zone_temps: Dict[str, float]


@dataclass
class BatteryMetrics:
    """Battery status metrics."""
    percent: Optional[float]
    is_charging: bool
    time_remaining_min: Optional[int]
    power_draw_w: Optional[float]


@dataclass
class SystemMetrics:
    """Complete system metrics snapshot."""
    timestamp: float
    cpu: CPUMetrics
    memory: MemoryMetrics
    thermal: ThermalMetrics
    battery: BatteryMetrics
    vms: List[VMMetrics]


class ResourceMonitor:
    """
    Monitors system and VM resources in real-time.

    Features:
    - CPU usage tracking (system and per-VM)
    - Memory utilization monitoring
    - Thermal sensor readings
    - Battery status
    - Historical data retention
    """

    def __init__(self, history_size: int = 100):
        """
        Initialize resource monitor.

        Args:
            history_size: Number of metric snapshots to retain
        """
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)

        # Cache for process tracking
        self.vm_processes: Dict[str, psutil.Process] = {}

        # Last measurement for rate calculations
        self.last_cpu_times = None
        self.last_io_counters = {}

    def collect_cpu_metrics(self) -> CPUMetrics:
        """
        Collect CPU metrics.

        Returns:
            CPUMetrics object
        """
        # Overall CPU usage
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
        except (PermissionError, OSError):
            cpu_percent = 0.0

        # Per-core usage
        try:
            per_core = psutil.cpu_percent(interval=0.1, percpu=True)
        except (PermissionError, OSError):
            cpu_count = psutil.cpu_count() or 8
            per_core = [0.0] * cpu_count

        # CPU frequency
        try:
            freq = psutil.cpu_freq(percpu=True)
            if freq:
                if isinstance(freq, list):
                    frequencies = [f.current for f in freq]
                else:
                    frequencies = [freq.current]
            else:
                frequencies = [0.0] * psutil.cpu_count()
        except (PermissionError, OSError, AttributeError):
            frequencies = [0.0] * (psutil.cpu_count() or 8)

        # Temperature
        temperature = self._read_cpu_temperature()

        # Context switches and interrupts
        try:
            cpu_stats = psutil.cpu_stats()
            ctx_switches = cpu_stats.ctx_switches
            interrupts = cpu_stats.interrupts
        except (PermissionError, OSError, AttributeError):
            ctx_switches = 0
            interrupts = 0

        return CPUMetrics(
            system_percent=cpu_percent,
            per_core=per_core,
            temperature_c=temperature,
            frequency_mhz=frequencies,
            context_switches=ctx_switches,
            interrupts=interrupts
        )

    def collect_memory_metrics(self) -> MemoryMetrics:
        """
        Collect memory metrics.

        Returns:
            MemoryMetrics object
        """
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return MemoryMetrics(
            total_mb=mem.total // (1024 * 1024),
            used_mb=mem.used // (1024 * 1024),
            free_mb=mem.free // (1024 * 1024),
            available_mb=mem.available // (1024 * 1024),
            percent=mem.percent,
            swap_total_mb=swap.total // (1024 * 1024),
            swap_used_mb=swap.used // (1024 * 1024),
            swap_percent=swap.percent
        )

    def collect_thermal_metrics(self) -> ThermalMetrics:
        """
        Collect thermal sensor metrics.

        Returns:
            ThermalMetrics object
        """
        cpu_temp = self._read_cpu_temperature()
        gpu_temp = self._read_gpu_temperature()
        battery_temp = self._read_battery_temperature()

        # Read all thermal zones
        thermal_zones = {}
        thermal_dir = Path("/sys/class/thermal")

        if thermal_dir.exists():
            for zone_dir in thermal_dir.glob("thermal_zone*"):
                try:
                    temp_file = zone_dir / "temp"
                    if temp_file.exists():
                        with open(temp_file, 'r') as f:
                            temp_millic = int(f.read().strip())
                            zone_name = zone_dir.name
                            thermal_zones[zone_name] = temp_millic / 1000.0
                except:
                    pass

        return ThermalMetrics(
            cpu_temp_c=cpu_temp,
            gpu_temp_c=gpu_temp,
            battery_temp_c=battery_temp,
            thermal_zone_temps=thermal_zones
        )

    def collect_battery_metrics(self) -> BatteryMetrics:
        """
        Collect battery metrics.

        Returns:
            BatteryMetrics object
        """
        try:
            battery = psutil.sensors_battery()
            if battery:
                return BatteryMetrics(
                    percent=battery.percent,
                    is_charging=battery.power_plugged,
                    time_remaining_min=battery.secsleft // 60 if battery.secsleft > 0 else None,
                    power_draw_w=None  # Would need additional sensors
                )
        except:
            pass

        # Android-specific battery reading
        battery_percent = self._read_android_battery_percent()
        is_charging = self._read_android_charging_status()

        return BatteryMetrics(
            percent=battery_percent,
            is_charging=is_charging,
            time_remaining_min=None,
            power_draw_w=None
        )

    def collect_vm_metrics(self, vm_name: str) -> Optional[VMMetrics]:
        """
        Collect metrics for a specific VM.

        Args:
            vm_name: VM name

        Returns:
            VMMetrics or None if VM not running
        """
        # Find VM process
        proc = self._find_vm_process(vm_name)

        if not proc:
            return VMMetrics(
                vm_name=vm_name,
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

        try:
            # CPU usage
            cpu_percent = proc.cpu_percent(interval=0.1)

            # Memory usage
            mem_info = proc.memory_info()
            memory_mb = mem_info.rss // (1024 * 1024)
            memory_percent = proc.memory_percent()

            # I/O counters
            try:
                io_counters = proc.io_counters()
                io_read_mb = io_counters.read_bytes / (1024 * 1024)
                io_write_mb = io_counters.write_bytes / (1024 * 1024)
            except:
                io_read_mb = 0.0
                io_write_mb = 0.0

            # Network (would need network namespace isolation to get per-VM)
            net_sent_mb = 0.0
            net_recv_mb = 0.0

            # Thread count
            threads = proc.num_threads()

            status = "running"

            return VMMetrics(
                vm_name=vm_name,
                pid=proc.pid,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                io_read_mb=io_read_mb,
                io_write_mb=io_write_mb,
                net_sent_mb=net_sent_mb,
                net_recv_mb=net_recv_mb,
                threads=threads,
                status=status
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def collect_all_metrics(self, vm_names: List[str] = None) -> SystemMetrics:
        """
        Collect all system metrics.

        Args:
            vm_names: List of VM names to monitor (optional)

        Returns:
            SystemMetrics object
        """
        # Collect system metrics
        cpu = self.collect_cpu_metrics()
        memory = self.collect_memory_metrics()
        thermal = self.collect_thermal_metrics()
        battery = self.collect_battery_metrics()

        # Collect VM metrics
        vms = []
        if vm_names:
            for vm_name in vm_names:
                vm_metrics = self.collect_vm_metrics(vm_name)
                if vm_metrics:
                    vms.append(vm_metrics)

        metrics = SystemMetrics(
            timestamp=time.time(),
            cpu=cpu,
            memory=memory,
            thermal=thermal,
            battery=battery,
            vms=vms
        )

        # Add to history
        self.metrics_history.append(metrics)

        return metrics

    def get_metrics_history(self, limit: int = None) -> List[SystemMetrics]:
        """
        Get historical metrics.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of SystemMetrics
        """
        if limit:
            return list(self.metrics_history)[-limit:]
        return list(self.metrics_history)

    def _find_vm_process(self, vm_name: str) -> Optional[psutil.Process]:
        """
        Find process for a VM.

        Args:
            vm_name: VM name

        Returns:
            psutil.Process or None
        """
        # Check cache first
        if vm_name in self.vm_processes:
            proc = self.vm_processes[vm_name]
            try:
                if proc.is_running():
                    return proc
            except:
                pass

        # Search for process
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'qemu' in ' '.join(cmdline).lower():
                    if vm_name in ' '.join(cmdline):
                        self.vm_processes[vm_name] = proc
                        return proc
            except:
                pass

        return None

    def _read_cpu_temperature(self) -> Optional[float]:
        """Read CPU temperature from thermal sensors."""
        try:
            # Try psutil first
            temps = psutil.sensors_temperatures()
            if temps:
                # Look for CPU temperature
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'core' in name.lower():
                        if entries:
                            return entries[0].current
        except:
            pass

        # Try reading from sysfs
        thermal_zones = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/devices/virtual/thermal/thermal_zone0/temp"
        ]

        for zone_file in thermal_zones:
            try:
                with open(zone_file, 'r') as f:
                    temp_millic = int(f.read().strip())
                    return temp_millic / 1000.0
            except:
                pass

        return None

    def _read_gpu_temperature(self) -> Optional[float]:
        """Read GPU temperature from thermal sensors."""
        # Try to find GPU thermal zone
        thermal_dir = Path("/sys/class/thermal")

        if thermal_dir.exists():
            for zone_dir in thermal_dir.glob("thermal_zone*"):
                try:
                    type_file = zone_dir / "type"
                    if type_file.exists():
                        with open(type_file, 'r') as f:
                            zone_type = f.read().strip().lower()
                            if 'gpu' in zone_type:
                                temp_file = zone_dir / "temp"
                                if temp_file.exists():
                                    with open(temp_file, 'r') as f:
                                        temp_millic = int(f.read().strip())
                                        return temp_millic / 1000.0
                except:
                    pass

        return None

    def _read_battery_temperature(self) -> Optional[float]:
        """Read battery temperature."""
        # Android battery temp
        battery_temp_file = "/sys/class/power_supply/battery/temp"

        try:
            if Path(battery_temp_file).exists():
                with open(battery_temp_file, 'r') as f:
                    temp_decidegc = int(f.read().strip())
                    return temp_decidegc / 10.0  # Convert decidegrees to degrees
        except:
            pass

        return None

    def _read_android_battery_percent(self) -> Optional[float]:
        """Read battery percentage on Android."""
        try:
            result = subprocess.run(
                ["termux-battery-status"],
                capture_output=True,
                text=True,
                timeout=1
            )

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                return data.get('percentage')
        except:
            pass

        # Try sysfs
        battery_capacity_file = "/sys/class/power_supply/battery/capacity"
        try:
            if Path(battery_capacity_file).exists():
                with open(battery_capacity_file, 'r') as f:
                    return float(f.read().strip())
        except:
            pass

        return None

    def _read_android_charging_status(self) -> bool:
        """Read charging status on Android."""
        try:
            result = subprocess.run(
                ["termux-battery-status"],
                capture_output=True,
                text=True,
                timeout=1
            )

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                status = data.get('status', '').lower()
                return 'charging' in status or 'full' in status
        except:
            pass

        # Try sysfs
        battery_status_file = "/sys/class/power_supply/battery/status"
        try:
            if Path(battery_status_file).exists():
                with open(battery_status_file, 'r') as f:
                    status = f.read().strip().lower()
                    return 'charging' in status or 'full' in status
        except:
            pass

        return False


def main():
    """Demo and testing."""
    print("="*70)
    print("QWAMOS Resource Monitor - Demo")
    print("="*70)

    monitor = ResourceMonitor(history_size=10)

    print("\n1. Collecting system metrics...\n")

    # Collect metrics
    metrics = monitor.collect_all_metrics(vm_names=["test-gpu-vm", "test-pqc-vm"])

    # Display CPU metrics
    print("CPU Metrics:")
    print(f"  System Usage:    {metrics.cpu.system_percent:.1f}%")
    print(f"  Per-Core Usage:  {[f'{p:.1f}%' for p in metrics.cpu.per_core]}")
    if metrics.cpu.temperature_c:
        print(f"  Temperature:     {metrics.cpu.temperature_c:.1f}°C")
    print(f"  Frequencies:     {[f'{f:.0f} MHz' for f in metrics.cpu.frequency_mhz]}")
    print(f"  Context Switches: {metrics.cpu.context_switches}")

    # Display memory metrics
    print(f"\nMemory Metrics:")
    print(f"  Total:           {metrics.memory.total_mb} MB")
    print(f"  Used:            {metrics.memory.used_mb} MB ({metrics.memory.percent:.1f}%)")
    print(f"  Available:       {metrics.memory.available_mb} MB")
    print(f"  Swap:            {metrics.memory.swap_used_mb}/{metrics.memory.swap_total_mb} MB ({metrics.memory.swap_percent:.1f}%)")

    # Display thermal metrics
    print(f"\nThermal Metrics:")
    if metrics.thermal.cpu_temp_c:
        print(f"  CPU Temperature: {metrics.thermal.cpu_temp_c:.1f}°C")
    if metrics.thermal.gpu_temp_c:
        print(f"  GPU Temperature: {metrics.thermal.gpu_temp_c:.1f}°C")
    if metrics.thermal.battery_temp_c:
        print(f"  Battery Temp:    {metrics.thermal.battery_temp_c:.1f}°C")

    if metrics.thermal.thermal_zone_temps:
        print(f"  Thermal Zones:")
        for zone, temp in metrics.thermal.thermal_zone_temps.items():
            print(f"    {zone}: {temp:.1f}°C")

    # Display battery metrics
    print(f"\nBattery Metrics:")
    if metrics.battery.percent is not None:
        print(f"  Battery Level:   {metrics.battery.percent:.0f}%")
    print(f"  Charging:        {'Yes' if metrics.battery.is_charging else 'No'}")
    if metrics.battery.time_remaining_min:
        print(f"  Time Remaining:  {metrics.battery.time_remaining_min} minutes")

    # Display VM metrics
    if metrics.vms:
        print(f"\nVM Metrics:")
        for vm in metrics.vms:
            print(f"\n  VM: {vm.vm_name}")
            print(f"    Status:        {vm.status}")
            if vm.status == "running":
                print(f"    PID:           {vm.pid}")
                print(f"    CPU:           {vm.cpu_percent:.1f}%")
                print(f"    Memory:        {vm.memory_mb} MB ({vm.memory_percent:.1f}%)")
                print(f"    I/O Read:      {vm.io_read_mb:.1f} MB")
                print(f"    I/O Write:     {vm.io_write_mb:.1f} MB")
                print(f"    Threads:       {vm.threads}")

    print("\n" + "="*70)
    print("✅ Resource monitor operational")
    print("="*70)


if __name__ == "__main__":
    main()
