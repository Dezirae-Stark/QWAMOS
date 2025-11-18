#!/usr/bin/env python3
"""
QWAMOS Differential Testing - Memory Stress Workload
Phase XII: KVM vs QEMU Comparison

Linear and random memory access patterns
Author: QWAMOS Project
License: AGPL-3.0
"""

import os
import sys
import time
import json
import random
from typing import Dict, List
from datetime import datetime


class MemoryStressWorkload:
    """Memory-intensive workload with linear and random access patterns."""

    def __init__(self, size_mb: int = 256, pattern: str = "mixed"):
        """
        Initialize memory stress test.

        Args:
            size_mb: Memory buffer size in MB
            pattern: Access pattern ('linear', 'random', 'mixed')
        """
        self.size_mb = size_mb
        self.pattern = pattern
        self.size_bytes = size_mb * 1024 * 1024
        self.results = {
            "workload": "memory_stress",
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "size_mb": size_mb,
                "pattern": pattern
            },
            "metrics": {},
            "errors": []
        }

    def test_linear_write(self) -> Dict:
        """Test linear memory write."""
        print(f"   Testing linear write ({self.size_mb} MB)...", end=" ", flush=True)

        start = time.time()
        try:
            # Allocate buffer
            buffer = bytearray(self.size_bytes)

            # Linear write pattern
            for i in range(self.size_bytes):
                buffer[i] = i % 256

            duration = time.time() - start
            throughput = self.size_mb / duration

            # Verify integrity
            errors = sum(1 for i in range(self.size_bytes) if buffer[i] != i % 256)

            print(f"{duration:.3f}s ({throughput:.2f} MB/s)")

            return {
                "test": "linear_write",
                "duration_sec": round(duration, 3),
                "throughput_mb_per_sec": round(throughput, 2),
                "integrity_errors": errors
            }
        except Exception as e:
            print(f"❌ {e}")
            self.results["errors"].append({"test": "linear_write", "error": str(e)})
            return {
                "test": "linear_write",
                "error": str(e)
            }

    def test_linear_read(self) -> Dict:
        """Test linear memory read."""
        print(f"   Testing linear read ({self.size_mb} MB)...", end=" ", flush=True)

        start = time.time()
        try:
            # Allocate and initialize buffer
            buffer = bytearray(i % 256 for i in range(self.size_bytes))

            # Linear read pattern
            checksum = 0
            for i in range(self.size_bytes):
                checksum += buffer[i]

            duration = time.time() - start
            throughput = self.size_mb / duration

            # Expected checksum
            expected_checksum = sum(i % 256 for i in range(self.size_bytes))
            integrity_ok = (checksum == expected_checksum)

            print(f"{duration:.3f}s ({throughput:.2f} MB/s)")

            return {
                "test": "linear_read",
                "duration_sec": round(duration, 3),
                "throughput_mb_per_sec": round(throughput, 2),
                "checksum_valid": integrity_ok
            }
        except Exception as e:
            print(f"❌ {e}")
            self.results["errors"].append({"test": "linear_read", "error": str(e)})
            return {
                "test": "linear_read",
                "error": str(e)
            }

    def test_random_access(self, operations: int = 1000000) -> Dict:
        """Test random memory access."""
        print(f"   Testing random access ({operations:,} ops)...", end=" ", flush=True)

        start = time.time()
        try:
            # Allocate buffer
            buffer = bytearray(self.size_bytes)

            # Initialize with random data
            for i in range(0, self.size_bytes, 4096):
                chunk_size = min(4096, self.size_bytes - i)
                buffer[i:i+chunk_size] = os.urandom(chunk_size)

            # Random access pattern
            read_count = 0
            write_count = 0

            for _ in range(operations):
                idx = random.randint(0, self.size_bytes - 1)

                if random.random() < 0.5:
                    # Read
                    _ = buffer[idx]
                    read_count += 1
                else:
                    # Write
                    buffer[idx] = random.randint(0, 255)
                    write_count += 1

            duration = time.time() - start
            ops_per_sec = operations / duration

            print(f"{duration:.3f}s ({ops_per_sec:.0f} ops/s)")

            return {
                "test": "random_access",
                "duration_sec": round(duration, 3),
                "operations": operations,
                "ops_per_sec": int(ops_per_sec),
                "read_count": read_count,
                "write_count": write_count
            }
        except Exception as e:
            print(f"❌ {e}")
            self.results["errors"].append({"test": "random_access", "error": str(e)})
            return {
                "test": "random_access",
                "error": str(e)
            }

    def test_strided_access(self, stride: int = 64) -> Dict:
        """Test strided memory access (cache-line simulation)."""
        print(f"   Testing strided access (stride={stride})...", end=" ", flush=True)

        start = time.time()
        try:
            # Allocate buffer
            buffer = bytearray(self.size_bytes)

            # Strided write pattern
            for i in range(0, self.size_bytes, stride):
                buffer[i] = (i // stride) % 256

            # Strided read and verify
            errors = 0
            accesses = 0
            for i in range(0, self.size_bytes, stride):
                if buffer[i] != (i // stride) % 256:
                    errors += 1
                accesses += 1

            duration = time.time() - start
            accesses_per_sec = accesses / duration

            print(f"{duration:.3f}s ({accesses_per_sec:.0f} accesses/s)")

            return {
                "test": "strided_access",
                "duration_sec": round(duration, 3),
                "stride": stride,
                "total_accesses": accesses,
                "accesses_per_sec": int(accesses_per_sec),
                "integrity_errors": errors
            }
        except Exception as e:
            print(f"❌ {e}")
            self.results["errors"].append({"test": "strided_access", "error": str(e)})
            return {
                "test": "strided_access",
                "error": str(e)
            }

    def run(self) -> Dict:
        """
        Execute memory stress test.

        Returns:
            Results dictionary
        """
        print(f"💾 Memory Stress Test - {self.size_mb} MB, pattern: {self.pattern}")

        overall_start = time.time()
        test_results = []

        # Run tests based on pattern
        if self.pattern in ["linear", "mixed"]:
            test_results.append(self.test_linear_write())
            test_results.append(self.test_linear_read())

        if self.pattern in ["random", "mixed"]:
            test_results.append(self.test_random_access())

        if self.pattern in ["mixed"]:
            test_results.append(self.test_strided_access(stride=64))
            test_results.append(self.test_strided_access(stride=4096))

        overall_duration = time.time() - overall_start

        # Calculate aggregate metrics
        self.results["metrics"] = {
            "total_duration_sec": round(overall_duration, 3),
            "tests_completed": len([t for t in test_results if "error" not in t]),
            "tests_failed": len([t for t in test_results if "error" in t]),
            "test_details": test_results
        }

        # Print summary
        print(f"   ✅ Completed in {overall_duration:.3f}s")
        print(f"   Tests passed: {self.results['metrics']['tests_completed']}/{len(test_results)}")

        if self.results["metrics"]["tests_failed"] > 0:
            print(f"   ⚠️  Tests failed: {self.results['metrics']['tests_failed']}")

        return self.results

    def save_results(self, output_path: str):
        """Save results to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="QWAMOS Memory Stress Workload")
    parser.add_argument('--size', type=int, default=256, help='Buffer size in MB')
    parser.add_argument('--pattern', type=str, default='mixed',
                       choices=['linear', 'random', 'mixed'],
                       help='Access pattern')
    parser.add_argument('--output', type=str, default='mem_stress_results.json', help='Output file')
    args = parser.parse_args()

    workload = MemoryStressWorkload(size_mb=args.size, pattern=args.pattern)
    results = workload.run()
    workload.save_results(args.output)

    print(f"\n✅ Results saved to: {args.output}")

    # Return non-zero exit code if errors occurred
    sys.exit(1 if results["metrics"]["tests_failed"] > 0 else 0)


if __name__ == "__main__":
    main()
