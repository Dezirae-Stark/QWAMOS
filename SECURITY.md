# Security Policy

**QWAMOS Security Team**
**Last Updated:** 2025-11-07
**Version:** v1.0.0-qbamos-gold

---

## Responsible Disclosure Policy

The QWAMOS project takes security vulnerabilities seriously. We appreciate the security research community's efforts to responsibly disclose issues and will work with researchers to verify, reproduce, and address security vulnerabilities.

---

## Reporting a Vulnerability

If you discover a security vulnerability in QWAMOS, please report it responsibly.

### Contact Information

**Primary Contact:**
- **Email:** clockwork.halo@tutanota.de
- **PGP/GPG Fingerprint:** `18C4E89E37D5ECD392F52E85269CD0658D8BD942DCF33BE4E37CC94933E4C4D2`
- **PGP Key Algorithm:** Ed448

**Encrypted Communication:**
We strongly encourage the use of PGP-encrypted email for vulnerability reports. You can find our public key at:
- **GitHub:** https://github.com/Dezirae-Stark/QWAMOS/blob/main/gpg_public_key.asc
- **Keyserver:** (Upload pending)

---

## What to Include in Your Report

Please provide as much information as possible to help us understand and reproduce the vulnerability:

### Required Information
1. **Vulnerability Description:** Clear explanation of the security issue
2. **Affected Component:** Which QWAMOS component or module is affected
3. **Version:** QWAMOS version number (e.g., v1.0.0-alpha, commit hash)
4. **Impact Assessment:** Potential security impact (confidentiality, integrity, availability)
5. **Attack Scenario:** Description of how an attacker could exploit this vulnerability

### Optional but Helpful Information
6. **Proof of Concept:** Steps to reproduce the vulnerability
7. **Exploit Code:** Working exploit code (if available and safe to share)
8. **Suggested Fix:** Your recommendation for remediation (if available)
9. **CVE References:** Related CVE numbers (if applicable)
10. **Screenshots/Logs:** Visual evidence or log files demonstrating the issue

---

## Response Timeline

We commit to the following response timeline for security vulnerability reports:

| Stage | Timeline | Description |
|-------|----------|-------------|
| **Initial Acknowledgment** | Within 7 days | Confirm receipt of your report |
| **Initial Assessment** | Within 14 days | Triage severity and confirm vulnerability |
| **Progress Update** | Every 7 days | Regular updates on investigation progress |
| **Resolution Target** | Within 30 days | Fix critical vulnerabilities (may vary by severity) |
| **Public Disclosure** | 90 days | Coordinated disclosure after fix is released |

**Note:** Timeline may vary based on vulnerability complexity and severity. We will keep you informed throughout the process.

---

## Severity Classification

We use the following severity levels to prioritize vulnerabilities:

### **CRITICAL** (CVSS 9.0-10.0)
- Remote code execution without authentication
- Complete system compromise
- Bootloader/kernel privilege escalation
- TrustZone/TEE compromise
- Post-quantum crypto implementation flaws

**Resolution Target:** 7-14 days

---

### **HIGH** (CVSS 7.0-8.9)
- Authenticated remote code execution
- VM escape vulnerabilities
- Bypass of security isolation (Dom0 ↔ VM)
- Network anonymity leaks (Tor/I2P bypass)
- Hardware kill switch bypass

**Resolution Target:** 14-30 days

---

### **MEDIUM** (CVSS 4.0-6.9)
- Information disclosure (sensitive data)
- Denial of service attacks
- Privilege escalation (within VM)
- Authentication bypass (non-critical components)
- Cryptographic weaknesses (non-breaking)

**Resolution Target:** 30-60 days

---

### **LOW** (CVSS 0.1-3.9)
- Minor information disclosure
- UI/UX security issues
- Non-exploitable bugs
- Low-impact denial of service

**Resolution Target:** 60-90 days

---

## Scope

### In-Scope Components

The following QWAMOS components are within the scope of our security program:

#### **Core System**
- ✅ Bootloader (U-Boot) and secure boot chain
- ✅ Linux kernel and KVM hypervisor
- ✅ Dom0 policy manager and control bus
- ✅ VM isolation and compartmentalization

