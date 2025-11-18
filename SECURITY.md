# Security Policy

## Table of Contents

- [Supported Versions](#supported-versions)
- [Reporting a Vulnerability](#reporting-a-vulnerability)
- [Vulnerability Reporting Template](#vulnerability-reporting-template)
- [Response Timeline](#response-timeline)
- [Disclosure Policy](#disclosure-policy)
- [Security Researcher Safe Harbor](#security-researcher-safe-harbor)
- [Security Patch Guidelines](#security-patch-guidelines)
- [Known Sensitive Components](#known-sensitive-components)
- [Security Audits & CVEs](#security-audits--cves)
- [Security Best Practices](#security-best-practices)

---

## Supported Versions

QWAMOS follows a rolling release model with security updates applied to the latest stable version and the previous major version for a limited time.

| Version | Supported          | Security Updates Until |
| ------- | ------------------ | ---------------------- |
| main    | :white_check_mark: | Continuous (development) |
| v1.x.x  | :white_check_mark: | Current stable release |
| v0.x.x  | :x:                | No longer supported |
| < v0.1  | :x:                | No longer supported |

**Recommendation**: Always use the latest stable release for optimal security.

**End-of-Life Policy**:
- Major versions receive security updates for 12 months after the next major release
- Minor versions receive security updates until the next minor release
- Patch versions are superseded immediately by the next patch

---

## Reporting a Vulnerability

**⚠️ CRITICAL: DO NOT disclose security vulnerabilities publicly in GitHub Issues or Discussions.**

### Secure Reporting Channels

We take security vulnerabilities seriously and appreciate responsible disclosure. Please report security issues through one of these channels:

#### 1. Private Email (Preferred)

**Email**: [qwamos@tutanota.com](mailto:qwamos@tutanota.com)

**Subject Line Format**: `[SECURITY] Brief vulnerability description`

**Encryption**: We recommend using PGP encryption for sensitive reports:
- PGP Key: Available on request
- Fingerprint: Contact us for current key

#### 2. GitHub Private Security Advisory (Alternative)

For GitHub-hosted vulnerabilities, you can use GitHub's private security advisory feature:

1. Go to https://github.com/Dezirae-Stark/QWAMOS/security/advisories
2. Click "New draft security advisory"
3. Fill in the details
4. Submit privately

**Note**: Email is preferred for time-sensitive or critical vulnerabilities.

### What NOT to Do

- ❌ **DO NOT** open public GitHub Issues for security vulnerabilities
- ❌ **DO NOT** post vulnerability details in Discussions
- ❌ **DO NOT** disclose vulnerabilities on social media
- ❌ **DO NOT** share exploits publicly before coordinated disclosure
- ❌ **DO NOT** test vulnerabilities on systems you don't own or have permission to test

---

## Vulnerability Reporting Template

Please include the following information in your vulnerability report:

### Required Information

```markdown
## Vulnerability Summary

**Title**: Brief descriptive title
**Severity**: Critical / High / Medium / Low
**Component**: [PQC / Gateway / VM Isolation / Panic System / Other]
**CVE-ID**: (if already assigned)

## Description

Detailed description of the vulnerability and its impact.

## Affected Versions

- Version(s) affected:
- First vulnerable version:
- Last vulnerable version:

## Vulnerability Type

Select all that apply:
- [ ] Cryptographic weakness (algorithm, implementation, key management)
- [ ] Authentication bypass
- [ ] Authorization failure
- [ ] VM escape / isolation breach
- [ ] Network deanonymization
- [ ] Information disclosure
- [ ] Denial of service
- [ ] Code execution (local / remote)
- [ ] Privilege escalation
- [ ] Input validation failure
- [ ] Memory safety issue (buffer overflow, use-after-free, etc.)
- [ ] Other: ___________

## Impact Assessment

**Confidentiality**: High / Medium / Low / None
**Integrity**: High / Medium / Low / None
**Availability**: High / Medium / Low / None

**Threat Model Tier Affected**: Tier 1 / Tier 2 / Tier 3 / Tier 4 / Tier 5
(See: https://github.com/Dezirae-Stark/QWAMOS/wiki/Security-Model)

**Exploitability**: Trivial / Easy / Moderate / Difficult / Very Difficult

## Attack Scenario

Describe how an attacker could exploit this vulnerability:

1. Preconditions (what access/conditions are required)
2. Step-by-step exploitation process
3. Post-exploitation impact

## Proof of Concept

**DO NOT include working exploits that could cause harm.**

Provide:
- Conceptual code showing the vulnerability (sanitized)
- Steps to reproduce (in a safe testing environment)
- Expected vs actual behavior
- Screenshots or logs (if applicable)

**Test Environment**:
- Device:
- Android Version:
- QWAMOS Version:
- Installation Method: Termux / Rooted KVM / Custom ROM

## Affected Components

Specific files, modules, or functions affected:

- File: `path/to/file.py`
- Function: `function_name()`
- Line numbers: XX-YY

## Suggested Fix

If you have ideas for mitigating or fixing the vulnerability:

- Proposed solution
- Alternative approaches
- Relevant patches or commits (if available)

## References

- Related CVEs:
- Security advisories:
- Research papers:
- Proof of concept code (external links):

## Researcher Information

**Name**: (optional - for attribution in advisory)
**Affiliation**: (optional)
**Contact**: (optional - for follow-up)
**PGP Key**: (optional - for encrypted communication)

**Attribution Preference**:
- [ ] Public acknowledgment with name
- [ ] Public acknowledgment anonymously
- [ ] No public acknowledgment

## Additional Notes

Any additional context or information.
```

---

## Response Timeline

We are committed to responding to security reports promptly and transparently.

### Expected Response Times

| Stage | Timeline | Description |
|-------|----------|-------------|
| **Initial Response** | 24-48 hours | Acknowledgment of receipt |
| **Triage & Validation** | 3-7 days | Confirm vulnerability and assess severity |
| **Patch Development** | 7-30 days | Develop and test fix (depends on complexity) |
| **Security Advisory** | 30-90 days | Coordinated public disclosure |
| **CVE Assignment** | As needed | Request CVE-ID if applicable |

### Severity-Based SLAs

**Critical Vulnerabilities** (CVSS 9.0-10.0):
- VM escape, crypto breaks, network deanonymization
- Initial response: 24 hours
- Patch target: 7 days
- Disclosure: 30 days

**High Vulnerabilities** (CVSS 7.0-8.9):
- Privilege escalation, authentication bypass, data exposure
- Initial response: 48 hours
- Patch target: 14 days
- Disclosure: 60 days

**Medium Vulnerabilities** (CVSS 4.0-6.9):
- DoS, information disclosure, input validation issues
- Initial response: 72 hours
- Patch target: 30 days
- Disclosure: 90 days

**Low Vulnerabilities** (CVSS 0.1-3.9):
- Minor issues, theoretical attacks
- Initial response: 7 days
- Patch target: Next release
- Disclosure: 90 days

**Note**: Timelines may be extended by mutual agreement if additional research or development time is needed.

---

## Disclosure Policy

QWAMOS follows a **Coordinated Vulnerability Disclosure** policy.

### Disclosure Process

1. **Private Reporting**: Researcher reports vulnerability privately
2. **Acknowledgment**: We acknowledge receipt within 24-48 hours
3. **Validation**: We confirm and assess the vulnerability (3-7 days)
4. **Patch Development**: We develop a fix (timeline depends on severity)
5. **Security Advisory**: We prepare a draft security advisory
6. **Researcher Review**: Researcher reviews advisory and patch (optional)
7. **Release**: We release patched version
8. **Public Disclosure**: We publish security advisory (coordinated timing)
9. **CVE Publication**: CVE details published (if applicable)

### Disclosure Timeline

**Standard Timeline**: 90 days from initial report to public disclosure

**Early Disclosure**: May occur if:
- Fix is released and widely deployed
- Vulnerability is being actively exploited in the wild
- Vulnerability details are already public
- Mutual agreement with researcher

**Extended Timeline**: May occur if:
- Fix is complex and requires extensive testing
- Coordinating with upstream dependencies
- Multiple vulnerabilities being addressed together
- Researcher requests extension

### Public Advisory Contents

Our security advisories include:

- Vulnerability description (non-technical summary)
- Affected versions
- Fixed versions
- Severity rating (CVSS score)
- Impact assessment
- Mitigation steps (if patch not immediately available)
- Upgrade instructions
- Researcher acknowledgment (with permission)
- Timeline of disclosure
- CVE-ID (if assigned)

---

## Security Researcher Safe Harbor

QWAMOS is committed to supporting security researchers who help improve our security.

### Safe Harbor Provisions

If you comply with this security policy, we will:

✅ **Not pursue legal action** against you for security research activities
✅ **Not report you to law enforcement** for good faith security research
✅ **Work with you** to understand and resolve the vulnerability
✅ **Publicly acknowledge** your contribution (with your permission)
✅ **Consider you** for our security researcher recognition program

### Safe Harbor Requirements

To qualify for safe harbor protections, you must:

1. **Follow Responsible Disclosure**: Report vulnerabilities privately and allow reasonable time for patching
2. **Avoid Harm**: Do not exploit vulnerabilities for malicious purposes
3. **Respect Privacy**: Do not access, modify, or delete data belonging to others
4. **Test Responsibly**: Only test on your own systems or systems you have explicit permission to test
5. **Avoid Service Disruption**: Do not perform testing that could degrade or disrupt services
6. **Follow the Law**: Comply with all applicable laws in your jurisdiction

### Legal Considerations

**This safe harbor does NOT cover**:

- ❌ Unauthorized access to production systems or user data
- ❌ Social engineering attacks on QWAMOS developers or users
- ❌ Physical attacks on infrastructure
- ❌ Denial of service attacks
- ❌ Automated scanning that disrupts services
- ❌ Activities that violate laws in your jurisdiction

**Disclaimer**: This policy is a good faith commitment but does not create a legally binding contract. We cannot control the actions of third parties, upstream dependencies, or law enforcement.

---

## Security Patch Guidelines

If you would like to submit a security patch, please follow these guidelines:

### Before Submitting a Patch

1. **Report the vulnerability first** via private channels (email or GitHub Security Advisory)
2. **Wait for triage** - Let us confirm the vulnerability and coordinate a fix
3. **Discuss your approach** - We may have architectural constraints or alternative solutions

### Submitting Security Patches

**DO**:
- ✅ Submit patches via private channels (email or private fork)
- ✅ Include clear commit messages explaining the fix
- ✅ Add tests that verify the fix
- ✅ Update documentation if behavior changes
- ✅ Follow our coding standards (see CONTRIBUTING.md)
- ✅ Sign your commits with GPG (preferred)

**DON'T**:
- ❌ Submit security patches via public pull requests
- ❌ Reference the vulnerability in commit messages (use vague descriptions)
- ❌ Include proof-of-concept exploits in patch comments
- ❌ Break backward compatibility without discussion
- ❌ Introduce new dependencies without approval

### Patch Review Process

1. We review the patch privately
2. We may request changes or clarifications
3. We test the patch across all VM modes and gateways
4. We integrate the patch into our codebase (may refactor)
5. We credit you in the security advisory (with permission)
6. We release the patched version
7. We publicly acknowledge your contribution

### Security Patch Attribution

If you submit a security patch:
- You will be credited in the security advisory (unless you prefer anonymity)
- Your name will appear in CHANGELOG.md
- You may receive a CVE "Discovered By" credit
- You will be recognized in our Security Researchers Hall of Fame

---

## Known Sensitive Components

The following components are particularly security-sensitive and should be carefully reviewed when making changes or reporting vulnerabilities.

### 1. Post-Quantum Cryptography (PQC) Stack

**Location**: `qwamos/crypto/`

**Critical Modules**:
- **Kyber-1024 KEM** (`kyber.py`): Key encapsulation mechanism for quantum-resistant key exchange
- **ChaCha20-Poly1305 AEAD** (`symmetric.py`): Authenticated encryption with associated data
- **BLAKE3 Hashing** (`hash.py`): Cryptographic hash function for integrity verification
- **Key Derivation** (`kdf.py`): KDF for deriving encryption keys
- **Random Number Generation** (`random.py`): Cryptographically secure randomness

**Vulnerability Types to Watch For**:
- ⚠️ Side-channel attacks (timing, cache, power analysis)
- ⚠️ Weak randomness or entropy issues
- ⚠️ Key reuse or improper key rotation
- ⚠️ Algorithm implementation flaws
- ⚠️ Memory leaks of key material
- ⚠️ Improper key storage or transmission

**Impact if Compromised**:
- Complete confidentiality loss (all encrypted data)
- VM disk decryption
- Network traffic decryption
- Authentication bypass

**Testing Requirements**:
```bash
# Run crypto test suite
pytest tests/crypto/ -v

# Test key generation
python3 -c "from qwamos.crypto.kyber import generate_keypair; generate_keypair()"

# Test encryption/decryption
python3 tests/crypto/test_aead.py
```

---

### 2. Gateway Stack (Network Anonymization)

**Location**: `qwamos/gateway/`

**Critical Components**:
- **Tor Integration** (`tor.py`): SOCKS5 proxy for Tor network access
- **I2P Integration** (`i2p.py`): HTTP proxy for I2P network access
- **DNSCrypt** (`dnscrypt.py`): DNS-over-HTTPS for DNS privacy
- **Gateway Manager** (`manager.py`): Orchestrates gateway selection and failover
- **Traffic Router** (`router.py`): Routes traffic through gateways

**Vulnerability Types to Watch For**:
- ⚠️ IP/DNS leaks (bypass of anonymization)
- ⚠️ Clearnet fallback without warning
- ⚠️ Correlation attacks (timing, traffic analysis)
- ⚠️ MITM attacks on gateway connections
- ⚠️ Credential leaks in gateway configuration
- ⚠️ DNS rebinding attacks

**Impact if Compromised**:
- User deanonymization
- Real IP address exposure
- Location tracking
- Network activity correlation
- Censorship bypass failure

**Testing Requirements**:
```bash
# Test Tor connectivity
curl --socks5 127.0.0.1:9050 https://check.torproject.org

# Test I2P connectivity
curl --proxy http://127.0.0.1:4444 http://stats.i2p/

# Test DNS resolution
dig @127.0.0.1 -p 5353 google.com

# Check for leaks
python3 tests/gateway/test_leak_detection.py
```

---

### 3. VM Isolation Layer

**Location**: `qwamos/vm/`

**Critical Components**:
- **QEMU Backend** (`qemu.py`): Software-based VM emulation
- **Chroot Backend** (`chroot.py`): Namespace-based isolation
- **PRoot Backend** (`proot.py`): Userspace virtualization
- **KVM Backend** (`kvm.py`): Hardware-accelerated virtualization
- **VM Manager** (`manager.py`): VM lifecycle management
- **Disk Encryption** (`disk.py`): Encrypted VM disk images
- **Isolation Enforcer** (`isolation.py`): Seccomp/AppArmor policies

**Vulnerability Types to Watch For**:
- ⚠️ VM escape vulnerabilities
- ⚠️ Privilege escalation (guest to host)
- ⚠️ Shared memory leaks
- ⚠️ Device passthrough issues
- ⚠️ Filesystem isolation bypass
- ⚠️ Network isolation bypass
- ⚠️ Resource exhaustion (DoS)

**Impact if Compromised**:
- Host system compromise
- Cross-VM attacks
- Data exfiltration from host
- Persistent malware on host
- Complete system takeover

**Testing Requirements**:
```bash
# Test VM isolation
./scripts/test_vm_isolation.sh qemu
./scripts/test_vm_isolation.sh chroot
./scripts/test_vm_isolation.sh proot
./scripts/test_vm_isolation.sh kvm

# Test seccomp policies
pytest tests/vm/test_seccomp.py

# Test disk encryption
pytest tests/vm/test_disk_encryption.py
```

---

### 4. Panic/Wipe Subsystem

**Location**: `qwamos/panic/`

**Critical Components**:
- **Panic Detector** (`detector.py`): Detects panic triggers (duress password, USB removal, etc.)
- **Wipe Engine** (`wipe.py`): Secure data deletion
- **Key Destruction** (`keys.py`): Emergency key material destruction
- **VM Termination** (`terminate.py`): Immediate VM shutdown
- **Evidence Removal** (`cleanup.py`): Removes forensic artifacts

**Vulnerability Types to Watch For**:
- ⚠️ Panic trigger bypass
- ⚠️ Incomplete data wiping
- ⚠️ Key recovery after wipe
- ⚠️ Race conditions in wipe process
- ⚠️ Wipe mechanism disclosure
- ⚠️ Denial of service via panic trigger

**Impact if Compromised**:
- Data recovery after panic
- Forensic evidence preservation
- User identification
- Duress detection bypass
- False panic triggers (data loss)

**Testing Requirements**:
```bash
# Test panic detection (USE CAUTION - may trigger wipe)
pytest tests/panic/test_detector.py --safe-mode

# Test wipe verification (on test data only)
pytest tests/panic/test_wipe.py

# Test key destruction
pytest tests/panic/test_key_destruction.py
```

---

### 5. Authentication & Authorization

**Location**: `qwamos/auth/`

**Critical Components**:
- **User Authentication** (`auth.py`): Password/biometric authentication
- **VM Access Control** (`access.py`): VM permission management
- **Session Management** (`session.py`): User session handling
- **Duress Mode** (`duress.py`): Plausible deniability features

**Vulnerability Types to Watch For**:
- ⚠️ Authentication bypass
- ⚠️ Weak password storage
- ⚠️ Session hijacking
- ⚠️ Privilege escalation
- ⚠️ Brute force vulnerabilities

---

### 6. Storage & Encryption

**Location**: `qwamos/storage/`

**Critical Components**:
- **Volume Management** (`volumes.py`): Encrypted volume creation/mounting
- **Key Management** (`keystore.py`): Encryption key storage
- **Backup System** (`backup.py`): Encrypted backups

**Vulnerability Types to Watch For**:
- ⚠️ Plaintext key storage
- ⚠️ Weak encryption parameters
- ⚠️ Backup integrity issues
- ⚠️ Key exposure in memory

---

## Security Audits & CVEs

### Security Audits

**Status**: No formal security audit has been completed yet.

**Roadmap**:
- Q2 2025: Internal security review
- Q4 2025: Third-party security audit (target)

**Interested in auditing QWAMOS?** Contact: [qwamos@tutanota.com](mailto:qwamos@tutanota.com)

### CVE Program

We participate in the CVE (Common Vulnerabilities and Exposures) program.

**CVE Namespace**: We request CVEs through GitHub Security Advisories or directly through MITRE.

**Published CVEs**: None to date

**Requesting a CVE**: If you discover a vulnerability, we will work with you to request a CVE-ID if appropriate.

---

## Security Best Practices

### For Users

**Installation**:
- ✅ Always download QWAMOS from official sources
- ✅ Verify Git commit signatures
- ✅ Use the latest stable release
- ✅ Keep Android and Termux updated

**Configuration**:
- ✅ Use strong, unique passwords
- ✅ Enable disk encryption for all VMs
- ✅ Configure gateways correctly (Tor/I2P/DNSCrypt)
- ✅ Review threat model tier and adjust settings accordingly

**Operational Security**:
- ✅ Regularly backup encrypted volumes
- ✅ Test panic/wipe functionality in safe environment
- ✅ Monitor logs for anomalies
- ✅ Understand your adversary model (see Security-Model.md)

### For Developers

**Code Review**:
- ✅ All crypto changes require two reviewer approvals
- ✅ VM isolation changes require thorough testing
- ✅ Gateway changes require leak testing

**Testing**:
- ✅ Run full test suite before commits
- ✅ Test all VM modes (QEMU/Chroot/PRoot/KVM)
- ✅ Test all gateway configurations (Tor/I2P/DNSCrypt)
- ✅ Verify crypto test suite passes

**Dependencies**:
- ✅ Pin dependency versions
- ✅ Review dependency security advisories
- ✅ Minimize external dependencies in security-critical code

---

## Security Resources

**Documentation**:
- [Security Model Wiki](https://github.com/Dezirae-Stark/QWAMOS/wiki/Security-Model) - Threat model and adversary tiers
- [Architecture Wiki](https://github.com/Dezirae-Stark/QWAMOS/wiki/Architecture) - System design and isolation boundaries
- [Developer Guide](https://github.com/Dezirae-Stark/QWAMOS/wiki/Developer-Guide) - Secure development practices

**External Resources**:
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Tor Project Security](https://www.torproject.org/docs/documentation.html)

**Security Tools**:
- [Bandit](https://github.com/PyCQA/bandit) - Python security linter
- [Safety](https://github.com/pyupio/safety) - Dependency vulnerability scanner
- [CodeQL](https://codeql.github.com/) - Semantic code analysis

---

## Hall of Fame

We recognize security researchers who have responsibly disclosed vulnerabilities.

**Security Researchers** (in chronological order):

_No vulnerabilities have been reported yet. Be the first!_

**How to be listed**:
- Report a valid security vulnerability
- Follow responsible disclosure
- Receive confirmation that vulnerability is fixed
- Provide permission for public acknowledgment

---

## Contact Information

**Security Team Email**: [qwamos@tutanota.com](mailto:qwamos@tutanota.com)

**Subject Line**: `[SECURITY] Your brief description`

**PGP Encryption**: Available on request (contact us for public key)

**Response Time**: 24-48 hours for initial acknowledgment

**Security Advisory Page**: https://github.com/Dezirae-Stark/QWAMOS/security/advisories

**General Security Questions**: Post in [Security Research Discussion](https://github.com/Dezirae-Stark/QWAMOS/discussions/4)

---

## Updates to This Policy

This security policy may be updated periodically. Significant changes will be announced in:
- GitHub Discussions (#2 Announcements)
- Security Advisory feed
- Release notes

**Last Updated**: 2025-11-18
**Version**: 1.0.0

---

**🛡️ Security is a community effort. Thank you for helping keep QWAMOS secure!**

**License**: This security policy is part of the QWAMOS project and is licensed under AGPL-3.0.
**Copyright**: © 2025 QWAMOS Project
**Contact**: qwamos@tutanota.com
