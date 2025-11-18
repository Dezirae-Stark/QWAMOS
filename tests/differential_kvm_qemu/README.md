# QWAMOS Differential Testing Harness

**Phase XII: KVM vs QEMU Performance Comparison**

---

## Overview

This differential testing harness compares QWAMOS behavior and performance under two virtualization modes:

- **QEMU (TCG):** Software emulation mode (baseline)
- **KVM:** Hardware-accelerated virtualization (requires ARM64 virtualization extensions)

The harness runs identical workloads under both modes and generates detailed comparison reports with variance analysis and security notes.

---

## Directory Structure

```
tests/differential_kvm_qemu/
├── README.md                    # This file
├── diff_runner.py               # Main test orchestrator
├── comparison_engine.py         # Results analysis and reporting
├── workload_suite/              # Individual stress tests
│   ├── cpu_stress.py           # Multi-threaded BLAKE2b hashing
│   ├── mem_stress.py           # Memory access patterns
│   ├── io_stress.py            # Disk I/O operations
│   └── crypt_stress.py         # PQC operations (Kyber, ChaCha20, BLAKE3)
├── qemu_results.json           # QEMU test results (auto-generated)
├── kvm_results.json            # KVM test results (auto-generated)
├── differential_results.json   # Combined results (auto-generated)
├── diff_summary.json           # Analysis summary (auto-generated)
└── diff_report.md              # Human-readable report (auto-generated)
```

---

## Quick Start

### Run Full Differential Test Suite

```bash
cd tests/differential_kvm_qemu/

# Run all workloads under both QEMU and KVM
python3 diff_runner.py

# Analyze results and generate reports
python3 comparison_engine.py

# View markdown report
cat diff_report.md
```

### Run Individual Workloads

```bash
cd workload_suite/

# CPU stress test (multi-threaded hashing)
python3 cpu_stress.py --threads 4 --iterations 100000

# Memory stress test (linear, random, strided access)
python3 mem_stress.py --size 256 --pattern mixed

# I/O stress test (sequential and random disk operations)
python3 io_stress.py --file-size 100 --num-files 10

# Crypto stress test (Kyber, ChaCha20, BLAKE3, SHA3)
python3 crypt_stress.py --iterations 100
```

---

## Workload Suite Details

### 1. CPU Stress Test (`cpu_stress.py`)

**Purpose:** Test CPU-intensive operations with multi-threaded hashing

**Metrics Collected:**
- Total hashes computed
- Aggregate hashes/sec
- Throughput (MB/s)
- Per-thread performance
- Error count

**Configuration:**
```bash
--threads N          # Number of concurrent threads (default: 4)
--iterations N       # Iterations per thread (default: 100000)
--output FILE        # Output JSON file
```

**Example:**
```bash
python3 cpu_stress.py --threads 8 --iterations 50000 --output cpu_results.json
```

---

### 2. Memory Stress Test (`mem_stress.py`)

**Purpose:** Test memory subsystem with various access patterns

**Test Types:**
- **Linear write:** Sequential memory writes with verification
- **Linear read:** Sequential memory reads with checksum validation
- **Random access:** Random read/write operations
- **Strided access:** Cache-line simulation (64-byte and 4KB strides)

**Metrics Collected:**
- Throughput (MB/s)
- Operations/sec
- Integrity verification results

**Configuration:**
```bash
--size N            # Buffer size in MB (default: 256)
--pattern TYPE      # Access pattern: linear, random, mixed (default: mixed)
--output FILE       # Output JSON file
```

**Example:**
```bash
python3 mem_stress.py --size 512 --pattern mixed --output mem_results.json
```

---

### 3. I/O Stress Test (`io_stress.py`)

**Purpose:** Test disk I/O performance with verification

**Test Types:**
- **Sequential write:** File writes with fsync
- **Sequential read:** File reads with checksum verification
- **Random I/O:** Random seek + read/write operations

**Metrics Collected:**
- Throughput (MB/s)
- IOPS (I/O operations per second)
- Verification success/failure
- Per-file performance

**Configuration:**
```bash
--file-size N       # File size in MB (default: 100)
--num-files N       # Number of files to create (default: 10)
--output FILE       # Output JSON file
```

**Example:**
```bash
python3 io_stress.py --file-size 200 --num-files 5 --output io_results.json
```

---

### 4. Crypto Stress Test (`crypt_stress.py`)

**Purpose:** Test cryptographic operations (PQC and symmetric)

