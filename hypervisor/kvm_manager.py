#!/usr/bin/env python3
"""
QWAMOS Phase XII: KVM Acceleration Manager

Provides hardware-accelerated virtualization when available,
with automatic fallback to software emulation (QEMU TCG).

Author: QWAMOS Development Team
License: AGPL-3.0
"""

import os
import subprocess
import platform
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KVMManager")


@dataclass
class CPUInfo:
    """ARM64 CPU information."""
    architecture: str
    implementer: str
    variant: str
    part: str
    revision: str
    features: List[str] = field(default_factory=list)

    @property
    def cpu_name(self) -> str:
        """Resolve CPU part number to name."""
        cpu_parts = {
            "0xd05": "Cortex-A55",
            "0xd0a": "Cortex-A75",
            "0xd0b": "Cortex-A76",
            "0xd0c": "Neoverse-N1",
            "0xd0d": "Cortex-A77",
            "0xd0e": "Cortex-A76AE",
            "0xd40": "Neoverse-V1",
            "0xd41": "Cortex-A78",
            "0xd44": "Cortex-X1",
            "0xd46": "Cortex-A510",
            "0xd47": "Cortex-A710",
            "0xd48": "Cortex-X2",
            "0xd49": "Neoverse-N2",
            "0xd4a": "Neoverse-E1",
            "0xd4b": "Cortex-A78AE",
            "0xd4c": "Cortex-X1C",
            "0xd4d": "Cortex-A715",
            "0xd4e": "Cortex-X3",
            "0xd80": "Cortex-A520",
            "0xd81": "Cortex-A720",
            "0xd82": "Cortex-X4",
        }
        return cpu_parts.get(self.part, f"Unknown (0x{self.part})")

    @property
    def has_crypto_extensions(self) -> bool:
        """Check if CPU supports ARM Crypto Extensions."""
        return "aes" in self.features and "sha1" in self.features


@dataclass
class KVMCapabilities:
    """KVM hardware capabilities detected on device."""
    kvm_available: bool = False
    kvm_device_path: str = "/dev/kvm"
    cpu_supports_virt: bool = False
    arm_virtualization: bool = False
    nested_virtualization: bool = False
    vgic_version: Optional[int] = None  # 2, 3, or 4
    smmu_available: bool = False
    cpu_info: Optional[CPUInfo] = None

    # Security features
    mte_supported: bool = False  # Memory Tagging Extension
    pauth_supported: bool = False  # Pointer Authentication
    bti_supported: bool = False  # Branch Target Identification

    def __str__(self) -> str:
        status = "✅ ENABLED" if self.kvm_available else "❌ DISABLED"
        lines = [
            f"KVM Status: {status}",
            f"CPU: {self.cpu_info.cpu_name if self.cpu_info else 'Unknown'}",
            f"Virtualization Support: {'✅' if self.cpu_supports_virt else '❌'}",
            f"ARM Crypto: {'✅' if self.cpu_info and self.cpu_info.has_crypto_extensions else '❌'}",
            f"SMMU/IOMMU: {'✅' if self.smmu_available else '❌'}",
        ]
        if self.vgic_version:
            lines.append(f"GIC Version: {self.vgic_version}")
        return "\n".join(lines)