#### **Cryptography (Critical)**
- ✅ Post-quantum cryptography (Kyber-1024, ChaCha20, BLAKE3)
- ✅ Key derivation (Argon2id)
- ✅ Volume encryption (PostQuantumVolume)
- ✅ TrustZone/StrongBox integration
- ✅ Secure boot and attestation

#### **Network Security**
- ✅ Tor/I2P/DNSCrypt integration
- ✅ Network isolation and firewall rules
- ✅ IP leak detection
- ✅ Baseband isolation

#### **Hardware Security (Phase 10)**
- ✅ ML bootloader override system
- ✅ Firmware integrity monitor
- ✅ A/B partition isolation
- ✅ Hardware kill switch kernel driver

#### **AI & ML Systems**
- ✅ AI assistants (Kali GPT, Claude, ChatGPT)
- ✅ ML threat detection (network, filesystem, syscall)
- ✅ AI app builder and security auditor
- ✅ SecureType keyboard (PQ encryption, ML anomaly detection)

#### **User Interface**
- ✅ React Native UI components
- ✅ Flutter hypervisor UI
- ✅ Native module bridges (Java ↔ Python)

---

### Out-of-Scope

The following are **NOT** considered valid security vulnerabilities:

❌ **Upstream Dependencies**
- Vulnerabilities in Linux kernel, QEMU, Tor, etc. (report to upstream projects)
- CVEs in third-party libraries (we will track and patch, but not our vulnerability)

❌ **Physical Access Attacks**
- Physical hardware extraction (e.g., decapping chips)
- TEMPEST/RF side-channel attacks (requires specialized equipment)
- Rubber-hose cryptanalysis (coercion)

❌ **Theoretical Attacks**
- Attacks requiring >$1M budget or nation-state resources
- Quantum computer attacks (we use post-quantum crypto, but current quantum computers cannot break it)
- Supply chain attacks on hardware manufacturers

❌ **Social Engineering**
- Phishing attacks against users
- Credential theft via non-technical means

❌ **Non-Security Issues**
- Feature requests
- Performance issues (unless exploitable)
- UI/UX bugs (unless security impact)

---

## Public Disclosure Policy

### Coordinated Disclosure

We believe in **responsible coordinated disclosure**:

1. **Private Reporting:** Report vulnerability privately to our security team
2. **Investigation:** We investigate and develop a fix
3. **Fix Release:** Security patch released (versioned update)
4. **Public Disclosure:** Vulnerability details published 90 days after fix release
5. **Credit:** Researcher credited in security advisory (if desired)

### Disclosure Timeline

- **Day 0:** Vulnerability reported to QWAMOS security team
- **Day 7:** Initial acknowledgment and severity assessment
- **Day 14-30:** Fix development and testing
- **Day 30:** Security patch released to users
- **Day 90:** Public disclosure of vulnerability details
- **Day 120:** Full technical write-up (if applicable)

**Researcher Credit:**
- Your name (or pseudonym) listed in security advisory
- CVE assignment (if applicable)
- Acknowledgment in CHANGELOG and release notes

---

## Security Advisories

Published security advisories will be available at:

- **GitHub Security Advisories:** https://github.com/Dezirae-Stark/QWAMOS/security/advisories
- **CHANGELOG:** https://github.com/Dezirae-Stark/QWAMOS/blob/main/CHANGELOG.md
- **Mailing List:** (To be established)

**Advisory Format:**
- **CVE Number:** (if assigned)
- **Severity:** Critical/High/Medium/Low
- **Affected Versions:** (e.g., v1.0.0 - v1.0.5)
- **Fixed Version:** (e.g., v1.0.6)
- **Vulnerability Description:** Technical details
- **Impact:** Exploitation scenarios
- **Mitigation:** Workarounds (if available)
- **Credit:** Researcher attribution

---

## Security Hardening Recommendations

### For Users

If you are running QWAMOS, we recommend:

1. **Keep Updated:** Install security updates promptly
2. **Enable Strict Mode:** Use `STRICT_MODE=on` for maximum security
3. **Verify Signatures:** Always verify GPG signatures on releases
4. **Reproducible Builds:** Build from source and verify checksums
5. **Hardware Kill Switches:** Use physical kill switches for camera/mic/cellular
6. **Panic Gesture:** Configure and test emergency wipe gesture
7. **Duress Profiles:** Set up decoy user accounts

### For Developers

If you are contributing to QWAMOS:

