#!/usr/bin/env python3
"""
QWAMOS Phase 9: Triple-AI Security Auditor

Comprehensive security auditing system requiring approval from all 3 AIs:
- Kali GPT: Vulnerability scanning and threat modeling
- Claude: Architecture security review
- ChatGPT: Dependency audit and manifest analysis

ALL 3 AIs must score >=90/100 for code to pass.

@module security_auditor
@version 1.0.0
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re

logger = logging.getLogger('SecurityAuditor')


class AuditType(Enum):
    """Types of security audits performed"""
    VULNERABILITY_SCAN = "vulnerability_scan"
    ARCHITECTURE_SECURITY = "architecture_security"
    DEPENDENCY_AUDIT = "dependency_audit"
    MANIFEST_ANALYSIS = "manifest_analysis"
    PERMISSION_REVIEW = "permission_review"
    CRYPTO_ANALYSIS = "crypto_analysis"
    NETWORK_SECURITY = "network_security"


class VulnerabilitySeverity(Enum):
    """Severity levels for vulnerabilities"""
    CRITICAL = "CRITICAL"  # Score penalty: -30
    HIGH = "HIGH"          # Score penalty: -20
    MEDIUM = "MEDIUM"      # Score penalty: -10
    LOW = "LOW"            # Score penalty: -5
    INFO = "INFO"          # Score penalty: 0


@dataclass
class SecurityVulnerability:
    """Single security vulnerability detected"""
    severity: VulnerabilitySeverity
    audit_type: AuditType
    file: str
    line: Optional[int]
    description: str
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID
    recommendation: str = ""
    detected_by_ai: str = ""  # kali_gpt, claude, chatgpt


@dataclass
class AISecurityAudit:
    """Security audit result from single AI"""
    ai_name: str  # kali_gpt, claude, chatgpt
    score: float  # 0-100
    vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    audit_timestamp: str = ""
    analysis_summary: str = ""
    pass_status: bool = False


@dataclass
class TripleAuditResult:
    """Combined result from all 3 AI security audits"""
    kali_gpt_audit: AISecurityAudit
    claude_audit: AISecurityAudit
    chatgpt_audit: AISecurityAudit

    weighted_score: float = 0.0
    all_pass: bool = False
    fail_conditions_triggered: List[str] = field(default_factory=list)

    total_vulnerabilities: int = 0
    critical_vulnerabilities: int = 0
    high_vulnerabilities: int = 0

    audit_summary: str = ""


class TripleAISecurityAuditor:
    """
    Triple-AI security auditor with consensus requirement.

    Architecture:
    - Kali GPT: Vulnerability scanning, penetration testing perspective (40% weight)
    - Claude: Architecture security, design patterns, best practices (35% weight)
    - ChatGPT: Dependency audit, manifest analysis, code quality (25% weight)

    Pass Criteria:
    - ALL 3 AIs must score >= 90/100
    - NO critical fail conditions
    - Weighted average >= 90/100
    """

    def __init__(self, config: Dict, kali_gpt, claude, chatgpt):
        self.config = config
        self.kali_gpt = kali_gpt
        self.claude = claude
        self.chatgpt = chatgpt

        # Load thresholds from config
        self.min_score_per_ai = config.get('security_audit', {}).get('min_score_per_ai', 90.0)
        self.fail_conditions = config.get('security_audit', {}).get('fail_conditions', [])

        # AI weights for weighted scoring
        self.ai_weights = {
            'kali_gpt': 0.40,
            'claude': 0.35,
            'chatgpt': 0.25
        }

    async def perform_triple_audit(
        self,
        code: Dict[str, str],
        manifest: str,
        dependencies: List[str],
        user_request: str
    ) -> TripleAuditResult:
        """
        Perform triple-AI security audit.

        Args:
            code: Generated code files {filename: content}
            manifest: AndroidManifest.xml content
            dependencies: List of dependencies
            user_request: Original user request

        Returns:
            TripleAuditResult with all audit findings
        """
        logger.info("Starting Triple-AI Security Audit...")

        # Run all 3 audits in parallel
        kali_audit_task = self._kali_gpt_audit(code, manifest, dependencies, user_request)
        claude_audit_task = self._claude_audit(code, manifest, dependencies, user_request)
        chatgpt_audit_task = self._chatgpt_audit(code, manifest, dependencies, user_request)

        kali_audit, claude_audit, chatgpt_audit = await asyncio.gather(
            kali_audit_task,
            claude_audit_task,
            chatgpt_audit_task
        )

        # Calculate weighted score
        weighted_score = (
            kali_audit.score * self.ai_weights['kali_gpt'] +
            claude_audit.score * self.ai_weights['claude'] +
            chatgpt_audit.score * self.ai_weights['chatgpt']
        )

        # Check if all AIs pass
        all_pass = (
            kali_audit.pass_status and
            claude_audit.pass_status and
            chatgpt_audit.pass_status and
            weighted_score >= self.min_score_per_ai
        )

        # Aggregate vulnerabilities
        all_vulnerabilities = (
            kali_audit.vulnerabilities +
            claude_audit.vulnerabilities +
            chatgpt_audit.vulnerabilities
        )

        critical_count = sum(
            1 for v in all_vulnerabilities
            if v.severity == VulnerabilitySeverity.CRITICAL
        )
        high_count = sum(
            1 for v in all_vulnerabilities
            if v.severity == VulnerabilitySeverity.HIGH
        )

        # Check fail conditions
        fail_conditions = self._check_fail_conditions(code, manifest, all_vulnerabilities)

        if fail_conditions:
            all_pass = False

        # Generate audit summary
        audit_summary = self._generate_audit_summary(
            kali_audit, claude_audit, chatgpt_audit,
            weighted_score, all_pass, fail_conditions
        )

        result = TripleAuditResult(
            kali_gpt_audit=kali_audit,
            claude_audit=claude_audit,
            chatgpt_audit=chatgpt_audit,
            weighted_score=weighted_score,
            all_pass=all_pass,
            fail_conditions_triggered=fail_conditions,
            total_vulnerabilities=len(all_vulnerabilities),
            critical_vulnerabilities=critical_count,
            high_vulnerabilities=high_count,
            audit_summary=audit_summary
        )

        logger.info(f"Triple-AI Security Audit Complete: {'PASS' if all_pass else 'FAIL'}")
        logger.info(f"  Kali GPT: {kali_audit.score:.1f}/100")
        logger.info(f"  Claude:   {claude_audit.score:.1f}/100")
        logger.info(f"  ChatGPT:  {chatgpt_audit.score:.1f}/100")
        logger.info(f"  Weighted: {weighted_score:.1f}/100")
        logger.info(f"  Vulnerabilities: {len(all_vulnerabilities)} ({critical_count} critical, {high_count} high)")

        return result

    async def _kali_gpt_audit(
        self,
        code: Dict[str, str],
        manifest: str,
        dependencies: List[str],
        user_request: str
    ) -> AISecurityAudit:
        """
        Kali GPT security audit - penetration testing perspective.

        Focus:
        - Vulnerability scanning (SQL injection, XSS, command injection)
        - Threat modeling
        - Minimal permissions validation
        - Cryptographic security
        """
        logger.info("Kali GPT: Starting security audit...")

        vulnerabilities = []
        score = 100.0

        # 1. Vulnerability Scanning
        vuln_scan_results = await self._vulnerability_scan(code, 'kali_gpt')
        vulnerabilities.extend(vuln_scan_results)

        # 2. Permission Analysis
        permission_vulns = self._analyze_permissions(manifest, user_request, 'kali_gpt')
        vulnerabilities.extend(permission_vulns)

        # 3. Cryptographic Analysis
        crypto_vulns = self._analyze_crypto(code, 'kali_gpt')
        vulnerabilities.extend(crypto_vulns)

        # 4. Network Security
        network_vulns = self._analyze_network_security(code, manifest, 'kali_gpt')
        vulnerabilities.extend(network_vulns)

        # Calculate score penalties
        for vuln in vulnerabilities:
            if vuln.severity == VulnerabilitySeverity.CRITICAL:
                score -= 30
            elif vuln.severity == VulnerabilitySeverity.HIGH:
                score -= 20
            elif vuln.severity == VulnerabilitySeverity.MEDIUM:
                score -= 10
            elif vuln.severity == VulnerabilitySeverity.LOW:
                score -= 5

        score = max(0.0, score)

        pass_status = score >= self.min_score_per_ai

        analysis_summary = (
            f"Kali GPT identified {len(vulnerabilities)} security issues. "
            f"Focus areas: vulnerability scanning, threat modeling, crypto analysis."
        )

        return AISecurityAudit(
            ai_name='kali_gpt',
            score=score,
            vulnerabilities=vulnerabilities,
            analysis_summary=analysis_summary,
            pass_status=pass_status
        )

    async def _claude_audit(
        self,
        code: Dict[str, str],
        manifest: str,
        dependencies: List[str],
        user_request: str
    ) -> AISecurityAudit:
        """
        Claude security audit - architecture and design perspective.

        Focus:
        - Architecture security patterns
        - Secure design principles
        - Code quality and maintainability
        - Performance security
        """
        logger.info("Claude: Starting architecture security review...")

        vulnerabilities = []
        score = 100.0

        # 1. Architecture Security Review
        arch_vulns = self._review_architecture_security(code, 'claude')
        vulnerabilities.extend(arch_vulns)

        # 2. Design Pattern Analysis
        design_vulns = self._analyze_design_patterns(code, 'claude')
        vulnerabilities.extend(design_vulns)

        # 3. Input Validation Review
        input_vulns = self._review_input_validation(code, 'claude')
        vulnerabilities.extend(input_vulns)

        # 4. Error Handling Review
        error_vulns = self._review_error_handling(code, 'claude')
        vulnerabilities.extend(error_vulns)

        # Calculate score penalties
        for vuln in vulnerabilities:
            if vuln.severity == VulnerabilitySeverity.CRITICAL:
                score -= 30
            elif vuln.severity == VulnerabilitySeverity.HIGH:
                score -= 20
            elif vuln.severity == VulnerabilitySeverity.MEDIUM:
                score -= 10
            elif vuln.severity == VulnerabilitySeverity.LOW:
                score -= 5

        score = max(0.0, score)

        pass_status = score >= self.min_score_per_ai

        analysis_summary = (
            f"Claude identified {len(vulnerabilities)} architecture/design issues. "
            f"Focus areas: secure design patterns, input validation, error handling."
        )

        return AISecurityAudit(
            ai_name='claude',
            score=score,
            vulnerabilities=vulnerabilities,
            analysis_summary=analysis_summary,
            pass_status=pass_status
        )

    async def _chatgpt_audit(
        self,
        code: Dict[str, str],
        manifest: str,
        dependencies: List[str],
        user_request: str
    ) -> AISecurityAudit:
        """
        ChatGPT security audit - dependency and manifest perspective.

        Focus:
        - Dependency vulnerabilities
        - Manifest security configuration
        - Third-party library risks
        - Code quality issues
        """
        logger.info("ChatGPT: Starting dependency and manifest audit...")

        vulnerabilities = []
        score = 100.0

        # 1. Dependency Audit
        dep_vulns = await self._audit_dependencies(dependencies, 'chatgpt')
        vulnerabilities.extend(dep_vulns)

        # 2. Manifest Security Analysis
        manifest_vulns = self._analyze_manifest_security(manifest, 'chatgpt')
        vulnerabilities.extend(manifest_vulns)

        # 3. Code Quality Security Review
        quality_vulns = self._review_code_quality_security(code, 'chatgpt')
        vulnerabilities.extend(quality_vulns)

        # Calculate score penalties
        for vuln in vulnerabilities:
            if vuln.severity == VulnerabilitySeverity.CRITICAL:
                score -= 30
            elif vuln.severity == VulnerabilitySeverity.HIGH:
                score -= 20
            elif vuln.severity == VulnerabilitySeverity.MEDIUM:
                score -= 10
            elif vuln.severity == VulnerabilitySeverity.LOW:
                score -= 5

        score = max(0.0, score)

        pass_status = score >= self.min_score_per_ai

        analysis_summary = (
            f"ChatGPT identified {len(vulnerabilities)} dependency/manifest issues. "
            f"Focus areas: dependency vulnerabilities, manifest security, code quality."
        )

        return AISecurityAudit(
            ai_name='chatgpt',
            score=score,
            vulnerabilities=vulnerabilities,
            analysis_summary=analysis_summary,
            pass_status=pass_status
        )

    async def _vulnerability_scan(self, code: Dict[str, str], ai_name: str) -> List[SecurityVulnerability]:
        """Scan for common vulnerabilities (OWASP Top 10)"""
        vulnerabilities = []

        for filename, content in code.items():
            # SQL Injection check
            if re.search(r'\.execSQL\s*\(\s*["\'].*?\+', content):
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.CRITICAL,
                    audit_type=AuditType.VULNERABILITY_SCAN,
                    file=filename,
                    line=None,
                    description="Potential SQL injection - string concatenation in SQL query",
                    cwe_id="CWE-89",
                    recommendation="Use parameterized queries with prepared statements",
                    detected_by_ai=ai_name
                ))

            # Command Injection check
            if re.search(r'Runtime\.getRuntime\(\)\.exec\s*\(', content):
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.HIGH,
                    audit_type=AuditType.VULNERABILITY_SCAN,
                    file=filename,
                    line=None,
                    description="Command execution detected - potential command injection",
                    cwe_id="CWE-78",
                    recommendation="Validate and sanitize all user input before executing commands",
                    detected_by_ai=ai_name
                ))

            # Hardcoded secrets check
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ]
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        severity=VulnerabilitySeverity.CRITICAL,
                        audit_type=AuditType.VULNERABILITY_SCAN,
                        file=filename,
                        line=None,
                        description="Hardcoded secret detected in source code",
                        cwe_id="CWE-798",
                        recommendation="Store secrets in Android Keystore or secure configuration",
                        detected_by_ai=ai_name
                    ))
                    break

            # Insecure random number generation
            if 'java.util.Random' in content and 'crypto' in filename.lower():
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.HIGH,
                    audit_type=AuditType.CRYPTO_ANALYSIS,
                    file=filename,
                    line=None,
                    description="Insecure random number generator used for cryptographic operations",
                    cwe_id="CWE-330",
                    recommendation="Use SecureRandom for cryptographic operations",
                    detected_by_ai=ai_name
                ))

        return vulnerabilities

    def _analyze_permissions(
        self,
        manifest: str,
        user_request: str,
        ai_name: str
    ) -> List[SecurityVulnerability]:
        """Analyze Android permissions for over-privileged access"""
        vulnerabilities = []

        # Extract permissions from manifest
        permissions = re.findall(r'<uses-permission\s+android:name="([^"]+)"', manifest)

        # Check for INTERNET permission when not explicitly requested
        if 'android.permission.INTERNET' in permissions:
            if 'internet' not in user_request.lower() and 'network' not in user_request.lower():
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.HIGH,
                    audit_type=AuditType.PERMISSION_REVIEW,
                    file='AndroidManifest.xml',
                    line=None,
                    description="INTERNET permission granted but not explicitly requested by user",
                    cwe_id="CWE-250",
                    recommendation="Remove INTERNET permission if not needed",
                    detected_by_ai=ai_name
                ))

        # Check for dangerous permissions
        dangerous_permissions = [
            'READ_EXTERNAL_STORAGE',
            'WRITE_EXTERNAL_STORAGE',
            'CAMERA',
            'RECORD_AUDIO',
            'ACCESS_FINE_LOCATION',
            'READ_CONTACTS',
            'READ_SMS'
        ]

        for perm in permissions:
            perm_name = perm.split('.')[-1]
            if perm_name in dangerous_permissions:
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.MEDIUM,
                    audit_type=AuditType.PERMISSION_REVIEW,
                    file='AndroidManifest.xml',
                    line=None,
                    description=f"Dangerous permission requested: {perm_name}",
                    cwe_id="CWE-250",
                    recommendation=f"Ensure {perm_name} is absolutely necessary for app functionality",
                    detected_by_ai=ai_name
                ))

        return vulnerabilities

    def _analyze_crypto(self, code: Dict[str, str], ai_name: str) -> List[SecurityVulnerability]:
        """Analyze cryptographic implementation"""
        vulnerabilities = []

        for filename, content in code.items():
            # Weak encryption algorithms
            weak_algorithms = ['DES', 'RC4', 'MD5', 'SHA1']
            for algo in weak_algorithms:
                if algo in content:
                    vulnerabilities.append(SecurityVulnerability(
                        severity=VulnerabilitySeverity.HIGH,
                        audit_type=AuditType.CRYPTO_ANALYSIS,
                        file=filename,
                        line=None,
                        description=f"Weak cryptographic algorithm detected: {algo}",
                        cwe_id="CWE-327",
                        recommendation="Use AES-256-GCM or ChaCha20-Poly1305 for encryption",
                        detected_by_ai=ai_name
                    ))

            # ECB mode (insecure)
            if 'ECB' in content:
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.HIGH,
                    audit_type=AuditType.CRYPTO_ANALYSIS,
                    file=filename,
                    line=None,
                    description="ECB cipher mode detected (insecure)",
                    cwe_id="CWE-327",
                    recommendation="Use GCM or CBC mode with proper IV",
                    detected_by_ai=ai_name
                ))

        return vulnerabilities

    def _analyze_network_security(
        self,
        code: Dict[str, str],
        manifest: str,
        ai_name: str
    ) -> List[SecurityVulnerability]:
        """Analyze network security configuration"""
        vulnerabilities = []

        for filename, content in code.items():
            # Insecure HTTP connections
            if re.search(r'http://[^"\']+', content):
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.MEDIUM,
                    audit_type=AuditType.NETWORK_SECURITY,
                    file=filename,
                    line=None,
                    description="Insecure HTTP connection detected",
                    cwe_id="CWE-319",
                    recommendation="Use HTTPS for all network communications",
                    detected_by_ai=ai_name
                ))

            # SSL certificate validation bypass
            if 'TrustAllCertificates' in content or 'trustAllHosts' in content:
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.CRITICAL,
                    audit_type=AuditType.NETWORK_SECURITY,
                    file=filename,
                    line=None,
                    description="SSL certificate validation bypass detected",
                    cwe_id="CWE-295",
                    recommendation="Implement proper certificate validation",
                    detected_by_ai=ai_name
                ))

        return vulnerabilities

    def _review_architecture_security(
        self,
        code: Dict[str, str],
        ai_name: str
    ) -> List[SecurityVulnerability]:
        """Review architectural security patterns"""
        vulnerabilities = []

        # This would integrate with Claude's architecture analysis
        # For now, basic checks

        for filename, content in code.items():
            # Missing authentication checks
            if 'Activity' in content and 'onCreate' in content:
                if 'authentication' not in content.lower() and 'login' not in content.lower():
                    vulnerabilities.append(SecurityVulnerability(
                        severity=VulnerabilitySeverity.LOW,
                        audit_type=AuditType.ARCHITECTURE_SECURITY,
                        file=filename,
                        line=None,
                        description="Activity may lack authentication checks",
                        cwe_id="CWE-306",
                        recommendation="Implement authentication checks if handling sensitive data",
                        detected_by_ai=ai_name
                    ))

        return vulnerabilities

    def _analyze_design_patterns(
        self,
        code: Dict[str, str],
        ai_name: str
    ) -> List[SecurityVulnerability]:
        """Analyze security-relevant design patterns"""
        vulnerabilities = []

        # Check for singleton pattern with mutable state
        for filename, content in code.items():
            if 'static' in content and 'getInstance' in content:
                if 'synchronized' not in content:
                    vulnerabilities.append(SecurityVulnerability(
                        severity=VulnerabilitySeverity.LOW,
                        audit_type=AuditType.ARCHITECTURE_SECURITY,
                        file=filename,
                        line=None,
                        description="Singleton pattern without thread synchronization",
                        cwe_id="CWE-543",
                        recommendation="Use synchronized keyword or double-checked locking",
                        detected_by_ai=ai_name
                    ))

        return vulnerabilities

    def _review_input_validation(
        self,
        code: Dict[str, str],
        ai_name: str
    ) -> List[SecurityVulnerability]:
        """Review input validation mechanisms"""
        vulnerabilities = []

        for filename, content in code.items():
            # Check for user input handling
            if 'EditText' in content or 'getUserInput' in content:
                if 'validate' not in content.lower() and 'sanitize' not in content.lower():
                    vulnerabilities.append(SecurityVulnerability(
                        severity=VulnerabilitySeverity.MEDIUM,
                        audit_type=AuditType.VULNERABILITY_SCAN,
                        file=filename,
                        line=None,
                        description="User input handling without visible validation",
                        cwe_id="CWE-20",
                        recommendation="Implement input validation and sanitization",
                        detected_by_ai=ai_name
                    ))

        return vulnerabilities

    def _review_error_handling(
        self,
        code: Dict[str, str],
        ai_name: str
    ) -> List[SecurityVulnerability]:
        """Review error handling for information leakage"""
        vulnerabilities = []

        for filename, content in code.items():
            # Check for stack trace exposure
            if 'printStackTrace()' in content:
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.LOW,
                    audit_type=AuditType.VULNERABILITY_SCAN,
                    file=filename,
                    line=None,
                    description="printStackTrace() exposes sensitive information",
                    cwe_id="CWE-209",
                    recommendation="Log errors securely without exposing stack traces to users",
                    detected_by_ai=ai_name
                ))

        return vulnerabilities

    async def _audit_dependencies(
        self,
        dependencies: List[str],
        ai_name: str
    ) -> List[SecurityVulnerability]:
        """Audit dependencies for known vulnerabilities"""
        vulnerabilities = []

        # Check for known vulnerable libraries
        vulnerable_libs = {
            'commons-collections:3.2.1': 'Known deserialization vulnerability',
            'log4j:1.2': 'Log4Shell vulnerability family',
            'okhttp:2.': 'Outdated version with known vulnerabilities'
        }

        for dep in dependencies:
            for vuln_lib, vuln_desc in vulnerable_libs.items():
                if vuln_lib in dep:
                    vulnerabilities.append(SecurityVulnerability(
                        severity=VulnerabilitySeverity.HIGH,
                        audit_type=AuditType.DEPENDENCY_AUDIT,
                        file='build.gradle',
                        line=None,
                        description=f"Vulnerable dependency: {dep} - {vuln_desc}",
                        cwe_id="CWE-1035",
                        recommendation="Update to latest secure version",
                        detected_by_ai=ai_name
                    ))

        return vulnerabilities

    def _analyze_manifest_security(
        self,
        manifest: str,
        ai_name: str
    ) -> List[SecurityVulnerability]:
        """Analyze AndroidManifest.xml for security issues"""
        vulnerabilities = []

        # Check for debuggable flag in production
        if 'android:debuggable="true"' in manifest:
            vulnerabilities.append(SecurityVulnerability(
                severity=VulnerabilitySeverity.HIGH,
                audit_type=AuditType.MANIFEST_ANALYSIS,
                file='AndroidManifest.xml',
                line=None,
                description="Debuggable flag enabled (production risk)",
                cwe_id="CWE-489",
                recommendation="Set debuggable=false for production builds",
                detected_by_ai=ai_name
            ))

        # Check for exported components without permissions
        if 'android:exported="true"' in manifest:
            if 'android:permission' not in manifest:
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.MEDIUM,
                    audit_type=AuditType.MANIFEST_ANALYSIS,
                    file='AndroidManifest.xml',
                    line=None,
                    description="Exported component without permission protection",
                    cwe_id="CWE-927",
                    recommendation="Add permission requirements to exported components",
                    detected_by_ai=ai_name
                ))

        # Check for cleartext traffic allowed
        if 'android:usesCleartextTraffic="true"' in manifest:
            vulnerabilities.append(SecurityVulnerability(
                severity=VulnerabilitySeverity.MEDIUM,
                audit_type=AuditType.MANIFEST_ANALYSIS,
                file='AndroidManifest.xml',
                line=None,
                description="Cleartext traffic allowed (HTTP)",
                cwe_id="CWE-319",
                recommendation="Disable cleartext traffic, use HTTPS only",
                detected_by_ai=ai_name
            ))

        return vulnerabilities

    def _review_code_quality_security(
        self,
        code: Dict[str, str],
        ai_name: str
    ) -> List[SecurityVulnerability]:
        """Review code quality issues that impact security"""
        vulnerabilities = []

        for filename, content in code.items():
            # Check for TODO/FIXME comments in security-critical areas
            if re.search(r'//\s*(TODO|FIXME).*?(security|auth|encrypt|password)', content, re.IGNORECASE):
                vulnerabilities.append(SecurityVulnerability(
                    severity=VulnerabilitySeverity.MEDIUM,
                    audit_type=AuditType.VULNERABILITY_SCAN,
                    file=filename,
                    line=None,
                    description="Unfinished security-related code (TODO/FIXME)",
                    cwe_id="CWE-1164",
                    recommendation="Complete all security-related implementations",
                    detected_by_ai=ai_name
                ))

        return vulnerabilities

    def _check_fail_conditions(
        self,
        code: Dict[str, str],
        manifest: str,
        vulnerabilities: List[SecurityVulnerability]
    ) -> List[str]:
        """Check for critical fail conditions"""
        fail_conditions = []

        # Check each configured fail condition
        for condition in self.fail_conditions:
            if condition == "network_calls_without_permission":
                has_network_code = any(
                    'HttpURLConnection' in content or 'OkHttp' in content
                    for content in code.values()
                )
                has_internet_perm = 'android.permission.INTERNET' in manifest

                if has_network_code and not has_internet_perm:
                    fail_conditions.append("Network calls without INTERNET permission")

            elif condition == "suspicious_permissions":
                suspicious = ['SEND_SMS', 'CALL_PHONE', 'SYSTEM_ALERT_WINDOW']
                for perm in suspicious:
                    if perm in manifest:
                        fail_conditions.append(f"Suspicious permission: {perm}")

            elif condition == "known_vulnerabilities":
                critical_vulns = [
                    v for v in vulnerabilities
                    if v.severity == VulnerabilitySeverity.CRITICAL
                ]
                if critical_vulns:
                    fail_conditions.append(f"{len(critical_vulns)} critical vulnerabilities detected")

            elif condition == "insecure_crypto":
                insecure_patterns = ['DES', 'RC4', 'MD5', 'ECB']
                for pattern in insecure_patterns:
                    if any(pattern in content for content in code.values()):
                        fail_conditions.append(f"Insecure cryptography: {pattern}")
                        break

            elif condition == "hardcoded_secrets":
                secret_patterns = ['password =', 'api_key =', 'secret =']
                for pattern in secret_patterns:
                    if any(pattern in content.lower() for content in code.values()):
                        fail_conditions.append("Hardcoded secrets detected")
                        break

        return fail_conditions

    def _generate_audit_summary(
        self,
        kali_audit: AISecurityAudit,
        claude_audit: AISecurityAudit,
        chatgpt_audit: AISecurityAudit,
        weighted_score: float,
        all_pass: bool,
        fail_conditions: List[str]
    ) -> str:
        """Generate human-readable audit summary"""

        summary = f"""
