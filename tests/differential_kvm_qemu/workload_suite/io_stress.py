#!/usr/bin/env python3
"""
QWAMOS Differential Testing - I/O Stress Workload
Phase XII: KVM vs QEMU Comparison

Simulated VM disk writes via PQC storage layer
Author: QWAMOS Project
License: AGPL-3.0
"""

import os
import sys
import time
import json
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class IOStressWorkload:
    """I/O-intensive workload simulating VM disk operations."""

    def __init__(self, file_size_mb: int = 100, num_files: int = 10):
        """
        Initialize I/O stress test.

        Args:
            file_size_mb: Size of each test file in MB
            num_files: Number of files to create
        """
        self.file_size_mb = file_size_mb
        self.num_files = num_files
        self.file_size_bytes = file_size_mb * 1024 * 1024
        self.temp_dir = None
        self.results = {
            "workload": "io_stress",
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "file_size_mb": file_size_mb,
                "num_files": num_files
            },
            "metrics": {},
            "errors": []
        }

    def setup_temp_directory(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp(prefix="qwamos_io_test_")
        print(f"   Test directory: {self.temp_dir}")

    def cleanup_temp_directory(self):
        """Remove temporary directory and test files."""
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir)

    def test_sequential_write(self) -> Dict:
        """Test sequential file writes with fsync."""
        print(f"   Testing sequential write ({self.num_files} files × {self.file_size_mb} MB)...")

        file_results = []
        total_bytes = 0
        total_duration = 0

        for i in range(self.num_files):
            file_path = Path(self.temp_dir) / f"test_write_{i}.bin"

            try:
                # Generate data
                data = os.urandom(self.file_size_bytes)

                # Write with fsync
                start = time.time()
                with open(file_path, 'wb') as f:
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
                duration = time.time() - start

                # Calculate checksum for verification
                checksum = hashlib.sha256(data).hexdigest()

                file_results.append({
                    "file": file_path.name,
                    "duration_sec": round(duration, 3),
                    "throughput_mb_per_sec": round(self.file_size_mb / duration, 2),
                    "checksum": checksum
                })

                total_bytes += self.file_size_bytes
                total_duration += duration

                print(f"      File {i+1}/{self.num_files}: {duration:.3f}s ({self.file_size_mb / duration:.2f} MB/s)")

            except Exception as e:
                self.results["errors"].append({
                    "test": "sequential_write",
                    "file": file_path.name,
                    "error": str(e)
                })
                print(f"      ❌ File {i+1}/{self.num_files}: {e}")

        avg_throughput = (total_bytes / (1024 * 1024)) / total_duration if total_duration > 0 else 0

        return {
            "test": "sequential_write",
            "total_duration_sec": round(total_duration, 3),
            "average_throughput_mb_per_sec": round(avg_throughput, 2),
            "files_written": len(file_results),
            "file_details": file_results
        }

    def test_sequential_read(self) -> Dict:
        """Test sequential file reads with verification."""
        print(f"   Testing sequential read ({self.num_files} files × {self.file_size_mb} MB)...")

        file_results = []
        total_bytes = 0
        total_duration = 0
        verification_failures = 0

        # Get checksums from write test
        write_checksums = {}
        if "test_details" in self.results.get("metrics", {}):
            for test in self.results["metrics"]["test_details"]:
                if test.get("test") == "sequential_write":
                    for file_detail in test.get("file_details", []):
                        write_checksums[file_detail["file"]] = file_detail["checksum"]

        for i in range(self.num_files):
            file_path = Path(self.temp_dir) / f"test_write_{i}.bin"

            try:
                if not file_path.exists():
                    continue

                # Read file
                start = time.time()
                with open(file_path, 'rb') as f:
                    data = f.read()
                duration = time.time() - start

                # Verify checksum
                checksum = hashlib.sha256(data).hexdigest()
                expected_checksum = write_checksums.get(file_path.name)
                checksum_valid = (checksum == expected_checksum) if expected_checksum else None

                if checksum_valid is False:
                    verification_failures += 1

                file_results.append({
                    "file": file_path.name,
                    "duration_sec": round(duration, 3),
                    "throughput_mb_per_sec": round(len(data) / (1024 * 1024) / duration, 2),
                    "checksum_valid": checksum_valid
                })

                total_bytes += len(data)
                total_duration += duration

                status = "✓" if checksum_valid is not False else "✗"
                print(f"      File {i+1}/{self.num_files}: {duration:.3f}s ({len(data) / (1024 * 1024) / duration:.2f} MB/s) {status}")

            except Exception as e:
                self.results["errors"].append({
                    "test": "sequential_read",
                    "file": file_path.name,
                    "error": str(e)
                })
                print(f"      ❌ File {i+1}/{self.num_files}: {e}")

        avg_throughput = (total_bytes / (1024 * 1024)) / total_duration if total_duration > 0 else 0

        return {
            "test": "sequential_read",
            "total_duration_sec": round(total_duration, 3),
            "average_throughput_mb_per_sec": round(avg_throughput, 2),
            "files_read": len(file_results),
            "verification_failures": verification_failures,
            "file_details": file_results
        }

    def test_random_io(self, operations: int = 1000) -> Dict:
        """Test random I/O operations (seek + read/write)."""
        print(f"   Testing random I/O ({operations} operations)...")

        # Use first test file
        file_path = Path(self.temp_dir) / f"test_write_0.bin"

        if not file_path.exists():
            return {
                "test": "random_io",
                "error": "Test file not found (run sequential write first)"
            }

        try:
            start = time.time()

            read_count = 0
            write_count = 0
            total_bytes = 0

            with open(file_path, 'r+b') as f:
                file_size = f.seek(0, 2)  # Seek to end to get size

                for _ in range(operations):
                    # Random seek
                    pos = int((hash(time.time()) % file_size))
                    f.seek(pos)

                    # Random read or write
                    if hash(pos) % 2 == 0:
                        # Read 4KB
                        chunk = f.read(4096)
                        read_count += 1
                        total_bytes += len(chunk)
                    else:
                        # Write 4KB
                        data = os.urandom(4096)
                        f.write(data)
                        write_count += 1
                        total_bytes += len(data)

            duration = time.time() - start
            ops_per_sec = operations / duration
            throughput_mb_per_sec = (total_bytes / (1024 * 1024)) / duration

            print(f"      {duration:.3f}s ({ops_per_sec:.0f} IOPS, {throughput_mb_per_sec:.2f} MB/s)")

            return {
                "test": "random_io",
                "duration_sec": round(duration, 3),
                "operations": operations,
                "iops": int(ops_per_sec),
                "throughput_mb_per_sec": round(throughput_mb_per_sec, 2),
                "read_count": read_count,
                "write_count": write_count
            }

        except Exception as e:
            self.results["errors"].append({
                "test": "random_io",
                "error": str(e)
            })
            print(f"      ❌ {e}")
            return {
                "test": "random_io",
                "error": str(e)
            }

    def run(self) -> Dict:
        """
        Execute I/O stress test.

        Returns:
            Results dictionary
        """
        print(f"💿 I/O Stress Test - {self.num_files} files × {self.file_size_mb} MB")

        overall_start = time.time()
        test_results = []

        try:
            # Setup
            self.setup_temp_directory()

            # Run tests
            test_results.append(self.test_sequential_write())
            test_results.append(self.test_sequential_read())
            test_results.append(self.test_random_io(operations=1000))

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

        finally:
            # Cleanup
            self.cleanup_temp_directory()

        return self.results

    def save_results(self, output_path: str):
        """Save results to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="QWAMOS I/O Stress Workload")
    parser.add_argument('--file-size', type=int, default=100, help='File size in MB')
    parser.add_argument('--num-files', type=int, default=10, help='Number of files')
    parser.add_argument('--output', type=str, default='io_stress_results.json', help='Output file')
    args = parser.parse_args()

    workload = IOStressWorkload(file_size_mb=args.file_size, num_files=args.num_files)
    results = workload.run()
    workload.save_results(args.output)

    print(f"\n✅ Results saved to: {args.output}")

    # Return non-zero exit code if errors occurred
    sys.exit(1 if results["metrics"]["tests_failed"] > 0 else 0)


if __name__ == "__main__":
    main()
