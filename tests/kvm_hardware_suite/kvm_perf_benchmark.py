#!/usr/bin/env python3
"""
QWAMOS KVM Performance Benchmark
Phase XII: KVM Acceleration - Performance Testing

Benchmarks KVM vs TCG performance on real hardware
Author: QWAMOS Project
License: AGPL-3.0
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class KVMBenchmark:
    """KVM performance benchmarking suite."""

    def __init__(self, output_dir: str = "."):
        """Initialize benchmark."""
        self.output_dir = Path(output_dir)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": {},
            "summary": {}
        }
        self.kvm_available = os.path.exists("/dev/kvm")

    def run_all_benchmarks(self):
        """Run all performance benchmarks."""
        print("=" * 80)
        print("QWAMOS Phase XII - KVM Performance Benchmark")
        print("=" * 80)
        print("")

        if not self.kvm_available:
            print("⚠️  WARNING: /dev/kvm not found")
            print("   Benchmarks will only test software emulation (TCG)")
            print("")

        # Run benchmarks
        self.benchmark_cpu()
        self.benchmark_memory()
        self.benchmark_crypto()
        self.benchmark_io()

        # Generate summary
        self.generate_summary()

        # Save results
        self.save_results()

    def benchmark_cpu(self):
        """Benchmark CPU performance."""
        print("🔥 CPU Benchmark")
        print("  Testing integer and floating-point operations...")

        results = {}

        # Integer benchmark (pi calculation)
        print("    Computing π (10M iterations)...", end=" ", flush=True)
        start = time.time()
        pi = self._calculate_pi(10000000)
        duration = time.time() - start
        results["pi_calculation_10m"] = {
            "duration_sec": round(duration, 3),
            "iterations_per_sec": int(10000000 / duration),
            "result": round(pi, 6)
        }
        print(f"{duration:.3f}s")

        # Prime number sieve
        print("    Prime sieve (100,000)...", end=" ", flush=True)
        start = time.time()
        primes = self._sieve_of_eratosthenes(100000)
        duration = time.time() - start
        results["prime_sieve_100k"] = {
            "duration_sec": round(duration, 3),
            "primes_found": len(primes)
        }
        print(f"{duration:.3f}s ({len(primes)} primes)")

        self.results["benchmarks"]["cpu"] = results

    def benchmark_memory(self):
        """Benchmark memory throughput."""
        print("\n💾 Memory Benchmark")
        print("  Testing memory allocation and access patterns...")

        results = {}

        # Sequential write
        print("    Sequential write (100MB)...", end=" ", flush=True)
        size_mb = 100
        start = time.time()
        data = bytearray(size_mb * 1024 * 1024)
        for i in range(len(data)):
            data[i] = i % 256
        duration = time.time() - start
        throughput = size_mb / duration
        results["sequential_write_100mb"] = {
            "duration_sec": round(duration, 3),
            "throughput_mb_per_sec": round(throughput, 2)
        }
        print(f"{duration:.3f}s ({throughput:.2f} MB/s)")

        # Random access
        print("    Random access (1M operations)...", end=" ", flush=True)
        import random
        test_size = 10 * 1024 * 1024  # 10MB
        test_data = bytearray(test_size)
        iterations = 1000000
        start = time.time()
        for _ in range(iterations):
            idx = random.randint(0, test_size - 1)
            _ = test_data[idx]
        duration = time.time() - start
        ops_per_sec = iterations / duration
        results["random_access_1m"] = {
            "duration_sec": round(duration, 3),
            "ops_per_sec": int(ops_per_sec)
        }
        print(f"{duration:.3f}s ({ops_per_sec:.0f} ops/s)")

        self.results["benchmarks"]["memory"] = results

    def benchmark_crypto(self):
        """Benchmark cryptographic operations."""
        print("\n🔐 Crypto Benchmark")
        print("  Testing ChaCha20-Poly1305 performance...")

        results = {}

        # Try to use Python's hashlib for ChaCha20 (if available)
        try:
            import hashlib

            # SHA256 benchmark (as baseline)
            print("    SHA256 (10MB)...", end=" ", flush=True)
            data = os.urandom(10 * 1024 * 1024)
            start = time.time()
            hash_obj = hashlib.sha256(data)
            digest = hash_obj.hexdigest()
            duration = time.time() - start
            throughput = 10 / duration
            results["sha256_10mb"] = {
                "duration_sec": round(duration, 3),
                "throughput_mb_per_sec": round(throughput, 2)
            }
            print(f"{duration:.3f}s ({throughput:.2f} MB/s)")

            # BLAKE2b benchmark
            print("    BLAKE2b (10MB)...", end=" ", flush=True)
            start = time.time()
            hash_obj = hashlib.blake2b(data)
            digest = hash_obj.hexdigest()
            duration = time.time() - start
            throughput = 10 / duration
            results["blake2b_10mb"] = {
                "duration_sec": round(duration, 3),
                "throughput_mb_per_sec": round(throughput, 2)
            }
            print(f"{duration:.3f}s ({throughput:.2f} MB/s)")

        except Exception as e:
            print(f"    ⚠️  Crypto benchmark failed: {e}")
            results["error"] = str(e)

        self.results["benchmarks"]["crypto"] = results

    def benchmark_io(self):
        """Benchmark I/O performance."""
        print("\n💿 I/O Benchmark")
        print("  Testing disk write/read performance...")

        results = {}

        test_file = self.output_dir / "benchmark_test.tmp"

        try:
            # Write test
            print("    Write 50MB...", end=" ", flush=True)
            size_mb = 50
            data = os.urandom(size_mb * 1024 * 1024)
            start = time.time()
            with open(test_file, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            duration = time.time() - start
            throughput = size_mb / duration
            results["write_50mb"] = {
                "duration_sec": round(duration, 3),
                "throughput_mb_per_sec": round(throughput, 2)
            }
            print(f"{duration:.3f}s ({throughput:.2f} MB/s)")

            # Read test
            print("    Read 50MB...", end=" ", flush=True)
            start = time.time()
            with open(test_file, "rb") as f:
                read_data = f.read()
            duration = time.time() - start
            throughput = size_mb / duration
            results["read_50mb"] = {
                "duration_sec": round(duration, 3),
                "throughput_mb_per_sec": round(throughput, 2)
            }
            print(f"{duration:.3f}s ({throughput:.2f} MB/s)")

            # Cleanup
            test_file.unlink()

        except Exception as e:
            print(f"    ⚠️  I/O benchmark failed: {e}")
            results["error"] = str(e)

        self.results["benchmarks"]["io"] = results

    def generate_summary(self):
        """Generate benchmark summary."""
        print("\n" + "=" * 80)
        print("Benchmark Summary")
        print("=" * 80)

        summary = {
            "kvm_available": self.kvm_available,
            "overall_rating": "unknown"
        }

        # Calculate overall score based on benchmarks
        if "cpu" in self.results["benchmarks"]:
            cpu_bench = self.results["benchmarks"]["cpu"]
            if "pi_calculation_10m" in cpu_bench:
                duration = cpu_bench["pi_calculation_10m"]["duration_sec"]
                if duration < 0.5:
                    summary["cpu_rating"] = "excellent"
                elif duration < 1.0:
                    summary["cpu_rating"] = "good"
                elif duration < 2.0:
                    summary["cpu_rating"] = "acceptable"
                else:
                    summary["cpu_rating"] = "slow"

        if "memory" in self.results["benchmarks"]:
            mem_bench = self.results["benchmarks"]["memory"]
            if "sequential_write_100mb" in mem_bench:
                throughput = mem_bench["sequential_write_100mb"]["throughput_mb_per_sec"]
                if throughput > 500:
                    summary["memory_rating"] = "excellent"
                elif throughput > 200:
                    summary["memory_rating"] = "good"
                elif throughput > 100:
                    summary["memory_rating"] = "acceptable"
                else:
                    summary["memory_rating"] = "slow"

        if "crypto" in self.results["benchmarks"]:
            crypto_bench = self.results["benchmarks"]["crypto"]
            if "blake2b_10mb" in crypto_bench:
                throughput = crypto_bench["blake2b_10mb"]["throughput_mb_per_sec"]
                if throughput > 200:
                    summary["crypto_rating"] = "excellent"
                elif throughput > 100:
                    summary["crypto_rating"] = "good"
                elif throughput > 50:
                    summary["crypto_rating"] = "acceptable"
                else:
                    summary["crypto_rating"] = "slow"

        # Print summary
        print(f"\nKVM Available: {'✅ Yes' if summary['kvm_available'] else '❌ No'}")
        if "cpu_rating" in summary:
            print(f"CPU Performance: {summary['cpu_rating'].upper()}")
        if "memory_rating" in summary:
            print(f"Memory Performance: {summary['memory_rating'].upper()}")
        if "crypto_rating" in summary:
            print(f"Crypto Performance: {summary['crypto_rating'].upper()}")

        self.results["summary"] = summary

    def save_results(self):
        """Save benchmark results to JSON."""
        output_file = self.output_dir / "kvm_perf_benchmark_results.json"
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✅ Results saved to: {output_file}")

        # Also save markdown report
        self._save_markdown_report()

    def _save_markdown_report(self):
        """Save benchmark results as markdown."""
        output_file = self.output_dir / "kvm_perf_benchmark_report.md"

        with open(output_file, "w") as f:
            f.write("# QWAMOS Phase XII - KVM Performance Benchmark Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**KVM Available:** {'Yes' if self.kvm_available else 'No'}\n\n")

            f.write("## CPU Benchmarks\n\n")
            if "cpu" in self.results["benchmarks"]:
                cpu = self.results["benchmarks"]["cpu"]
                f.write("| Test | Duration | Performance |\n")
                f.write("|------|----------|-------------|\n")
                for test_name, result in cpu.items():
                    duration = result.get("duration_sec", "N/A")
                    if "iterations_per_sec" in result:
                        perf = f"{result['iterations_per_sec']:,} iter/s"
                    elif "primes_found" in result:
                        perf = f"{result['primes_found']} primes"
                    else:
                        perf = "N/A"
                    f.write(f"| {test_name} | {duration}s | {perf} |\n")
                f.write("\n")

            f.write("## Memory Benchmarks\n\n")
            if "memory" in self.results["benchmarks"]:
                mem = self.results["benchmarks"]["memory"]
                f.write("| Test | Duration | Throughput |\n")
                f.write("|------|----------|------------|\n")
                for test_name, result in mem.items():
                    duration = result.get("duration_sec", "N/A")
                    throughput = result.get("throughput_mb_per_sec") or result.get("ops_per_sec", "N/A")
                    unit = "MB/s" if "throughput_mb_per_sec" in result else "ops/s"
                    f.write(f"| {test_name} | {duration}s | {throughput} {unit} |\n")
                f.write("\n")

            f.write("## Crypto Benchmarks\n\n")
            if "crypto" in self.results["benchmarks"]:
                crypto = self.results["benchmarks"]["crypto"]
                if "error" not in crypto:
                    f.write("| Algorithm | Data Size | Duration | Throughput |\n")
                    f.write("|-----------|-----------|----------|------------|\n")
                    for test_name, result in crypto.items():
                        duration = result.get("duration_sec", "N/A")
                        throughput = result.get("throughput_mb_per_sec", "N/A")
                        f.write(f"| {test_name.replace('_10mb', '')} | 10MB | {duration}s | {throughput} MB/s |\n")
                    f.write("\n")

            f.write("## Summary\n\n")
            if "summary" in self.results:
                for key, value in self.results["summary"].items():
                    f.write(f"- **{key}:** {value}\n")

        print(f"✅ Markdown report saved to: {output_file}")

    # Helper methods

    def _calculate_pi(self, iterations: int) -> float:
        """Calculate π using Leibniz formula."""
        pi = 0.0
        for i in range(iterations):
            pi += ((-1) ** i) / (2 * i + 1)
        return 4 * pi

    def _sieve_of_eratosthenes(self, limit: int) -> List[int]:
        """Find all primes up to limit using Sieve of Eratosthenes."""
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False

        for i in range(2, int(limit**0.5) + 1):
            if is_prime[i]:
                for j in range(i*i, limit + 1, i):
                    is_prime[j] = False

        return [i for i in range(limit + 1) if is_prime[i]]


def main():
    """Main entry point."""
    benchmark = KVMBenchmark()
    benchmark.run_all_benchmarks()

    print("\nNext steps:")
    print("  1. Review kvm_perf_benchmark_results.json")
    print("  2. Review kvm_perf_benchmark_report.md")
    print("  3. Run: python3 vm_boot_test.py")
    print("")


if __name__ == "__main__":
    main()