═══════════════════════════════════════════════════════════════
                TRIPLE-AI SECURITY AUDIT REPORT
═══════════════════════════════════════════════════════════════

OVERALL RESULT: {'✅ PASS' if all_pass else '❌ FAIL'}

INDIVIDUAL AI SCORES:
  Kali GPT (40% weight):  {kali_audit.score:.1f}/100  {'✅' if kali_audit.pass_status else '❌'}
  Claude   (35% weight):  {claude_audit.score:.1f}/100  {'✅' if claude_audit.pass_status else '❌'}
  ChatGPT  (25% weight):  {chatgpt_audit.score:.1f}/100  {'✅' if chatgpt_audit.pass_status else '❌'}

  Weighted Average:       {weighted_score:.1f}/100  {'✅' if weighted_score >= 90 else '❌'}

VULNERABILITY SUMMARY:
  Total Vulnerabilities:   {len(kali_audit.vulnerabilities) + len(claude_audit.vulnerabilities) + len(chatgpt_audit.vulnerabilities)}
  Critical:                {sum(1 for v in kali_audit.vulnerabilities + claude_audit.vulnerabilities + chatgpt_audit.vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL)}
  High:                    {sum(1 for v in kali_audit.vulnerabilities + claude_audit.vulnerabilities + chatgpt_audit.vulnerabilities if v.severity == VulnerabilitySeverity.HIGH)}
  Medium:                  {sum(1 for v in kali_audit.vulnerabilities + claude_audit.vulnerabilities + chatgpt_audit.vulnerabilities if v.severity == VulnerabilitySeverity.MEDIUM)}
  Low:                     {sum(1 for v in kali_audit.vulnerabilities + claude_audit.vulnerabilities + chatgpt_audit.vulnerabilities if v.severity == VulnerabilitySeverity.LOW)}

FAIL CONDITIONS:
  {f"{'  - ' + chr(10) + '  - '.join(fail_conditions)}" if fail_conditions else "  None"}

AI ANALYSIS SUMMARIES:

Kali GPT:
  {kali_audit.analysis_summary}

Claude:
  {claude_audit.analysis_summary}

ChatGPT:
  {chatgpt_audit.analysis_summary}

═══════════════════════════════════════════════════════════════
"""

        return summary