class KVMManager:
    """
    KVM hardware acceleration manager for QWAMOS hypervisor.

    Responsibilities:
    - Detect KVM availability and ARM64 virtualization features
    - Configure QEMU to use KVM acceleration when available
    - Manage vCPU topology for big.LITTLE scheduling
    - Enable VirtIO device acceleration (vhost-net, vhost-vsock)
    - Implement fallback to software emulation (QEMU TCG)
    """

    def __init__(self, force_tcg: bool = False):
        """
        Initialize KVM manager.

        Args:
            force_tcg: Force software emulation even if KVM available
        """
        self.force_tcg = force_tcg
        self.capabilities = self._detect_capabilities()
        self.enabled = self.capabilities.kvm_available and not force_tcg

        if self.enabled:
            logger.info("✅ KVM acceleration enabled")
        else:
            logger.warning("⚠️  Using QEMU TCG (software emulation) - slower but functional")

    def _parse_cpuinfo(self) -> Optional[CPUInfo]:
        """Parse /proc/cpuinfo for ARM64 CPU details."""
        try:
            with open("/proc/cpuinfo", "r") as f:
                lines = f.readlines()

            cpu_info = CPUInfo(
                architecture="",
                implementer="",
                variant="",
                part="",
                revision=""
            )

            for line in lines:
                line = line.strip()
                if line.startswith("CPU architecture"):
                    cpu_info.architecture = line.split(":")[-1].strip()
                elif line.startswith("CPU implementer"):
                    cpu_info.implementer = line.split(":")[-1].strip()
                elif line.startswith("CPU variant"):
                    cpu_info.variant = line.split(":")[-1].strip()
                elif line.startswith("CPU part"):
                    cpu_info.part = line.split(":")[-1].strip()
                elif line.startswith("CPU revision"):
                    cpu_info.revision = line.split(":")[-1].strip()
                elif line.startswith("Features"):
                    features = line.split(":")[-1].strip().split()
                    cpu_info.features = features
                    break  # Only parse first CPU

            return cpu_info

        except Exception as e:
            logger.error(f"Failed to parse /proc/cpuinfo: {e}")
            return None

    def _check_virtualization_support(self) -> bool:
        """
        Check if CPU supports ARM Virtualization Extensions.

        ARM64 CPUs with ARMv8.0-A or later should support virtualization,
        but Android kernels often disable it.
        """
        cpu_info = self._parse_cpuinfo()
        if not cpu_info:
            return False

        # ARMv8+ has virtualization extensions
        try:
            arch_version = int(cpu_info.architecture)
            return arch_version >= 8
        except ValueError:
            return False

    def _detect_capabilities(self) -> KVMCapabilities:
        """
        Detect KVM support and ARM64 virtualization features.

        Checks:
        - /dev/kvm existence and permissions
        - ARM Virtualization Extensions in /proc/cpuinfo
        - SMMU/IOMMU availability
        - Security features (MTE, PAuth, BTI)

        Returns:
            KVMCapabilities object with detected features
        """
        caps = KVMCapabilities()

        # Parse CPU info
        caps.cpu_info = self._parse_cpuinfo()

        # Check /dev/kvm
        if os.path.exists("/dev/kvm"):
            try:
                # Attempt to open /dev/kvm to verify permissions
                with open("/dev/kvm", "r") as f:
                    caps.kvm_available = True
                    logger.info(f"✅ {caps.kvm_device_path} accessible")
            except PermissionError:
                logger.error(f"❌ {caps.kvm_device_path} exists but permission denied")
                logger.error("   Run: sudo chmod 666 /dev/kvm")
        else:
            logger.warning(f"❌ {caps.kvm_device_path} not found - KVM not enabled in kernel")

        # Check CPU virtualization support
        caps.cpu_supports_virt = self._check_virtualization_support()
        caps.arm_virtualization = caps.cpu_supports_virt

        # Check for SMMU (IOMMU for ARM)
        caps.smmu_available = os.path.exists("/sys/class/iommu")

        # Check for ARM security features
        if caps.cpu_info:
            # Memory Tagging Extension (ARMv8.5-A+)
            caps.mte_supported = "mte" in caps.cpu_info.features

            # Pointer Authentication (ARMv8.3-A+)
            caps.pauth_supported = any(f.startswith("pauth") for f in caps.cpu_info.features)

            # Branch Target Identification (ARMv8.5-A+)
            caps.bti_supported = "bti" in caps.cpu_info.features

        # Detect GIC version (from device tree if accessible)
        caps.vgic_version = self._detect_gic_version()

        return caps

    def _detect_gic_version(self) -> Optional[int]:
        """
        Detect ARM Generic Interrupt Controller (GIC) version.

        Returns GIC version (2, 3, or 4) or None if unknown.
        """
        # Try to read from device tree
        dt_paths = [
            "/proc/device-tree/interrupt-controller@*/compatible",
            "/sys/firmware/devicetree/base/interrupt-controller*/compatible",
        ]

        for dt_path_pattern in dt_paths:
            try:
                from glob import glob
                for dt_path in glob(dt_path_pattern):
                    with open(dt_path, "rb") as f:
                        content = f.read().decode("utf-8", errors="ignore")
                        if "gic-v4" in content or "gicv4" in content:
                            return 4
                        elif "gic-v3" in content or "gicv3" in content:
                            return 3
                        elif "gic-v2" in content or "gicv2" in content:
                            return 2
            except Exception:
                continue

        # Default to GICv3 for modern ARM64 systems
        return 3

    def generate_qemu_args(self, vm_config: Dict) -> List[str]:
        """
        Generate QEMU command-line arguments for KVM acceleration.

        Args:
            vm_config: VM configuration dictionary with keys:
                - name: VM name (str)
                - cpu: Number of vCPUs (int)
                - memory: Memory size (str, e.g., "2G")
                - disk: Disk image path (str, optional)
                - network: Network config (dict, optional)

        Returns:
            List of QEMU arguments to enable KVM acceleration or TCG fallback

        Example:
            ['-accel', 'kvm', '-cpu', 'host', '-machine', 'virt,gic-version=3']
        """
        args = []

        if self.enabled:
            # Enable KVM hardware acceleration
            args.extend(['-accel', 'kvm'])

            # Use host CPU model for maximum performance
            # This passes through all host CPU features to the guest
            args.extend(['-cpu', 'host'])

            logger.info(f"🚀 Using KVM acceleration for {vm_config.get('name', 'VM')}")

        else:
            # Fallback to software emulation (TCG)
            args.extend(['-accel', 'tcg'])

            # Emulate a common high-performance ARM CPU
            cpu_model = "cortex-a76"  # Good balance of features and compatibility
            args.extend(['-cpu', cpu_model])

            logger.warning(f"🐢 Using TCG (software) for {vm_config.get('name', 'VM')} - expect 50-70% slowdown")

        # Configure machine type with appropriate GIC version
        gic_version = self.capabilities.vgic_version or 3
        machine = f'virt,gic-version={gic_version}'

        # Enable virtualization extensions in machine type if supported
        if self.capabilities.arm_virtualization:
            machine += ',virtualization=on'

        args.extend(['-machine', machine])

        # Configure vCPUs
        vcpu_count = vm_config.get('cpu', 2)
        args.extend(['-smp', str(vcpu_count)])

        # Configure memory
        memory = vm_config.get('memory', '2G')
        args.extend(['-m', memory])

        # Enable vhost-net for network acceleration (if KVM enabled)
        if self.enabled and vm_config.get('network'):
            # TODO: Implement vhost-net configuration
            pass

        return args

    def configure_vcpu_affinity(self, vm_pid: int, vm_name: str,
                              vcpu_policy: str = "auto") -> bool:
        """
        Configure vCPU affinity for big.LITTLE scheduling.

        Args:
            vm_pid: Process ID of QEMU VM
            vm_name: Name of VM to configure
            vcpu_policy: CPU affinity policy:
                - "auto": Kernel decides (default)
                - "big": Pin to performance cores
                - "little": Pin to efficiency cores
                - "isolated": Dedicated core (for realtime VMs)

        Returns:
            True if affinity configured successfully

        Note:
            ARM big.LITTLE topology varies by SoC. Common layouts:
            - Snapdragon 8 Gen 3: CPU 0 (X4), 1-3 (A720), 4-7 (A520)
            - MediaTek Dimensity 9300: All big cores (no little)
        """
        if vcpu_policy == "auto":
            # Let kernel scheduler decide
            logger.info(f"VM {vm_name}: Using automatic CPU scheduling")
            return True

        try:
            # Read CPU topology from /sys
            cpu_topology = self._read_cpu_topology()

            if vcpu_policy == "big":
                # Pin to performance cores
                cpus = cpu_topology.get("big_cores", [0, 1, 2, 3])
            elif vcpu_policy == "little":
                # Pin to efficiency cores
                cpus = cpu_topology.get("little_cores", [4, 5, 6, 7])
            elif vcpu_policy == "isolated":
                # Use last core for isolation
                cpus = [cpu_topology.get("total_cpus", 8) - 1]
            else:
                logger.error(f"Unknown vCPU policy: {vcpu_policy}")
                return False

            # Set CPU affinity using taskset
            cpu_list = ",".join(map(str, cpus))
            subprocess.run(["taskset", "-acp", cpu_list, str(vm_pid)],
                         check=True, capture_output=True)

            logger.info(f"VM {vm_name} (PID {vm_pid}): Pinned to CPUs {cpu_list}")
            return True

        except Exception as e:
            logger.error(f"Failed to set CPU affinity for {vm_name}: {e}")
            return False

    def _read_cpu_topology(self) -> Dict[str, List[int]]:
        """
        Read CPU topology from /sys/devices/system/cpu.

        Returns:
            Dictionary with big_cores, little_cores, and total_cpus
        """
        topology = {
            "big_cores": [],
            "little_cores": [],
            "total_cpus": 0
        }

        try:
            cpu_dirs = list(Path("/sys/devices/system/cpu").glob("cpu[0-9]*"))
            topology["total_cpus"] = len(cpu_dirs)

            # Simple heuristic: higher max frequency = big core
            cpu_freqs = []
            for cpu_dir in sorted(cpu_dirs):
                cpu_num = int(cpu_dir.name.replace("cpu", ""))
                freq_file = cpu_dir / "cpufreq" / "cpuinfo_max_freq"

                if freq_file.exists():
                    with open(freq_file) as f:
                        max_freq = int(f.read().strip())
                        cpu_freqs.append((cpu_num, max_freq))

            if cpu_freqs:
                # Sort by frequency
                cpu_freqs.sort(key=lambda x: x[1], reverse=True)

                # Assume top 50% are big cores
                split = len(cpu_freqs) // 2
                topology["big_cores"] = [cpu for cpu, _ in cpu_freqs[:split]]
                topology["little_cores"] = [cpu for cpu, _ in cpu_freqs[split:]]
            else:
                # Fallback: assume first half are big
                mid = topology["total_cpus"] // 2
                topology["big_cores"] = list(range(mid))
                topology["little_cores"] = list(range(mid, topology["total_cpus"]))

        except Exception as e:
            logger.error(f"Failed to read CPU topology: {e}")
            # Ultra-safe fallback
            topology["big_cores"] = [0, 1]
            topology["little_cores"] = [2, 3, 4, 5, 6, 7]
            topology["total_cpus"] = 8

        return topology

    def benchmark_performance(self, test_vm_config: Dict) -> Dict[str, float]:
        """
        Run quick performance benchmark to verify KVM acceleration.

        Args:
            test_vm_config: Minimal VM config for testing

        Returns:
            Dictionary with benchmark results:
            - boot_time_ms: VM boot time in milliseconds
            - cpu_perf_score: CPU performance score (higher is better)

        Note: This is a lightweight sanity check, not comprehensive benchmarking.
        """
        results = {
            "boot_time_ms": 0.0,
            "cpu_perf_score": 0.0,
        }

        logger.info("Running performance benchmark...")

        # TODO: Implement actual benchmarking
        # - Create minimal Alpine Linux VM
        # - Measure boot time
        # - Run sysbench or dhrystone

        logger.warning("Benchmark not yet implemented")

        return results


def main():
    """Test KVM manager and display capabilities."""
    print("=" * 70)
    print("QWAMOS Phase XII: KVM Acceleration Manager")
    print("=" * 70)

    kvm = KVMManager()

    print(f"\n{kvm.capabilities}\n")

    # Example VM configuration
    vm_config = {
        "name": "test-gateway-vm",
        "cpu": 2,
        "memory": "2G",
    }

    print(f"Generating QEMU args for {vm_config['name']}...")
    qemu_args = kvm.generate_qemu_args(vm_config)
    print(f"\nQEMU command:")
    print(f"  qemu-system-aarch64 {' '.join(qemu_args)} ...")

    print("\n" + "=" * 70)
    print("KVM Manager initialized successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