1. **Code Review:** All code changes require peer review
2. **Static Analysis:** Run security linters (bandit, semgrep, shellcheck)
3. **Dependency Audits:** Verify all dependencies in SUPPLYCHAIN.md
4. **No Hardcoded Secrets:** Never commit API keys, passwords, or private keys
5. **Signed Commits:** Sign all Git commits with GPG
6. **Security Testing:** Run integration tests before merging
7. **Threat Modeling:** Consider adversarial scenarios

---

## Bug Bounty Program

**Status:** Currently unfunded

We do not currently offer a paid bug bounty program. However, we deeply appreciate security research and will:

- ✅ Publicly credit researchers (with permission)
- ✅ Provide CVE assignments for significant vulnerabilities
- ✅ Acknowledge contributions in release notes
- ✅ Future consideration for paid bounties if funding becomes available

---

## Past Security Incidents

**Status:** No security incidents to date.

This section will be updated if any security incidents occur.

---

## Security Best Practices in QWAMOS

### Implemented Security Measures

QWAMOS incorporates defense-in-depth security:

#### **Layer 1: Hardware Security**
- ARM TrustZone (StrongBox/Keymaster)
- Verified boot (measured boot with PCR logs)
- Hardware kill switches (camera, mic, cellular)
- Secure memory wiping (3-pass DoD 5220.22-M)

#### **Layer 2: Bootloader & Kernel**
- U-Boot signature verification
- Kyber-1024 post-quantum secure boot
- Kernel hardening (KASLR, stack canaries, W^X)
- SELinux + AppArmor + TOMOYO

#### **Layer 3: VM Isolation**
- 4-domain architecture (Dom0, Gateway, Workstation, Trusted UI)
- KVM hypervisor (hardware virtualization)
- Network isolation (workstation has NO network)
- Firewall with DEFAULT DROP

#### **Layer 4: Cryptography**
- Post-quantum encryption (Kyber-1024 + ChaCha20-Poly1305)
- Memory-hard KDF (Argon2id)
- Integrity verification (BLAKE3)
- Zero legacy crypto (no AES/RSA/ECDH in keyboard)

#### **Layer 5: Network Anonymity**
- Mandatory Tor/I2P egress
- DNS over Tor (no leaks)
- VPN cascading support
- IP leak detection (6-layer testing)

#### **Layer 6: ML Threat Detection**
- Real-time network anomaly detection
- File system monitoring (ransomware, malware)
- System call analysis (privilege escalation)
- Multi-AI coordinated response

#### **Layer 7: Emergency Protection**
- Panic gesture (instant wipe)
- Duress profiles (decoy data)
- Radio kill switch
- Session key destruction

---

## Security Audit Status

### Internal Audits
- ✅ Phase 4 (Post-Quantum Crypto): 6/6 tests passing
- ✅ Phase 7 (ML Threat Detection): 17/17 integration tests passing
- ✅ Phase 10 (Hardware Security): Complete implementation audit

### External Audits
- ⏳ Awaiting third-party security audit (target: Q1 2026)
- ⏳ Awaiting cryptographic review by security firm

### Continuous Security
- ✅ Dependabot enabled (GitHub dependency scanning)
- ✅ CodeQL analysis enabled
- ✅ Automated CVE tracking

---

## Security Hall of Fame

We will publicly recognize security researchers who responsibly disclose vulnerabilities:

**Hall of Fame:**
- (No entries yet - be the first!)

---

## Additional Resources

- **SUPPLYCHAIN.md:** Dependency verification and reproducible builds
- **OPS_GUIDE.md:** Operational security best practices
- **SUPPORT.md:** Troubleshooting and recovery procedures
- **Threat Model:** See README.md § "Threat Model & Protection Against State-Level Actors"

---

## Questions?

If you have questions about this security policy:

- **Email:** clockwork.halo@tutanota.de (PGP encrypted preferred)
- **GitHub Issues:** https://github.com/Dezirae-Stark/QWAMOS/issues (for non-sensitive questions only)

**Do NOT publicly disclose security vulnerabilities in GitHub Issues.**

---

## Changelog

- **2025-11-07:** Initial security policy published
- (Future updates will be listed here)

---

**Thank you for helping keep QWAMOS secure!**

---

© 2025 First Sterling Capital, LLC · QWAMOS Project
Licensed under AGPL-3.0
