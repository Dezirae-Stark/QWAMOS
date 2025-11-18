#!/usr/bin/env python3
"""
QWAMOS Differential Testing - Comparison Engine
Phase XII: KVM vs QEMU Analysis

Compares performance metrics between QEMU and KVM modes
Author: QWAMOS Project
License: AGPL-3.0
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class ComparisonEngine:
    """Analyzes and compares QEMU vs KVM test results."""

    # Variance thresholds
    VARIANCE_EQUIVALENT = 0.10  # <10%: Equivalent
    VARIANCE_ACCEPTABLE = 0.25  # 10-25%: Acceptable difference
    # >25%: Significant deviation

    def __init__(self, qemu_results_path: str, kvm_results_path: str, output_dir: str = "."):
        """
        Initialize comparison engine.

        Args:
            qemu_results_path: Path to QEMU results JSON
            kvm_results_path: Path to KVM results JSON
            output_dir: Output directory for reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load results
        self.qemu_results = self._load_json(qemu_results_path)
        self.kvm_results = self._load_json(kvm_results_path)

        self.comparison = {
            "timestamp": datetime.now().isoformat(),
            "qemu_file": qemu_results_path,
            "kvm_file": kvm_results_path,
            "comparisons": [],
            "security_notes": [],
            "summary": {}
        }

    def _load_json(self, path: str) -> Dict:
        """Load JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load {path}: {e}")
            return {}

    def calculate_variance(self, qemu_value: float, kvm_value: float) -> Tuple[float, str]:
        """
        Calculate variance between two values.

        Args:
            qemu_value: QEMU metric value
            kvm_value: KVM metric value

        Returns:
            (variance_percentage, classification)
        """
        if qemu_value == 0:
            if kvm_value == 0:
                return 0.0, "Equivalent"
            else:
                return float('inf'), "Significant deviation"

        variance = abs(kvm_value - qemu_value) / qemu_value

        if variance < self.VARIANCE_EQUIVALENT:
            classification = "Equivalent"
        elif variance < self.VARIANCE_ACCEPTABLE:
            classification = "Acceptable difference"
        else:
            classification = "Significant deviation"

        return variance, classification

    def compare_workload(self, workload_name: str, qemu_data: Dict, kvm_data: Dict) -> Dict:
        """
        Compare a specific workload between QEMU and KVM.

        Args:
            workload_name: Name of the workload
            qemu_data: QEMU workload results
            kvm_data: KVM workload results

        Returns:
            Comparison results
        """
        comparison = {
            "workload": workload_name,
            "metrics": [],
            "issues": []
        }

        # Check for errors
        if "error" in qemu_data:
            comparison["issues"].append(f"QEMU error: {qemu_data['error']}")
        if "error" in kvm_data:
            comparison["issues"].append(f"KVM error: {kvm_data['error']}")

        if comparison["issues"]:
            return comparison

        # Extract metrics from both results
        qemu_metrics = qemu_data.get("metrics", {})
        kvm_metrics = kvm_data.get("metrics", {})

        # Compare total duration
        if "total_duration_sec" in qemu_metrics and "total_duration_sec" in kvm_metrics:
            qemu_dur = qemu_metrics["total_duration_sec"]
            kvm_dur = kvm_metrics["total_duration_sec"]
            variance, classification = self.calculate_variance(qemu_dur, kvm_dur)

            comparison["metrics"].append({
                "metric": "total_duration_sec",
                "qemu_value": qemu_dur,
                "kvm_value": kvm_dur,
                "variance_pct": round(variance * 100, 2),
                "classification": classification,
                "kvm_faster": kvm_dur < qemu_dur
            })

        # Compare workload-specific metrics
        self._compare_specific_metrics(workload_name, qemu_metrics, kvm_metrics, comparison)

        return comparison

    def _compare_specific_metrics(self, workload_name: str, qemu_metrics: Dict, kvm_metrics: Dict, comparison: Dict):
        """Compare workload-specific metrics."""

        # CPU stress metrics
        if workload_name == "cpu_stress":
            if "aggregate_hashes_per_sec" in qemu_metrics and "aggregate_hashes_per_sec" in kvm_metrics:
                variance, classification = self.calculate_variance(
                    qemu_metrics["aggregate_hashes_per_sec"],
                    kvm_metrics["aggregate_hashes_per_sec"]
                )
                comparison["metrics"].append({
                    "metric": "aggregate_hashes_per_sec",
                    "qemu_value": qemu_metrics["aggregate_hashes_per_sec"],
                    "kvm_value": kvm_metrics["aggregate_hashes_per_sec"],
                    "variance_pct": round(variance * 100, 2),
                    "classification": classification,
                    "kvm_faster": kvm_metrics["aggregate_hashes_per_sec"] > qemu_metrics["aggregate_hashes_per_sec"]
                })

        # Memory stress metrics
        elif workload_name == "mem_stress":
            # Compare individual test results
            qemu_tests = qemu_metrics.get("test_details", [])
            kvm_tests = kvm_metrics.get("test_details", [])

            for qemu_test in qemu_tests:
                test_name = qemu_test.get("test")
                kvm_test = next((t for t in kvm_tests if t.get("test") == test_name), None)

                if kvm_test:
                    # Compare throughput
                    if "throughput_mb_per_sec" in qemu_test and "throughput_mb_per_sec" in kvm_test:
                        variance, classification = self.calculate_variance(
                            qemu_test["throughput_mb_per_sec"],
                            kvm_test["throughput_mb_per_sec"]
                        )
                        comparison["metrics"].append({
                            "metric": f"{test_name}_throughput_mb_per_sec",
                            "qemu_value": qemu_test["throughput_mb_per_sec"],
                            "kvm_value": kvm_test["throughput_mb_per_sec"],
                            "variance_pct": round(variance * 100, 2),
                            "classification": classification,
                            "kvm_faster": kvm_test["throughput_mb_per_sec"] > qemu_test["throughput_mb_per_sec"]
                        })

        # I/O stress metrics
        elif workload_name == "io_stress":
            qemu_tests = qemu_metrics.get("test_details", [])
            kvm_tests = kvm_metrics.get("test_details", [])

            for qemu_test in qemu_tests:
                test_name = qemu_test.get("test")
                kvm_test = next((t for t in kvm_tests if t.get("test") == test_name), None)

                if kvm_test:
                    # Compare average throughput
                    if "average_throughput_mb_per_sec" in qemu_test and "average_throughput_mb_per_sec" in kvm_test:
                        variance, classification = self.calculate_variance(
                            qemu_test["average_throughput_mb_per_sec"],
                            kvm_test["average_throughput_mb_per_sec"]
                        )
                        comparison["metrics"].append({
                            "metric": f"{test_name}_avg_throughput_mb_per_sec",
                            "qemu_value": qemu_test["average_throughput_mb_per_sec"],
                            "kvm_value": kvm_test["average_throughput_mb_per_sec"],
                            "variance_pct": round(variance * 100, 2),
                            "classification": classification,
                            "kvm_faster": kvm_test["average_throughput_mb_per_sec"] > qemu_test["average_throughput_mb_per_sec"]
                        })

                    # Compare IOPS
                    if "iops" in qemu_test and "iops" in kvm_test:
                        variance, classification = self.calculate_variance(
                            qemu_test["iops"],
                            kvm_test["iops"]
                        )
                        comparison["metrics"].append({
                            "metric": f"{test_name}_iops",
                            "qemu_value": qemu_test["iops"],
                            "kvm_value": kvm_test["iops"],
                            "variance_pct": round(variance * 100, 2),
                            "classification": classification,
                            "kvm_faster": kvm_test["iops"] > qemu_test["iops"]
                        })

        # Crypto stress metrics
        elif workload_name == "crypt_stress":
            qemu_tests = qemu_metrics.get("test_details", [])
            kvm_tests = kvm_metrics.get("test_details", [])

            for qemu_test in qemu_tests:
                test_name = qemu_test.get("test")
                kvm_test = next((t for t in kvm_tests if t.get("test") == test_name), None)

                if kvm_test:
                    # Compare throughput
                    if "throughput_mb_per_sec" in qemu_test and "throughput_mb_per_sec" in kvm_test:
                        variance, classification = self.calculate_variance(
                            qemu_test["throughput_mb_per_sec"],
                            kvm_test["throughput_mb_per_sec"]
                        )
                        comparison["metrics"].append({
                            "metric": f"{test_name}_throughput_mb_per_sec",
                            "qemu_value": qemu_test["throughput_mb_per_sec"],
                            "kvm_value": kvm_test["throughput_mb_per_sec"],
                            "variance_pct": round(variance * 100, 2),
                            "classification": classification,
                            "kvm_faster": kvm_test["throughput_mb_per_sec"] > qemu_test["throughput_mb_per_sec"]
                        })

                    # Compare operations per second
                    if "keys_per_sec" in qemu_test and "keys_per_sec" in kvm_test:
                        variance, classification = self.calculate_variance(
                            qemu_test["keys_per_sec"],
                            kvm_test["keys_per_sec"]
                        )
                        comparison["metrics"].append({
                            "metric": f"{test_name}_keys_per_sec",
                            "qemu_value": qemu_test["keys_per_sec"],
                            "kvm_value": kvm_test["keys_per_sec"],
                            "variance_pct": round(variance * 100, 2),
                            "classification": classification,
                            "kvm_faster": kvm_test["keys_per_sec"] > qemu_test["keys_per_sec"]
                        })

    def analyze_security_concerns(self):
        """Analyze results for security concerns."""

        # Check for unexpected behavior patterns
        for comp in self.comparison["comparisons"]:
            workload = comp["workload"]

            # Check for anomalies in timing
            for metric in comp["metrics"]:
                if metric["variance_pct"] > 100:  # More than 100% variance
                    self.comparison["security_notes"].append({
                        "severity": "high",
                        "category": "timing_anomaly",
                        "description": f"{workload}/{metric['metric']}: Extreme variance ({metric['variance_pct']:.1f}%) may indicate timing side-channel vulnerability"
                    })

                # Check if KVM is unexpectedly slower
                if metric.get("kvm_faster") is False and metric["variance_pct"] > 25:
                    self.comparison["security_notes"].append({
                        "severity": "medium",
                        "category": "performance_regression",
                        "description": f"{workload}/{metric['metric']}: KVM slower than QEMU ({metric['variance_pct']:.1f}% variance) - investigate potential scheduler/interrupt issues"
                    })

            # Check for errors
            if comp.get("issues"):
                for issue in comp["issues"]:
                    self.comparison["security_notes"].append({
                        "severity": "high",
                        "category": "execution_error",
                        "description": f"{workload}: {issue}"
                    })

    def generate_summary(self):
        """Generate comparison summary."""
        total_metrics = 0
        equivalent = 0
        acceptable = 0
        significant = 0
        kvm_faster_count = 0
        qemu_faster_count = 0

        for comp in self.comparison["comparisons"]:
            for metric in comp["metrics"]:
                total_metrics += 1

                classification = metric["classification"]
                if classification == "Equivalent":
                    equivalent += 1
                elif classification == "Acceptable difference":
                    acceptable += 1
                else:  # Significant deviation
                    significant += 1

                if metric.get("kvm_faster"):
                    kvm_faster_count += 1
                else:
                    qemu_faster_count += 1

        self.comparison["summary"] = {
            "total_metrics_compared": total_metrics,
            "equivalent_count": equivalent,
            "acceptable_difference_count": acceptable,
            "significant_deviation_count": significant,
            "kvm_faster_count": kvm_faster_count,
            "qemu_faster_count": qemu_faster_count,
            "security_notes_count": len(self.comparison["security_notes"]),
            "overall_assessment": self._get_overall_assessment(equivalent, acceptable, significant, total_metrics)
        }

    def _get_overall_assessment(self, equivalent: int, acceptable: int, significant: int, total: int) -> str:
        """Determine overall assessment."""
        if total == 0:
            return "No metrics to compare"

        significant_pct = (significant / total) * 100

        if significant_pct > 50:
            return "CRITICAL: Majority of metrics show significant deviations"
        elif significant_pct > 25:
            return "WARNING: Many metrics show significant deviations"
        elif acceptable + equivalent >= total * 0.9:
            return "GOOD: Most metrics within acceptable range"
        else:
            return "ACCEPTABLE: Some deviations noted"

    def run_comparison(self):
        """Run full comparison analysis."""
        print("=" * 80)
        print("QWAMOS Phase XII - Differential Comparison Engine")
        print("=" * 80)
        print()

        # Check if KVM results are available
        if self.kvm_results.get("skipped"):
            print("⚠️  KVM results unavailable - comparison skipped")
            print(f"   Reason: {self.kvm_results.get('reason', 'Unknown')}")
            print()
            return

        # Compare each workload
        qemu_workloads = self.qemu_results.get("workloads", {})
        kvm_workloads = self.kvm_results.get("workloads", {})

        for workload_name in qemu_workloads.keys():
            if workload_name in kvm_workloads:
                print(f"Comparing {workload_name}...")
                comparison = self.compare_workload(
                    workload_name,
                    qemu_workloads[workload_name],
                    kvm_workloads[workload_name]
                )
                self.comparison["comparisons"].append(comparison)

        # Analyze security concerns
        self.analyze_security_concerns()

        # Generate summary
        self.generate_summary()

        # Save results
        self.save_json_report()
        self.save_markdown_report()

        # Print summary
        self.print_summary()

    def save_json_report(self):
        """Save comparison results as JSON."""
        output_path = self.output_dir / "diff_summary.json"
        with open(output_path, 'w') as f:
            json.dump(self.comparison, f, indent=2)
        print(f"\n✅ JSON report saved: {output_path}")

    def save_markdown_report(self):
        """Save comparison results as Markdown."""
        output_path = self.output_dir / "diff_report.md"

        with open(output_path, 'w') as f:
            f.write("# QWAMOS Phase XII - Differential Testing Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Summary
            f.write("## Summary\n\n")
            summary = self.comparison["summary"]
            f.write(f"**Overall Assessment:** {summary['overall_assessment']}\n\n")
            f.write(f"- Total metrics compared: {summary['total_metrics_compared']}\n")
            f.write(f"- Equivalent (<10% variance): {summary['equivalent_count']}\n")
            f.write(f"- Acceptable difference (10-25%): {summary['acceptable_difference_count']}\n")
            f.write(f"- Significant deviation (>25%): {summary['significant_deviation_count']}\n")
            f.write(f"- KVM faster: {summary['kvm_faster_count']}\n")
            f.write(f"- QEMU faster: {summary['qemu_faster_count']}\n")
            f.write(f"- Security notes: {summary['security_notes_count']}\n\n")

            # Detailed comparisons
            f.write("---\n\n")
            f.write("## Detailed Comparisons\n\n")

            for comp in self.comparison["comparisons"]:
                f.write(f"### {comp['workload']}\n\n")

                if comp.get("issues"):
                    f.write("**Issues:**\n")
                    for issue in comp["issues"]:
                        f.write(f"- ❌ {issue}\n")
                    f.write("\n")

                if comp["metrics"]:
                    f.write("| Metric | QEMU | KVM | Variance | Classification | Winner |\n")
                    f.write("|--------|------|-----|----------|----------------|--------|\n")

                    for metric in comp["metrics"]:
                        winner = "🚀 KVM" if metric.get("kvm_faster") else "QEMU"
                        f.write(f"| {metric['metric']} | {metric['qemu_value']:.2f} | {metric['kvm_value']:.2f} | {metric['variance_pct']:.1f}% | {metric['classification']} | {winner} |\n")

                    f.write("\n")

            # Security notes
            if self.comparison["security_notes"]:
                f.write("---\n\n")
                f.write("## Security & Performance Notes\n\n")

                for note in self.comparison["security_notes"]:
                    severity_icon = "🔴" if note["severity"] == "high" else "🟡"
                    f.write(f"**{severity_icon} {note['category'].upper()}** ({note['severity']})\n")
                    f.write(f"- {note['description']}\n\n")

            f.write("---\n\n")
            f.write("## Recommendations\n\n")

            if summary['significant_deviation_count'] > 0:
                f.write("1. **Investigate significant deviations:** Review metrics with >25% variance\n")
                f.write("2. **Check system configuration:** Ensure KVM is properly configured\n")
                f.write("3. **Review security notes:** Address timing anomalies and performance regressions\n")
            else:
                f.write("1. **Performance validated:** KVM and QEMU show consistent behavior\n")
                f.write("2. **Proceed with deployment:** Phase XII ready for production\n")

            f.write("\n")

        print(f"✅ Markdown report saved: {output_path}")

    def print_summary(self):
        """Print summary to console."""
        print("\n" + "=" * 80)
        print("Comparison Summary")
        print("=" * 80)

        summary = self.comparison["summary"]
        print(f"\nOverall Assessment: {summary['overall_assessment']}")
        print(f"\nMetrics Compared: {summary['total_metrics_compared']}")
        print(f"  - Equivalent: {summary['equivalent_count']}")
        print(f"  - Acceptable: {summary['acceptable_difference_count']}")
        print(f"  - Significant deviation: {summary['significant_deviation_count']}")
        print(f"\nPerformance Winner:")
        print(f"  - KVM faster: {summary['kvm_faster_count']} metrics")
        print(f"  - QEMU faster: {summary['qemu_faster_count']} metrics")

        if summary['security_notes_count'] > 0:
            print(f"\n⚠️  Security/Performance Notes: {summary['security_notes_count']}")
            print("   Review diff_report.md for details")

        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="QWAMOS Differential Comparison Engine"
    )
    parser.add_argument(
        '--qemu-results',
        type=str,
        default='qemu_results.json',
        help='Path to QEMU results JSON'
    )
    parser.add_argument(
        '--kvm-results',
        type=str,
        default='kvm_results.json',
        help='Path to KVM results JSON'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Output directory for reports'
    )
    args = parser.parse_args()

    engine = ComparisonEngine(
        qemu_results_path=args.qemu_results,
        kvm_results_path=args.kvm_results,
        output_dir=args.output_dir
    )
    engine.run_comparison()


if __name__ == "__main__":
    main()
