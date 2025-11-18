# QWAMOS Phase XII - Device Validation Instructions

## Overview

This document provides step-by-step instructions for validating KVM support on real ARM hardware using the QWAMOS KVM Hardware Test Suite.

---

## Prerequisites

### Required Tools
- `adb` (Android Debug Bridge) - for transferring files
- SSH access or Termux on the device
- Python 3.6+ installed on device
- Bash shell

### Device Requirements
- ARM64 architecture
- Root access (for /dev/kvm permissions)
- 2GB+ free RAM
- 500MB+ free storage

---

## Method 1: Using ADB (Recommended)

### Step 1: Prepare Test Suite

On your computer:

```bash
# Navigate to QWAMOS repository
cd /path/to/QWAMOS

# Verify test suite exists
ls tests/kvm_hardware_suite/
```

### Step 2: Transfer to Device

```bash
# Push test suite to device
adb push tests/kvm_hardware_suite/ /data/local/tmp/qwamos_kvm_test/

# Verify transfer
adb shell ls /data/local/tmp/qwamos_kvm_test/
```

### Step 3: Connect to Device

```bash
# Connect via ADB shell
adb shell

# Navigate to test directory
cd /data/local/tmp/qwamos_kvm_test/
```

### Step 4: Set Permissions

```bash
# Make scripts executable
chmod +x kvm_hardware_check.sh
chmod +x *.py

# Grant KVM device access (requires root)
su
chmod 666 /dev/kvm
exit
```

### Step 5: Run Tests

```bash
# Test 1: Hardware Check (5 minutes)
./kvm_hardware_check.sh

# Test 2: Capability Report (2 minutes)
python3 kvm_capability_report.py

# Test 3: Performance Benchmark (10 minutes)
python3 kvm_perf_benchmark.py

# Test 4: VM Boot Test (2 minutes)
python3 vm_boot_test.py
```

### Step 6: Collect Results

```bash
# List generated files
ls -lh *.json *.md

# Pull results back to computer
exit  # Exit adb shell

adb pull /data/local/tmp/qwamos_kvm_test/kvm_capability_report.json .
adb pull /data/local/tmp/qwamos_kvm_test/kvm_perf_benchmark_results.json .
adb pull /data/local/tmp/qwamos_kvm_test/kvm_perf_benchmark_report.md .
```

---

## Method 2: Using Termux (On-Device)

### Step 1: Install Termux

Install Termux from F-Droid (recommended) or Google Play.

### Step 2: Install Dependencies

```bash
# Update packages
pkg update && pkg upgrade

# Install required packages
pkg install python git

# Clone QWAMOS repository
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS/tests/kvm_hardware_suite/
```

### Step 3: Run Tests

```bash
# Make scripts executable
chmod +x kvm_hardware_check.sh

# Run all tests
./kvm_hardware_check.sh
python kvm_capability_report.py
python kvm_perf_benchmark.py
python vm_boot_test.py
```

### Step 4: View Results

```bash
# View JSON reports
cat kvm_capability_report.json
cat kvm_perf_benchmark_results.json

# View markdown report
cat kvm_perf_benchmark_report.md
```

---

## Method 3: SSH Access

If you have SSH access to your device:

```bash
# SSH into device
ssh user@device-ip

# Create test directory
mkdir -p ~/qwamos_kvm_test
cd ~/qwamos_kvm_test

# Transfer files (from another terminal on your computer)
scp -r tests/kvm_hardware_suite/* user@device-ip:~/qwamos_kvm_test/

# Run tests (on device via SSH)
chmod +x kvm_hardware_check.sh
./kvm_hardware_check.sh
python3 kvm_capability_report.py
python3 kvm_perf_benchmark.py
python3 vm_boot_test.py

# Download results (from computer)
scp user@device-ip:~/qwamos_kvm_test/*.json .
scp user@device-ip:~/qwamos_kvm_test/*.md .
```

---

## Interpreting Results

### Test 1: kvm_hardware_check.sh

**Expected Output:**
```
✅ ALL TESTS PASSED
This device appears to support KVM acceleration!
```

**If Failed:**
- Check which specific tests failed
- Review recommendations in output
- Verify /dev/kvm permissions
- Check kernel configuration

### Test 2: kvm_capability_report.py

**Key Fields to Check:**

```json
{
  "kvm_support": {
    "kvm_device_exists": true,  // Must be true
    "kvm_device_accessible": true  // Must be true
  },
  "cpu_capabilities": {
    "supports_kvm": true  // Must be true
  },
  "performance_estimate": {
    "expected_performance_level": "good",  // good/excellent preferred
    "expected_speedup_vs_tcg": "8-12x"  // 8x+ is good
  }
}
```

### Test 3: kvm_perf_benchmark.py

**Benchmark Targets:**

| Metric | Target | Meaning |
|--------|--------|---------|
| CPU Rating | Good+ | Acceptable performance |
| Memory Throughput | >200 MB/s | Sufficient for VMs |
| Crypto (BLAKE2b) | >100 MB/s | Good crypto performance |

### Test 4: vm_boot_test.py

**Expected Output:**
```
✅ BOOT SUCCESS
VM booted successfully under KVM acceleration
```

If boot fails, check:
- Kernel image location
- QEMU installation
- /dev/kvm accessibility

---

## Troubleshooting

### Problem: /dev/kvm not found

**Solution:**
```bash
# Check if KVM module is loaded
lsmod | grep kvm

# Try loading KVM module (if available)
sudo modprobe kvm
sudo modprobe kvm-arm

# If still not working, kernel may not support KVM
# Need custom kernel with CONFIG_KVM=y
```

### Problem: Permission denied on /dev/kvm

**Solution:**
```bash
# Option 1: Temporary fix
sudo chmod 666 /dev/kvm

# Option 2: Add user to kvm group (permanent)
sudo usermod -aG kvm $USER
# Log out and back in
```

### Problem: Python not found

**Solution:**
```bash
# Install Python 3
pkg install python  # Termux
apt install python3  # Debian/Ubuntu
```

### Problem: QEMU not found

**Solution:**
```bash
# Install QEMU
pkg install qemu-system-aarch64  # Termux
apt install qemu-system-arm  # Debian/Ubuntu
```

---

## Reporting Results

### To QWAMOS Maintainers

After running all tests, send the following files:

1. `kvm_hardware_check.sh` output (copy terminal output)
2. `kvm_capability_report.json`
3. `kvm_perf_benchmark_results.json`
4. `kvm_perf_benchmark_report.md`
5. Device information:
   - Device model
   - Kernel version (`uname -a`)
   - Android version
   - ROM/OS details

**Send to:** dezirae@firststirling.capital

**Subject:** QWAMOS Phase XII - KVM Validation Results - [Device Model]

---

## Next Steps

### If KVM Works ✅
1. Proceed with full QWAMOS deployment
2. Configure VMs for optimal performance
3. Enable production features

### If KVM Doesn't Work ❌
1. Check if custom kernel is available for your device
2. Consider installing LineageOS or other custom ROM with KVM support
3. Use TCG fallback mode (limited performance)
4. Consider upgrading to KVM-capable device

---

## Support

For questions or issues:
- GitHub Issues: https://github.com/Dezirae-Stark/QWAMOS/issues
- Documentation: See `kvm_vs_tcg_comparison.md`
- Community: QWAMOS Discord/Matrix

---

**Last Updated:** 2025-11-18
**Test Suite Version:** 1.0.0