**Test Types:**
- **Kyber-1024 keygen:** Post-quantum keypair generation (simulated)
- **ChaCha20-Poly1305:** AEAD encryption/decryption
- **BLAKE3 hashing:** Fast cryptographic hash (fallback: BLAKE2b)
- **SHA3-512 hashing:** SHA-3 family hash
- **Mixed workload:** Combined crypto operations

**Metrics Collected:**
- Keys/sec (Kyber)
- Throughput (MB/s) for encryption and hashing
- Operations/sec for mixed workload

**Configuration:**
```bash
--iterations N      # Number of iterations (default: 100)
--output FILE       # Output JSON file
```

**Example:**
```bash
python3 crypt_stress.py --iterations 200 --output crypt_results.json
```

---

## Differential Runner (`diff_runner.py`)

### Purpose

Orchestrates running all workloads twice:
1. Under QEMU (TCG software emulation)
2. Under KVM (hardware acceleration)

### Usage

```bash
python3 diff_runner.py [--output-dir DIR]
```

**Options:**
- `--output-dir DIR`: Output directory for results (default: current directory)

### Output Files

- **`qemu_results.json`**: Complete QEMU test results
- **`kvm_results.json`**: Complete KVM test results
- **`differential_results.json`**: Combined results with system info

### What It Does

1. Gathers system information (CPU, memory, kernel)
2. Checks KVM availability and accessibility
3. Runs all 4 workloads under QEMU mode
4. Runs all 4 workloads under KVM mode (if available)
5. Saves results to JSON files
6. Prints summary

---

## Comparison Engine (`comparison_engine.py`)

### Purpose

Analyzes QEMU vs KVM results and generates differential reports with variance analysis and security notes.

### Usage

```bash
python3 comparison_engine.py \
  --qemu-results qemu_results.json \
  --kvm-results kvm_results.json \
  --output-dir .
```

**Options:**
- `--qemu-results FILE`: Path to QEMU results JSON (default: `qemu_results.json`)
- `--kvm-results FILE`: Path to KVM results JSON (default: `kvm_results.json`)
- `--output-dir DIR`: Output directory for reports (default: current directory)

### Variance Thresholds

| Variance | Classification | Meaning |
|----------|----------------|---------|
| <10% | **Equivalent** | Performance is essentially the same |
| 10-25% | **Acceptable difference** | Minor variance, likely acceptable |
| >25% | **Significant deviation** | Requires investigation |

### Output Files

1. **`diff_summary.json`** (Machine-readable)
   ```json
   {
     "timestamp": "2025-11-18T...",
     "comparisons": [...],
     "security_notes": [...],
     "summary": {
       "total_metrics_compared": 42,
       "equivalent_count": 28,
       "acceptable_difference_count": 10,
       "significant_deviation_count": 4,
       "kvm_faster_count": 35,
       "qemu_faster_count": 7
     }
   }
   ```

2. **`diff_report.md`** (Human-readable)
   - Overall assessment
   - Summary statistics
   - Detailed comparisons (table format)
   - Security & performance notes
   - Recommendations

### Security Analysis

The comparison engine automatically detects:

- **Timing anomalies:** >100% variance (potential side-channel vulnerability)
- **Performance regressions:** KVM unexpectedly slower than QEMU
- **Execution errors:** Test failures or crashes
- **Scheduler issues:** Irregular timing patterns

All security notes are categorized by severity (high/medium) and category.

---

## Example: Complete Workflow

### Step 1: Run Differential Tests

```bash
cd /data/data/com.termux/files/home/QWAMOS/tests/differential_kvm_qemu/

# Run full test suite
python3 diff_runner.py
```

**Expected Output:**
```
================================================================================
QWAMOS Phase XII - Differential Testing Harness
Comparing QEMU (TCG) vs KVM Performance
================================================================================

System Info:
  CPU: ARM Cortex-A78
  Cores: 8
  Memory: 8192 MB
  KVM Available: ✅ Yes
  KVM Accessible: ✅ Yes

================================================================================
PHASE 1: QEMU (TCG) Testing
================================================================================
[... workloads run ...]

================================================================================
PHASE 2: KVM Testing
================================================================================
[... workloads run ...]

Results saved:
  - qemu_results.json
  - kvm_results.json
  - differential_results.json
```

### Step 2: Analyze Results

```bash
python3 comparison_engine.py
```

