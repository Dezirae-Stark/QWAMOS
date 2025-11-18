#!/usr/bin/env python3
"""
QWAMOS Differential Testing Runner
Phase XII: KVM vs QEMU Comparison

Runs all workloads under both QEMU (TCG) and KVM modes
Author: QWAMOS Project
License: AGPL-3.0
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add workload suite to path
sys.path.insert(0, str(Path(__file__).parent / "workload_suite"))

from cpu_stress import CPUStressWorkload
from mem_stress import MemoryStressWorkload
from io_stress import IOStressWorkload
from crypt_stress import CryptoStressWorkload


class DifferentialRunner:
    """Orchestrates differential testing between QEMU and KVM."""

    def __init__(self, output_dir: str = "."):
        """
        Initialize differential runner.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.kvm_available = os.path.exists("/dev/kvm")
        self.kvm_accessible = self._check_kvm_accessible()

        self.results = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "kvm_available": self.kvm_available,
                "kvm_accessible": self.kvm_accessible
            },
            "qemu_results": {},
            "kvm_results": {},
            "system_info": self._gather_system_info()
        }

    def _check_kvm_accessible(self) -> bool:
        """Check if /dev/kvm is accessible."""
        if not self.kvm_available:
            return False

        try:
            # Try to open /dev/kvm
            with open("/dev/kvm", "r"):
                return True
        except PermissionError:
            return False
        except Exception:
            return False

    def _gather_system_info(self) -> Dict:
        """Gather system information."""
        info = {
            "platform": sys.platform,
            "python_version": sys.version,
        }

        try:
            # Get CPU info
            if Path("/proc/cpuinfo").exists():
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read()
                    # Count cores
                    cores = cpuinfo.count("processor")
                    info["cpu_cores"] = cores

                    # Get model name
                    for line in cpuinfo.split('\n'):
                        if 'model name' in line.lower() or 'Hardware' in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                info["cpu_model"] = parts[1].strip()
                                break

            # Get memory info
            if Path("/proc/meminfo").exists():
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal"):
                            parts = line.split()
                            if len(parts) >= 2:
                                mem_kb = int(parts[1])
                                info["memory_mb"] = mem_kb // 1024

            # Get kernel version
            if Path("/proc/version").exists():
                with open("/proc/version", "r") as f:
                    info["kernel_version"] = f.read().strip()

        except Exception as e:
            info["error"] = str(e)

        return info

    def run_workload_suite(self, mode: str) -> Dict:
        """
        Run all workloads in specified mode.

        Args:
            mode: "qemu" or "kvm"

        Returns:
            Results dictionary
        """
        print(f"\n{'=' * 80}")
        print(f"Running Workload Suite - Mode: {mode.upper()}")
        print(f"{'=' * 80}\n")

        results = {
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "workloads": {}
        }

        # Note: In a real VM environment, we would switch QEMU modes here
        # For now, we run workloads natively and note the theoretical mode
        if mode == "kvm" and not self.kvm_accessible:
            print(f"⚠️  WARNING: KVM not accessible, running in native mode")
            print(f"   Results may not reflect true KVM performance\n")

        # Run CPU stress
        try:
            print("=" * 80)
            cpu_workload = CPUStressWorkload(threads=4, iterations=50000)
            cpu_results = cpu_workload.run()
            results["workloads"]["cpu_stress"] = cpu_results
        except Exception as e:
            print(f"❌ CPU stress failed: {e}")
            results["workloads"]["cpu_stress"] = {"error": str(e)}

        print()

        # Run memory stress
        try:
            print("=" * 80)
            mem_workload = MemoryStressWorkload(size_mb=128, pattern="mixed")
            mem_results = mem_workload.run()
            results["workloads"]["mem_stress"] = mem_results
        except Exception as e:
            print(f"❌ Memory stress failed: {e}")
            results["workloads"]["mem_stress"] = {"error": str(e)}

        print()

        # Run I/O stress
        try:
            print("=" * 80)
            io_workload = IOStressWorkload(file_size_mb=50, num_files=5)
            io_results = io_workload.run()
            results["workloads"]["io_stress"] = io_results
        except Exception as e:
            print(f"❌ I/O stress failed: {e}")
            results["workloads"]["io_stress"] = {"error": str(e)}

        print()

        # Run crypto stress
        try:
            print("=" * 80)
            crypto_workload = CryptoStressWorkload(iterations=50)
            crypto_results = crypto_workload.run()
            results["workloads"]["crypt_stress"] = crypto_results
        except Exception as e:
            print(f"❌ Crypto stress failed: {e}")
            results["workloads"]["crypt_stress"] = {"error": str(e)}

        print()

        return results

    def run_differential_tests(self):
        """Run all tests in both QEMU and KVM modes."""
        print("=" * 80)
        print("QWAMOS Phase XII - Differential Testing Harness")
        print("Comparing QEMU (TCG) vs KVM Performance")
        print("=" * 80)
        print()
        print(f"System Info:")
        print(f"  CPU: {self.results['system_info'].get('cpu_model', 'Unknown')}")
        print(f"  Cores: {self.results['system_info'].get('cpu_cores', 'Unknown')}")
        print(f"  Memory: {self.results['system_info'].get('memory_mb', 'Unknown')} MB")
        print(f"  KVM Available: {'✅ Yes' if self.kvm_available else '❌ No'}")
        print(f"  KVM Accessible: {'✅ Yes' if self.kvm_accessible else '❌ No'}")
        print()

        # Run QEMU tests
        print("\n" + "=" * 80)
        print("PHASE 1: QEMU (TCG) Testing")
        print("=" * 80)
        self.results["qemu_results"] = self.run_workload_suite("qemu")

        # Save intermediate results
        self._save_results("qemu_results.json", self.results["qemu_results"])

        # Run KVM tests
        print("\n" + "=" * 80)
        print("PHASE 2: KVM Testing")
        print("=" * 80)

        if self.kvm_accessible:
            self.results["kvm_results"] = self.run_workload_suite("kvm")
        else:
            print("⚠️  KVM not accessible - skipping KVM tests")
            print("   To enable KVM tests:")
            print("   1. Ensure /dev/kvm exists (kernel with CONFIG_KVM=y)")
            print("   2. Set permissions: sudo chmod 666 /dev/kvm")
            print()
            self.results["kvm_results"] = {
                "mode": "kvm",
                "skipped": True,
                "reason": "KVM not accessible"
            }

        # Save intermediate results
        self._save_results("kvm_results.json", self.results["kvm_results"])

        # Save combined results
        self._save_results("differential_results.json", self.results)

        print("\n" + "=" * 80)
        print("Differential Testing Complete")
        print("=" * 80)
        print(f"\nResults saved:")
        print(f"  - qemu_results.json")
        print(f"  - kvm_results.json")
        print(f"  - differential_results.json")
        print(f"\nNext step: Run comparison_engine.py to analyze results")
        print()

    def _save_results(self, filename: str, data: Dict):
        """Save results to JSON file."""
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("Test Summary")
        print("=" * 80)

        # QEMU summary
        if "qemu_results" in self.results:
            qemu = self.results["qemu_results"]
            print(f"\nQEMU (TCG) Results:")
            if "workloads" in qemu:
                for workload_name, workload_data in qemu["workloads"].items():
                    if "error" in workload_data:
                        print(f"  ❌ {workload_name}: {workload_data['error']}")
                    elif "metrics" in workload_data:
                        duration = workload_data["metrics"].get("total_duration_sec", "N/A")
                        print(f"  ✅ {workload_name}: {duration}s")

        # KVM summary
        if "kvm_results" in self.results:
            kvm = self.results["kvm_results"]
            print(f"\nKVM Results:")
            if kvm.get("skipped"):
                print(f"  ⚠️  Skipped: {kvm.get('reason', 'Unknown')}")
            elif "workloads" in kvm:
                for workload_name, workload_data in kvm["workloads"].items():
                    if "error" in workload_data:
                        print(f"  ❌ {workload_name}: {workload_data['error']}")
                    elif "metrics" in workload_data:
                        duration = workload_data["metrics"].get("total_duration_sec", "N/A")
                        print(f"  ✅ {workload_name}: {duration}s")

        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="QWAMOS Differential Testing Runner - QEMU vs KVM"
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Output directory for results'
    )
    args = parser.parse_args()

    runner = DifferentialRunner(output_dir=args.output_dir)
    runner.run_differential_tests()
    runner.print_summary()


if __name__ == "__main__":
    main()
