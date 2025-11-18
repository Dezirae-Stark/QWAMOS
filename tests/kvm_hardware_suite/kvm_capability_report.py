#!/usr/bin/env python3
"""
QWAMOS KVM Capability Report Generator
Phase XII: KVM Acceleration - Hardware Capability Analysis

Generates comprehensive JSON report of device KVM capabilities
Author: QWAMOS Project
License: AGPL-3.0
"""

import os
import re
import json
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class KVMCapabilityAnalyzer:
    """Analyzes device KVM capabilities and generates report."""

    def __init__(self):
        """Initialize analyzer."""
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "test_suite_version": "1.0.0",
            "device_info": {},
            "kernel_info": {},
            "kvm_support": {},
            "cpu_capabilities": {},
            "performance_estimate": {},
            "security_notes": [],
            "recommendations": []
        }

    def run(self) -> Dict[str, Any]:
        """
        Run full capability analysis.

        Returns:
            Complete capability report
        """
        print("🔍 Analyzing KVM Capabilities...")
        print("")

        self.analyze_device_info()
        self.analyze_kernel()
        self.analyze_kvm_support()
        self.analyze_cpu_capabilities()
        self.estimate_performance()
        self.generate_security_notes()
        self.generate_recommendations()

        return self.report

    def analyze_device_info(self):
        """Collect device information."""
        print("  📱 Collecting device info...")

        try:
            # Basic system info
            self.report["device_info"] = {
                "hostname": platform.node(),
                "architecture": platform.machine(),
                "processor": platform.processor() or self._get_cpu_model(),
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release()
            }

            # Try to get device model
            device_model = self._get_device_model()
            if device_model:
                self.report["device_info"]["model"] = device_model

            # CPU count
            try:
                import multiprocessing
                self.report["device_info"]["cpu_cores"] = multiprocessing.cpu_count()
            except:
                self.report["device_info"]["cpu_cores"] = self._get_cpu_count()

            # Memory info
            memory_info = self._get_memory_info()
            if memory_info:
                self.report["device_info"]["memory_mb"] = memory_info

        except Exception as e:
            print(f"    ⚠️  Warning: {e}")

    def analyze_kernel(self):
        """Analyze kernel version and configuration."""
        print("  🐧 Analyzing kernel...")

        try:
            uname = platform.uname()
            self.report["kernel_info"] = {
                "version": uname.release,
                "version_full": uname.version,
                "build_date": self._extract_build_date(uname.version)
            }

            # Check kernel config
            kvm_config = self._check_kernel_config()
            if kvm_config:
                self.report["kernel_info"]["kvm_config"] = kvm_config

            # Check loaded modules
            modules = self._get_loaded_modules()
            if modules:
                self.report["kernel_info"]["kvm_modules"] = modules

        except Exception as e:
            print(f"    ⚠️  Warning: {e}")

    def analyze_kvm_support(self):
        """Check KVM device and support."""
        print("  ⚡ Checking KVM support...")

        kvm_info = {
            "kvm_device_exists": False,
            "kvm_device_accessible": False,
            "kvm_module_loaded": False,
            "virtualization_extensions": False
        }

        # Check /dev/kvm
        if os.path.exists("/dev/kvm"):
            kvm_info["kvm_device_exists"] = True
            kvm_info["kvm_device_path"] = "/dev/kvm"

            # Check permissions
            if os.access("/dev/kvm", os.R_OK | os.W_OK):
                kvm_info["kvm_device_accessible"] = True
            else:
                kvm_info["permission_issue"] = "Cannot read/write /dev/kvm"

        # Check if KVM module is loaded
        try:
            result = subprocess.run(
                ["lsmod"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "kvm" in result.stdout.lower():
                kvm_info["kvm_module_loaded"] = True
        except:
            pass

        # Check virtualization in dmesg
        try:
            result = subprocess.run(
                ["dmesg"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                dmesg_kvm = []
                for line in result.stdout.split('\n'):
                    if 'kvm' in line.lower() or 'virt' in line.lower():
                        dmesg_kvm.append(line.strip())
                if dmesg_kvm:
                    kvm_info["dmesg_kvm_mentions"] = dmesg_kvm[:10]  # First 10 lines
        except:
            pass

        self.report["kvm_support"] = kvm_info

    def analyze_cpu_capabilities(self):
        """Analyze CPU virtualization capabilities."""
        print("  💻 Analyzing CPU capabilities...")

        cpu_caps = {
            "virtualization_flags": [],
            "supports_kvm": False,
            "cpu_features": []
        }

        # Read /proc/cpuinfo
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()

            # Look for virtualization flags
            virt_flags = []
            for line in cpuinfo.split('\n'):
                if 'features' in line.lower() or 'flags' in line.lower():
                    if any(flag in line.lower() for flag in ['virt', 'hyp', 'kvm']):
                        # Extract individual flags
                        flags_match = re.search(r':\s*(.+)', line)
                        if flags_match:
                            all_flags = flags_match.group(1).split()
                            virt_related = [f for f in all_flags if any(v in f.lower() for v in ['virt', 'hyp', 'kvm', 've'])]
                            virt_flags.extend(virt_related)

            if virt_flags:
                cpu_caps["virtualization_flags"] = list(set(virt_flags))
                cpu_caps["supports_kvm"] = True

            # Get all CPU features
            all_features = set()
            for line in cpuinfo.split('\n'):
                if 'features' in line.lower() or 'flags' in line.lower():
                    flags_match = re.search(r':\s*(.+)', line)
                    if flags_match:
                        all_features.update(flags_match.group(1).split())

            # Filter interesting features
            interesting = ['aes', 'sha', 'crc', 'neon', 'asimd', 'pmull', 'sha2']
            cpu_caps["cpu_features"] = [f for f in all_features if any(i in f.lower() for i in interesting)]

        except Exception as e:
            print(f"    ⚠️  Warning: {e}")

        self.report["cpu_capabilities"] = cpu_caps

    def estimate_performance(self):
        """Estimate expected KVM performance."""
        print("  📊 Estimating performance...")

        perf = {
            "kvm_available": self.report["kvm_support"].get("kvm_device_exists", False),
            "expected_performance_level": "unknown",
            "expected_speedup_vs_tcg": "unknown",
            "vm_boot_time_estimate": "unknown",
            "recommended_vm_count": 0
        }

        if perf["kvm_available"]:
            # Estimate based on CPU cores
            cores = self.report["device_info"].get("cpu_cores", 0)
            memory_mb = self.report["device_info"].get("memory_mb", 0)

            if cores >= 8 and memory_mb >= 16000:
                perf["expected_performance_level"] = "excellent"
                perf["expected_speedup_vs_tcg"] = "10-15x"
                perf["vm_boot_time_estimate"] = "<2 seconds"
                perf["recommended_vm_count"] = min(cores // 2, 6)
            elif cores >= 4 and memory_mb >= 8000:
                perf["expected_performance_level"] = "good"
                perf["expected_speedup_vs_tcg"] = "8-12x"
                perf["vm_boot_time_estimate"] = "2-4 seconds"
                perf["recommended_vm_count"] = min(cores // 2, 4)
            elif cores >= 2 and memory_mb >= 4000:
                perf["expected_performance_level"] = "acceptable"
                perf["expected_speedup_vs_tcg"] = "5-8x"
                perf["vm_boot_time_estimate"] = "4-8 seconds"
                perf["recommended_vm_count"] = 2
            else:
                perf["expected_performance_level"] = "limited"
                perf["expected_speedup_vs_tcg"] = "3-5x"
                perf["vm_boot_time_estimate"] = ">8 seconds"
                perf["recommended_vm_count"] = 1

            # CPU efficiency estimate
            if "sha" in str(self.report["cpu_capabilities"].get("cpu_features", [])).lower():
                perf["crypto_acceleration"] = "SHA hardware support detected"

        else:
            perf["expected_performance_level"] = "tcg_only"
            perf["expected_speedup_vs_tcg"] = "1x (software emulation)"
            perf["vm_boot_time_estimate"] = ">30 seconds"
            perf["recommended_vm_count"] = 1

        self.report["performance_estimate"] = perf

    def generate_security_notes(self):
        """Generate security-related notes."""
        print("  🔒 Generating security notes...")

        notes = []

        # KVM device permissions
        if self.report["kvm_support"].get("kvm_device_exists"):
            if not self.report["kvm_support"].get("kvm_device_accessible"):
                notes.append({
                    "severity": "high",
                    "issue": "KVM device not accessible",
                    "recommendation": "Run: sudo chmod 666 /dev/kvm (or add user to kvm group)"
                })

        # SELinux/AppArmor check
        if self._check_selinux_enforcing():
            notes.append({
                "severity": "medium",
                "issue": "SELinux is in enforcing mode",
                "recommendation": "May need to configure SELinux policy for KVM access"
            })

        # Kernel version check
        kernel_version = self.report["kernel_info"].get("version", "")
        if kernel_version:
            major, minor = self._parse_kernel_version(kernel_version)
            if major < 5:
                notes.append({
                    "severity": "high",
                    "issue": f"Old kernel version: {kernel_version}",
                    "recommendation": "Upgrade to kernel 5.0+ for best KVM support"
                })

        # Memory warning
        memory_mb = self.report["device_info"].get("memory_mb", 0)
        if memory_mb > 0 and memory_mb < 4000:
            notes.append({
                "severity": "medium",
                "issue": f"Limited memory: {memory_mb}MB",
                "recommendation": "QWAMOS multi-VM requires 4GB+ RAM"
            })

        self.report["security_notes"] = notes

    def generate_recommendations(self):
        """Generate actionable recommendations."""
        print("  💡 Generating recommendations...")

        recommendations = []

        # Based on KVM support
        if not self.report["kvm_support"].get("kvm_device_exists"):
            recommendations.append(
                "KVM device not found. Verify kernel was compiled with CONFIG_KVM=y and CONFIG_KVM_ARM=y"
            )
        elif not self.report["kvm_support"].get("kvm_device_accessible"):
            recommendations.append(
                "Grant KVM device access: sudo chmod 666 /dev/kvm (or usermod -aG kvm $USER)"
            )

        # Based on CPU capabilities
        if not self.report["cpu_capabilities"].get("supports_kvm"):
            recommendations.append(
                "CPU virtualization extensions not detected. Check BIOS/firmware settings or verify ARM CPU supports virtualization"
            )

        # Based on performance estimate
        perf_level = self.report["performance_estimate"].get("expected_performance_level")
        if perf_level == "limited" or perf_level == "tcg_only":
            recommendations.append(
                "Device has limited resources. Consider reducing VM count or using lightweight configuration"
            )

        # General recommendations
        if self.report["kvm_support"].get("kvm_device_exists"):
            recommendations.append(
                "Run kvm_perf_benchmark.py to measure actual KVM performance"
            )
            recommendations.append(
                "Run vm_boot_test.py to validate QWAMOS VM boot under KVM"
            )

        self.report["recommendations"] = recommendations

    # Helper methods

    def _get_cpu_model(self) -> str:
        """Get CPU model from /proc/cpuinfo."""
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line.lower() or "processor" in line.lower():
                        return line.split(':')[1].strip()
        except:
            pass
        return "Unknown"

    def _get_device_model(self) -> Optional[str]:
        """Try to get device model."""
        paths = [
            "/sys/devices/virtual/dmi/id/product_name",
            "/sys/firmware/devicetree/base/model",
            "/proc/device-tree/model"
        ]
        for path in paths:
            try:
                with open(path, "r") as f:
                    model = f.read().strip().replace('\x00', '')
                    if model:
                        return model
            except:
                continue
        return None

    def _get_cpu_count(self) -> int:
        """Get CPU count from /proc/cpuinfo."""
        try:
            with open("/proc/cpuinfo", "r") as f:
                return sum(1 for line in f if line.startswith("processor"))
        except:
            return 0

    def _get_memory_info(self) -> Optional[int]:
        """Get total memory in MB."""
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        return kb // 1024
        except:
            pass
        return None

    def _extract_build_date(self, version_string: str) -> Optional[str]:
        """Extract build date from version string."""
        match = re.search(r'(\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+\s+\w+\s+\d{4})', version_string)
        if match:
            return match.group(1)
        return None

    def _check_kernel_config(self) -> Optional[Dict[str, bool]]:
        """Check kernel configuration for KVM."""
        config_paths = ["/proc/config.gz", "/boot/config-" + platform.release()]
        config = {}

        for path in config_paths:
            try:
                if path.endswith(".gz"):
                    import gzip
                    with gzip.open(path, "rt") as f:
                        content = f.read()
                else:
                    with open(path, "r") as f:
                        content = f.read()

                for key in ["CONFIG_KVM", "CONFIG_KVM_ARM", "CONFIG_ARM64_VHE", "CONFIG_HAVE_KVM"]:
                    if f"{key}=y" in content:
                        config[key] = True
                    elif f"{key}=m" in content:
                        config[key] = "module"
                    else:
                        config[key] = False

                return config
            except:
                continue

        return None

    def _get_loaded_modules(self) -> Optional[List[str]]:
        """Get loaded KVM-related modules."""
        try:
            result = subprocess.run(
                ["lsmod"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                modules = []
                for line in result.stdout.split('\n'):
                    if 'kvm' in line.lower():
                        modules.append(line.split()[0])
                return modules if modules else None
        except:
            pass
        return None

    def _check_selinux_enforcing(self) -> bool:
        """Check if SELinux is enforcing."""
        try:
            result = subprocess.run(
                ["getenforce"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.stdout.strip().lower() == "enforcing"
        except:
            return False

    def _parse_kernel_version(self, version: str) -> tuple:
        """Parse kernel version string."""
        match = re.match(r'(\d+)\.(\d+)', version)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 0, 0


def main():
    """Main entry point."""
    print("=" * 80)
    print("QWAMOS Phase XII - KVM Capability Report")
    print("=" * 80)
    print("")

    analyzer = KVMCapabilityAnalyzer()
    report = analyzer.run()

    print("")
    print("=" * 80)
    print("Report Generated Successfully")
    print("=" * 80)
    print("")

    # Save to JSON
    output_file = Path("kvm_capability_report.json")
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Full report saved to: {output_file}")
    print("")

    # Print summary
    print("📋 Summary:")
    print(f"  Device: {report['device_info'].get('model', 'Unknown')}")
    print(f"  Kernel: {report['kernel_info'].get('version', 'Unknown')}")
    print(f"  KVM Available: {'✅ Yes' if report['kvm_support'].get('kvm_device_exists') else '❌ No'}")
    print(f"  CPU Virtualization: {'✅ Yes' if report['cpu_capabilities'].get('supports_kvm') else '❌ No'}")
    print(f"  Expected Performance: {report['performance_estimate'].get('expected_performance_level', 'Unknown')}")
    print("")

    if report["recommendations"]:
        print("💡 Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")
        print("")

    if report["security_notes"]:
        print("🔒 Security Notes:")
        for note in report["security_notes"]:
            severity = note.get("severity", "info").upper()
            print(f"  [{severity}] {note.get('issue')}")
            print(f"          → {note.get('recommendation')}")
        print("")

    print("Next steps:")
    print("  1. Review kvm_capability_report.json")
    print("  2. Run: python3 kvm_perf_benchmark.py")
    print("  3. Run: python3 vm_boot_test.py")
    print("")


if __name__ == "__main__":
    main()
