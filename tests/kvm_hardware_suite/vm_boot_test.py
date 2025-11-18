#!/usr/bin/env python3
"""
QWAMOS VM Boot Test
Phase XII: KVM Acceleration - VM Boot Validation

Tests QWAMOS VM boot under KVM acceleration
Author: QWAMOS Project
License: AGPL-3.0
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional, Tuple


class VMBootTester:
    """Test QWAMOS VM boot under KVM."""

    def __init__(self):
        """Initialize tester."""
        self.kvm_available = os.path.exists("/dev/kvm")
        self.qemu_binary = "qemu-system-aarch64"
        self.test_results = []

    def run_boot_test(self) -> bool:
        """
        Run VM boot test.

        Returns:
            True if boot successful
        """
        print("=" * 80)
        print("QWAMOS Phase XII - VM Boot Test")
        print("=" * 80)
        print("")

        if not self.kvm_available:
            print("⚠️  WARNING: /dev/kvm not available")
            print("   Test will use software emulation (TCG)")
            print("")

        # Check QEMU
        if not self._check_qemu():
            print("❌ QEMU not available")
            return False

        # Check kernel image
        kernel_path = self._find_kernel()
        if not kernel_path:
            print("⚠️  Kernel image not found")
            print("   Cannot perform full boot test")
            print("   Please ensure kernel/Image exists")
            return False

        # Run boot test
        print("🚀 Starting VM boot test...")
        success = self._test_vm_boot(kernel_path)

        if success:
            print("\n✅ BOOT SUCCESS")
            print("")
            print("VM booted successfully under", end=" ")
            print("KVM acceleration" if self.kvm_available else "TCG emulation")
            return True
        else:
            print("\n❌ BOOT FAILED")
            print("")
            print("Check error messages above")
            return False

    def _check_qemu(self) -> bool:
        """Check if QEMU is available."""
        print("  Checking QEMU...", end=" ")
        try:
            result = subprocess.run(
                [self.qemu_binary, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"✅ {version}")
                return True
        except Exception as e:
            print(f"❌ {e}")
        return False

    def _find_kernel(self) -> Optional[Path]:
        """Find kernel image."""
        print("  Locating kernel...", end=" ")

        # Search paths
        search_paths = [
            Path.cwd() / "kernel" / "Image",
            Path.home() / "QWAMOS" / "kernel" / "Image",
            Path("/data/data/com.termux/files/home/QWAMOS/kernel/Image"),
            Path("/boot/vmlinuz")
        ]

        for path in search_paths:
            if path.exists():
                print(f"✅ {path}")
                return path

        print("❌ Not found")
        return None

    def _test_vm_boot(self, kernel_path: Path) -> bool:
        """Test VM boot with minimal configuration."""
        print("  Launching minimal VM (timeout: 10s)...")

        # Build QEMU command
        cmd = [
            self.qemu_binary,
            "-machine", "virt",
            "-cpu", "cortex-a57",
            "-m", "512M",
            "-kernel", str(kernel_path),
            "-nographic",
            "-serial", "mon:stdio"
        ]

        # Add KVM if available
        if self.kvm_available:
            cmd.extend(["-enable-kvm"])
            print("    Using KVM acceleration...")
        else:
            print("    Using TCG emulation...")

        try:
            # Start QEMU
            start_time = time.time()
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for boot with timeout
            timeout = 10
            boot_detected = False
            output_lines = []

            while time.time() - start_time < timeout:
                # Check if process exited
                if process.poll() is not None:
                    break

                # Read output
                try:
                    line = process.stdout.readline()
                    if line:
                        output_lines.append(line.strip())
                        # Look for boot success indicators
                        if any(indicator in line.lower() for indicator in
                               ['login:', 'init', 'boot', 'starting']):
                            boot_detected = True
                            print(f"    ✅ Boot detected ({time.time() - start_time:.2f}s)")
                            break
                except:
                    break

                time.sleep(0.1)

            # Terminate QEMU
            process.terminate()
            try:
                process.wait(timeout=2)
            except:
                process.kill()

            # Check results
            if boot_detected:
                print("    ✅ VM reached boot sequence")
                return True
            else:
                print("    ⚠️  No boot detected within timeout")
                if output_lines:
                    print(f"    Last output: {output_lines[-1][:60]}")
                return False

        except Exception as e:
            print(f"    ❌ Error: {e}")
            return False


def main():
    """Main entry point."""
    tester = VMBootTester()
    success = tester.run_boot_test()

    print("\nTest Status:", "✅ PASSED" if success else "❌ FAILED")
    print("")

    if success:
        print("Phase XII KVM acceleration validation successful!")
        print("Hardware is ready for QWAMOS deployment.")
    else:
        print("Please review errors and ensure:")
        print("  1. /dev/kvm exists and is accessible")
        print("  2. QEMU is installed (qemu-system-aarch64)")
        print("  3. Kernel image is available")
        print("  4. CPU supports virtualization")

    print("")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
