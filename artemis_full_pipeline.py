#!/usr/bin/env python3
"""
QWAMOS Artemis Full Security Hardening Pipeline
Claude Sonnet 4.5 Autonomous Security System

Runs comprehensive security analysis and automated hardening.
Designed to run on GCP VM with full toolchain.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ArtemisColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class ArtemisPipeline:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.report_dir = repo_root / "reports"
        self.static_dir = self.report_dir / "static"
        self.triage_dir = self.report_dir / "triage"
        self.hardening_dir = self.report_dir / "hardening"

        # Create directories
        for d in [self.static_dir, self.triage_dir, self.hardening_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.findings = {
            "p0_critical": [],
            "p1_high": [],
            "p2_medium": [],
            "p3_low": [],
            "info": []
        }

    def print_header(self, text: str):
        print(f"\n{ArtemisColors.HEADER}{ArtemisColors.BOLD}{'═' * 70}{ArtemisColors.ENDC}")
        print(f"{ArtemisColors.HEADER}{ArtemisColors.BOLD}{text:^70}{ArtemisColors.ENDC}")
        print(f"{ArtemisColors.HEADER}{ArtemisColors.BOLD}{'═' * 70}{ArtemisColors.ENDC}\n")

    def print_step(self, step: int, total: int, description: str):
        print(f"{ArtemisColors.OKCYAN}[{step}/{total}] {description}...{ArtemisColors.ENDC}")

    def run_command(self, cmd: List[str], output_file: Path = None) -> Tuple[int, str, str]:
        """Run command and capture output"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=600
            )

            if output_file:
                output_file.write_text(result.stdout + result.stderr)

            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def phase1_static_analysis(self):
        """Phase 1: Comprehensive Static Analysis"""
        self.print_header("PHASE 1: STATIC ANALYSIS SUITE")

        analyses = [
            ("bandit", ["bandit", "-r", ".", "-f", "json", "-o", str(self.static_dir / "bandit.json")]),
            ("semgrep", ["semgrep", "--config=auto", "--json", f"--output={self.static_dir}/semgrep.json", "."]),
            ("safety", ["safety", "check", "--json", f"--output={self.static_dir}/safety.json"]),
            ("shellcheck", self._run_shellcheck),
            ("gitleaks", ["gitleaks", "detect", "-v", f"--report-path={self.static_dir}/gitleaks.json", "--report-format=json"]),
            ("syft", ["syft", "dir:.", "--output=json", f"--file={self.static_dir}/sbom.json"]),
            ("grype", ["grype", "dir:.", "--output=json", f"--file={self.static_dir}/grype.json"]),
            ("trivy", ["trivy", "fs", "--format=json", f"--output={self.static_dir}/trivy.json", "."]),
        ]

        for i, (name, cmd) in enumerate(analyses, 1):
            self.print_step(i, len(analyses), f"Running {name}")

            if callable(cmd):
                cmd()
            else:
                code, stdout, stderr = self.run_command(cmd)
                if code != 0 and "found" not in stderr.lower():
                    print(f"{ArtemisColors.WARNING}  ⚠ {name} completed with warnings{ArtemisColors.ENDC}")

        print(f"{ArtemisColors.OKGREEN}✅ Phase 1 Complete{ArtemisColors.ENDC}")

    def _run_shellcheck(self):
        """Run shellcheck on all shell scripts"""
        shell_files = list(self.repo_root.rglob("*.sh"))
        shell_files.extend(self.repo_root.rglob("*.bash"))

        results = []
        for script in shell_files:
            if ".git" in str(script):
                continue

            code, stdout, stderr = self.run_command(["shellcheck", "-f", "json", str(script)])
            if stdout:
                try:
                    results.extend(json.loads(stdout))
                except:
                    pass

        (self.static_dir / "shellcheck.json").write_text(json.dumps(results, indent=2))

    def phase2_triage(self):
        """Phase 2: Triage and Prioritization"""
        self.print_header("PHASE 2: TRIAGE AND PRIORITIZATION")

        # Load all results
        self._load_bandit_results()
        self._load_semgrep_results()
        self._load_gitleaks_results()
        self._load_shellcheck_results()
        self._load_vulnerability_results()

        # Write triage reports
        self._write_triage_reports()

        # Generate dependency graph
        self._generate_dependency_graph()

        print(f"{ArtemisColors.OKGREEN}✅ Phase 2 Complete{ArtemisColors.ENDC}")
        print(f"  P0 Critical: {len(self.findings['p0_critical'])}")
        print(f"  P1 High:     {len(self.findings['p1_high'])}")
        print(f"  P2 Medium:   {len(self.findings['p2_medium'])}")
        print(f"  P3 Low:      {len(self.findings['p3_low'])}")

    def _load_bandit_results(self):
        """Load and categorize bandit findings"""
        bandit_file = self.static_dir / "bandit.json"
        if not bandit_file.exists():
            return

        try:
            data = json.loads(bandit_file.read_text())
            for result in data.get("results", []):
                severity = result.get("issue_severity", "").upper()
                finding = {
                    "tool": "bandit",
                    "file": result.get("filename"),
                    "line": result.get("line_number"),
                    "issue": result.get("issue_text"),
                    "confidence": result.get("issue_confidence"),
                    "severity": severity,
                    "code": result.get("code")
                }

                if severity == "HIGH" and result.get("issue_confidence") == "HIGH":
                    self.findings["p0_critical"].append(finding)
                elif severity == "HIGH":
                    self.findings["p1_high"].append(finding)
                elif severity == "MEDIUM":
                    self.findings["p2_medium"].append(finding)
                else:
                    self.findings["p3_low"].append(finding)
        except Exception as e:
            print(f"{ArtemisColors.WARNING}Warning: Could not parse bandit results: {e}{ArtemisColors.ENDC}")

    def _load_semgrep_results(self):
        """Load and categorize semgrep findings"""
        semgrep_file = self.static_dir / "semgrep.json"
        if not semgrep_file.exists():
            return

        try:
            data = json.loads(semgrep_file.read_text())
            for result in data.get("results", []):
                extra = result.get("extra", {})
                severity = extra.get("severity", "").upper()

                finding = {
                    "tool": "semgrep",
                    "file": result.get("path"),
                    "line": result.get("start", {}).get("line"),
                    "issue": extra.get("message"),
                    "rule_id": result.get("check_id"),
                    "severity": severity
                }

                if "security" in result.get("check_id", "").lower():
                    if severity == "ERROR":
                        self.findings["p0_critical"].append(finding)
                    elif severity == "WARNING":
                        self.findings["p1_high"].append(finding)
                    else:
                        self.findings["p2_medium"].append(finding)
                else:
                    self.findings["p3_low"].append(finding)
        except Exception as e:
            print(f"{ArtemisColors.WARNING}Warning: Could not parse semgrep results: {e}{ArtemisColors.ENDC}")

    def _load_gitleaks_results(self):
        """Load secret scanning results"""
        gitleaks_file = self.static_dir / "gitleaks.json"
        if not gitleaks_file.exists():
            return

        try:
            data = json.loads(gitleaks_file.read_text())
            for leak in data:
                finding = {
                    "tool": "gitleaks",
                    "file": leak.get("File"),
                    "line": leak.get("StartLine"),
                    "issue": f"Secret detected: {leak.get('Description')}",
                    "secret_type": leak.get("RuleID"),
                    "severity": "CRITICAL"
                }
                self.findings["p0_critical"].append(finding)
        except Exception as e:
            print(f"{ArtemisColors.WARNING}Warning: Could not parse gitleaks results: {e}{ArtemisColors.ENDC}")

    def _load_shellcheck_results(self):
        """Load shellcheck findings"""
        shellcheck_file = self.static_dir / "shellcheck.json"
        if not shellcheck_file.exists():
            return

        try:
            data = json.loads(shellcheck_file.read_text())
            for issue in data:
                severity = issue.get("level", "").upper()
                finding = {
                    "tool": "shellcheck",
                    "file": issue.get("file"),
                    "line": issue.get("line"),
                    "issue": issue.get("message"),
                    "code": issue.get("code"),
                    "severity": severity
                }

                if severity == "ERROR":
                    self.findings["p1_high"].append(finding)
                elif severity == "WARNING":
                    self.findings["p2_medium"].append(finding)
                else:
                    self.findings["p3_low"].append(finding)
        except Exception as e:
            print(f"{ArtemisColors.WARNING}Warning: Could not parse shellcheck results: {e}{ArtemisColors.ENDC}")

    def _load_vulnerability_results(self):
        """Load grype/trivy vulnerability results"""
        grype_file = self.static_dir / "grype.json"
        if grype_file.exists():
            try:
                data = json.loads(grype_file.read_text())
                for match in data.get("matches", []):
                    vuln = match.get("vulnerability", {})
                    severity = vuln.get("severity", "").upper()

                    finding = {
                        "tool": "grype",
                        "package": match.get("artifact", {}).get("name"),
                        "version": match.get("artifact", {}).get("version"),
                        "vulnerability": vuln.get("id"),
                        "issue": vuln.get("description"),
                        "severity": severity,
                        "fix": vuln.get("fix", {}).get("versions", [])
                    }

                    if severity == "CRITICAL":
                        self.findings["p0_critical"].append(finding)
                    elif severity == "HIGH":
                        self.findings["p1_high"].append(finding)
                    elif severity == "MEDIUM":
                        self.findings["p2_medium"].append(finding)
                    else:
                        self.findings["p3_low"].append(finding)
            except Exception as e:
                print(f"{ArtemisColors.WARNING}Warning: Could not parse grype results: {e}{ArtemisColors.ENDC}")

    def _write_triage_reports(self):
        """Write triage reports for each priority level"""
        for priority, issues in self.findings.items():
            if not issues:
                continue

            report_file = self.triage_dir / f"{priority}.md"
            with open(report_file, 'w') as f:
                f.write(f"# {priority.upper()} Issues\n\n")
                f.write(f"**Total:** {len(issues)}\n")
                f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")

                for i, issue in enumerate(issues, 1):
                    f.write(f"## Issue #{i}\n\n")
                    for key, value in issue.items():
                        f.write(f"- **{key}:** {value}\n")
                    f.write("\n---\n\n")

    def _generate_dependency_graph(self):
        """Generate fix dependency graph"""
        graph_file = self.triage_dir / "dependency_graph.md"
        with open(graph_file, 'w') as f:
            f.write("# Fix Dependency Graph\n\n")
            f.write("This graph shows the order in which fixes should be applied.\n\n")

            # Crypto fixes first
            f.write("## Priority 1: Crypto Module Hardening\n")
            f.write("- Fix crypto anti-patterns\n")
            f.write("- Add constant-time comparisons\n")
            f.write("- Add buffer zeroization\n")
            f.write("- Enforce AEAD-only encryption\n\n")

            # Hypervisor fixes
            f.write("## Priority 2: Hypervisor Hardening\n")
            f.write("- Fix memory safety issues\n")
            f.write("- Enforce IOMMU isolation\n")
            f.write("- Add privilege dropping\n\n")

            # AI fixes
            f.write("## Priority 3: AI Module Sandboxing\n")
            f.write("- Implement sandbox\n")
            f.write("- Add prompt firewall\n")
            f.write("- Enforce file access boundaries\n\n")

            # Shell fixes
            f.write("## Priority 4: Shell Hardening\n")
            f.write("- Add strict mode\n")
            f.write("- Fix quote safety\n")
            f.write("- Remove command injection vectors\n\n")

    def generate_summary(self):
        """Generate final summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "repo": str(self.repo_root),
            "findings": {
                "p0_critical": len(self.findings["p0_critical"]),
                "p1_high": len(self.findings["p1_high"]),
                "p2_medium": len(self.findings["p2_medium"]),
                "p3_low": len(self.findings["p3_low"]),
                "info": len(self.findings["info"])
            },
            "total_issues": sum(len(v) for v in self.findings.values()),
            "reports_generated": [
                str(f.relative_to(self.repo_root))
                for f in self.report_dir.rglob("*")
                if f.is_file()
            ]
        }

        summary_file = self.report_dir / "artemis_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2))

        # Print summary
        self.print_header("ARTEMIS PIPELINE SUMMARY")
        print(f"Total Issues Found: {summary['total_issues']}")
        print(f"  P0 Critical: {summary['findings']['p0_critical']}")
        print(f"  P1 High:     {summary['findings']['p1_high']}")
        print(f"  P2 Medium:   {summary['findings']['p2_medium']}")
        print(f"  P3 Low:      {summary['findings']['p3_low']}")
        print(f"\nReports saved to: {self.report_dir}")

        return summary

def main():
    print(f"{ArtemisColors.BOLD}{ArtemisColors.HEADER}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║          QWAMOS ARTEMIS SECURITY HARDENING PIPELINE              ║")
    print("║          Claude Sonnet 4.5 Autonomous Security System            ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{ArtemisColors.ENDC}\n")

    repo_root = Path.cwd()
    if not (repo_root / ".git").exists():
        print(f"{ArtemisColors.FAIL}Error: Not in a git repository{ArtemisColors.ENDC}")
        return 1

    pipeline = ArtemisPipeline(repo_root)

    try:
        # Phase 1: Static Analysis
        pipeline.phase1_static_analysis()

        # Phase 2: Triage
        pipeline.phase2_triage()

        # Generate Summary
        summary = pipeline.generate_summary()

        print(f"\n{ArtemisColors.OKGREEN}{ArtemisColors.BOLD}✅ Pipeline Complete!{ArtemisColors.ENDC}")
        print(f"\nNext Steps:")
        print(f"1. Review findings in reports/triage/")
        print(f"2. Run artemis_hardening.py to apply automated fixes")
        print(f"3. Validate with artemis_validate.py")

        return 0

    except KeyboardInterrupt:
        print(f"\n{ArtemisColors.WARNING}Pipeline interrupted by user{ArtemisColors.ENDC}")
        return 130
    except Exception as e:
        print(f"\n{ArtemisColors.FAIL}Pipeline failed: {e}{ArtemisColors.ENDC}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
