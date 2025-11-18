#!/usr/bin/env python3
"""
QWAMOS Differential Testing - CPU Stress Workload
Phase XII: KVM vs QEMU Comparison

Multi-threaded BLAKE3 hashing stress test
Author: QWAMOS Project
License: AGPL-3.0
"""

import os
import sys
import time
import json
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class CPUStressWorkload:
    """CPU-intensive workload using BLAKE3 hashing."""

    def __init__(self, threads: int = 4, iterations: int = 100000):
        """
        Initialize CPU stress test.

        Args:
            threads: Number of concurrent threads
            iterations: Iterations per thread
        """
        self.threads = threads
        self.iterations = iterations
        self.results = {
            "workload": "cpu_stress",
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "threads": threads,
                "iterations": iterations
            },
            "metrics": {},
            "errors": []
        }
        self.thread_results = []
        self.lock = threading.Lock()

    def worker_thread(self, thread_id: int, data_size: int = 1024):
        """
        Worker thread performing BLAKE3 hashing.

        Args:
            thread_id: Thread identifier
            data_size: Size of data to hash (bytes)
        """
        thread_start = time.time()
        hashes_computed = 0
        bytes_processed = 0
        errors = 0

        try:
            # Generate random data for this thread
            data = os.urandom(data_size)

            for i in range(self.iterations):
                try:
                    # BLAKE3 fallback to BLAKE2b (BLAKE3 not in standard hashlib)
                    # In production, use python-blake3 package
                    hash_obj = hashlib.blake2b(data)
                    digest = hash_obj.digest()

                    # Verify digest length
                    if len(digest) != 64:
                        errors += 1
                        continue

                    hashes_computed += 1
                    bytes_processed += data_size

                    # Use digest as next iteration's data (chain hashes)
                    data = digest + os.urandom(data_size - 64)

                except Exception as e:
                    errors += 1
                    with self.lock:
                        self.results["errors"].append({
                            "thread": thread_id,
                            "iteration": i,
                            "error": str(e)
                        })

        except Exception as e:
            with self.lock:
                self.results["errors"].append({
                    "thread": thread_id,
                    "fatal": True,
                    "error": str(e)
                })

        thread_duration = time.time() - thread_start

        # Store thread results
        with self.lock:
            self.thread_results.append({
                "thread_id": thread_id,
                "duration_sec": round(thread_duration, 3),
                "hashes_computed": hashes_computed,
                "bytes_processed": bytes_processed,
                "hashes_per_sec": round(hashes_computed / thread_duration, 2) if thread_duration > 0 else 0,
                "throughput_mb_per_sec": round((bytes_processed / (1024 * 1024)) / thread_duration, 2) if thread_duration > 0 else 0,
                "errors": errors
            })

    def run(self) -> Dict:
        """
        Execute CPU stress test.

        Returns:
            Results dictionary
        """
        print(f"🔥 CPU Stress Test - {self.threads} threads, {self.iterations} iterations/thread")
        print(f"   Using BLAKE2b hashing (BLAKE3 fallback)")

        overall_start = time.time()

        # Launch worker threads
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.worker_thread, args=(i,))
            t.start()
            threads.append(t)

        # Wait for all threads to complete
        for t in threads:
            t.join()

        overall_duration = time.time() - overall_start

        # Calculate aggregate metrics
        total_hashes = sum(r["hashes_computed"] for r in self.thread_results)
        total_bytes = sum(r["bytes_processed"] for r in self.thread_results)
        total_errors = sum(r["errors"] for r in self.thread_results)

        self.results["metrics"] = {
            "total_duration_sec": round(overall_duration, 3),
            "total_hashes_computed": total_hashes,
            "total_bytes_processed": total_bytes,
            "aggregate_hashes_per_sec": round(total_hashes / overall_duration, 2) if overall_duration > 0 else 0,
            "aggregate_throughput_mb_per_sec": round((total_bytes / (1024 * 1024)) / overall_duration, 2) if overall_duration > 0 else 0,
            "total_errors": total_errors,
            "threads_completed": len(self.thread_results),
            "thread_details": self.thread_results
        }

        # Print summary
        print(f"   ✅ Completed in {overall_duration:.3f}s")
        print(f"   Total hashes: {total_hashes:,}")
        print(f"   Throughput: {self.results['metrics']['aggregate_hashes_per_sec']:.2f} hashes/sec")
        print(f"   Data processed: {self.results['metrics']['aggregate_throughput_mb_per_sec']:.2f} MB/s")
        if total_errors > 0:
            print(f"   ⚠️  Errors: {total_errors}")

        return self.results

    def save_results(self, output_path: str):
        """Save results to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="QWAMOS CPU Stress Workload")
    parser.add_argument('--threads', type=int, default=4, help='Number of threads')
    parser.add_argument('--iterations', type=int, default=100000, help='Iterations per thread')
    parser.add_argument('--output', type=str, default='cpu_stress_results.json', help='Output file')
    args = parser.parse_args()

    workload = CPUStressWorkload(threads=args.threads, iterations=args.iterations)
    results = workload.run()
    workload.save_results(args.output)

    print(f"\n✅ Results saved to: {args.output}")

    # Return non-zero exit code if errors occurred
    sys.exit(1 if results["metrics"]["total_errors"] > 0 else 0)


if __name__ == "__main__":
    main()