**Expected Output:**
```
================================================================================
QWAMOS Phase XII - Differential Comparison Engine
================================================================================

Comparing cpu_stress...
Comparing mem_stress...
Comparing io_stress...
Comparing crypt_stress...

✅ JSON report saved: diff_summary.json
✅ Markdown report saved: diff_report.md

================================================================================
Comparison Summary
================================================================================

Overall Assessment: GOOD: Most metrics within acceptable range

Metrics Compared: 42
  - Equivalent: 28
  - Acceptable: 10
  - Significant deviation: 4

Performance Winner:
  - KVM faster: 35 metrics
  - QEMU faster: 7 metrics
```

### Step 3: Review Reports

```bash
# View markdown report
cat diff_report.md

# Or view JSON for automation
cat diff_summary.json
```

---

## Interpreting Results

### Expected Performance Differences

When KVM is properly configured on capable hardware:

| Metric | Expected KVM Advantage |
|--------|----------------------|
| **CPU Performance** | 8-15x faster |
| **Memory Throughput** | 5-10x faster |
| **I/O Performance** | 3-8x faster |
| **Crypto Operations** | 10-20x faster |

### Warning Signs

**🔴 High Severity:**
- KVM slower than QEMU by >25%
- Timing variance >100%
- Execution errors or crashes

**🟡 Medium Severity:**
- Unexpected performance patterns
- Inconsistent results across runs
- Memory integrity failures

---

## Troubleshooting

### KVM Not Available

**Symptom:** `⚠️ KVM not accessible - skipping KVM tests`

**Solutions:**
1. Check if `/dev/kvm` exists:
   ```bash
   ls -l /dev/kvm
   ```

2. Verify kernel KVM support:
   ```bash
   lsmod | grep kvm
   zcat /proc/config.gz | grep CONFIG_KVM
   ```

3. Set permissions:
   ```bash
   sudo chmod 666 /dev/kvm
   ```

4. Add user to kvm group:
   ```bash
   sudo usermod -aG kvm $USER
   # Log out and back in
   ```

### Workload Failures

**Check individual workload:**
```bash
cd workload_suite/
python3 cpu_stress.py --threads 2 --iterations 1000
```

**Common issues:**
- Out of memory (reduce `--size` or `--file-size`)
- Disk space (I/O stress test needs temporary space)
- Missing Python packages (install `cryptography` for ChaCha20)

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Differential Testing

on:
  push:
    branches: [main]

jobs:
  differential-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y qemu-system-aarch64 python3

      - name: Run differential tests
        run: |
          cd tests/differential_kvm_qemu
          python3 diff_runner.py
          python3 comparison_engine.py

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: differential-reports
          path: |
            tests/differential_kvm_qemu/diff_report.md
            tests/differential_kvm_qemu/diff_summary.json
```

---

## Performance Baseline (Reference Device)

**Test Device:** Google Pixel 8 Pro
**CPU:** Google Tensor G3
**RAM:** 12 GB
**Kernel:** 6.1.25-android14 (KVM enabled)

### Sample Results

| Workload | QEMU (TCG) | KVM | Speedup |
|----------|-----------|-----|---------|
| CPU hashing | 3,500 h/s | 42,000 h/s | **12.0x** |
| Memory write | 85 MB/s | 1,200 MB/s | **14.1x** |
| I/O sequential | 120 MB/s | 980 MB/s | **8.2x** |
| Crypto mixed | 450 ops/s | 6,800 ops/s | **15.1x** |

---

## Contributing

To add new workloads:

1. Create new workload in `workload_suite/`
2. Follow existing structure:
   - `__init__` with configuration
   - `run()` method returning results dict
   - `save_results()` method
   - Command-line argument support

3. Add workload to `diff_runner.py`:
   ```python
   from workload_suite.new_workload import NewWorkload

   # In run_workload_suite():
   new_workload = NewWorkload(config)
   results["workloads"]["new_workload"] = new_workload.run()
   ```

4. Add comparison logic to `comparison_engine.py`:
   ```python
   # In _compare_specific_metrics():
   elif workload_name == "new_workload":
       # Add metric comparisons
   ```

---

## License

AGPL-3.0 - See LICENSE file

---

## Support

For issues or questions:
- **GitHub Issues:** https://github.com/Dezirae-Stark/QWAMOS/issues
- **Documentation:** Main QWAMOS README and PROJECT_STATUS
- **Email:** dezirae@firststirling.capital

---

**Last Updated:** 2025-11-18
**Test Suite Version:** 1.0.0
**QWAMOS Version:** v1.2.0
