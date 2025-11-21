# QWAMOS Hardening Standard

**Baseline Configuration & Operational Security Controls**

**Author:** Dezirae Stark · First Sterling Capital, LLC
**Version:** 1.0
**Date:** 2025-11-17
**Status:** Active Standard

---

## 1. Purpose & Scope

### Purpose

This document defines the minimum security hardening requirements and operational controls for QWAMOS deployments. It serves as a baseline configuration standard for users, administrators, and auditors to ensure consistent security posture across all QWAMOS installations.

### Scope

This standard applies to:
- **Production Deployments:** QWAMOS installations used in operational environments
- **Development Environments:** Test and development instances handling sensitive data
- **Security Audits:** Third-party security assessments and penetration tests

This standard does NOT apply to:
- Intentionally weakened test environments (must be clearly labeled)
- Research/academic environments explicitly operating in reduced-security mode

### Authority

This standard is maintained by **First Sterling Capital, LLC** and enforced through:
- Default configurations in official releases
- Documentation and operational guides
- Community best practices and security advisories

---

## 2. Threat Model Summary

QWAMOS is designed to defend against sophisticated adversaries including:

### Threat Actors
- **Nation-State APTs:** Advanced persistent threats with substantial resources
- **Targeted Surveillance:** Zero-day exploits, baseband attacks, supply chain compromise
- **Local Attackers:** Physical device seizure, coercion, forensic analysis
- **Malware & Ransomware:** Remote code execution, data exfiltration, encryption attacks
- **Network Adversaries:** ISP surveillance, man-in-the-middle, traffic analysis

### Attack Vectors
1. **Baseband Processor:** Exploitation of cellular modem firmware
2. **Hardware Tampering:** Physical modification, evil maid attacks
3. **VM Escape:** Hypervisor vulnerabilities leading to isolation bypass
4. **Network Deanonymization:** Tor/I2P compromise, timing attacks
5. **Cryptographic Attacks:** Quantum computers (post-2030), side-channel leakage
6. **Supply Chain:** Malicious dependencies, compromised build tools
7. **Panic/Duress Scenarios:** Device seizure, rubber-hose cryptanalysis

### Security Goals
- **Confidentiality:** Protect data at rest and in transit against unauthorized access
- **Integrity:** Prevent unauthorized modification of code, configuration, and data
- **Availability:** Maintain system functionality under attack (within reason)
- **Anonymity:** Conceal user identity and network activity from surveillance
- **Deniability:** Provide plausible deniability via decoy profiles and panic modes

---

## 3. Device Hardening

### 3.1 Bootloader Security

**Requirements:**
- ✅ **Bootloader Lock:** Bootloader must verify kernel signatures before execution
- ✅ **Secure Boot Chain:** U-Boot → Kernel signature verification using Ed448/Kyber-1024
- ✅ **No Fastboot Mode:** Fastboot interface disabled in production builds
- ⚠️ **Rollback Protection:** Anti-rollback counters enforced (implementation pending)

**Verification:**
```bash
# Check bootloader lock status
cat /proc/cmdline | grep "androidboot.verifiedbootstate=green"

# Verify U-Boot signature verification enabled
strings /dev/block/bootdevice/by-name/boot | grep "CONFIG_FIT_SIGNATURE=y"
```

**Configuration:**
- Bootloader unlock MUST require full data wipe
- Developer mode MUST be disabled for production deployments

---

### 3.2 Physical Access Controls

**Requirements:**
- ✅ **Device Encryption:** Full-disk encryption mandatory (PostQuantumVolume with Kyber-1024 + ChaCha20-Poly1305)
- ✅ **Lockscreen Timeout:** Maximum 5 minutes idle before lockscreen activates
- ✅ **USB Debugging Disabled:** ADB disabled for production (development only with explicit user action)
- ✅ **OEM Unlock Disabled:** Bootloader unlock option disabled in settings

**Configuration:**
```bash
# Enforce full-disk encryption
setprop ro.crypto.type file
setprop ro.crypto.state encrypted

# Disable USB debugging
setprop persist.sys.usb.config none
setprop ro.adb.secure 1
```

**Physical Security Checklist:**
- [ ] Device stored in secure location when not in use
- [ ] Screen lock enabled (PIN/password/biometric)
- [ ] SIM card PIN enabled
- [ ] USB-C port access controlled (dust plugs or physical locks)

---

### 3.3 Secure Storage & Disk Encryption

**Requirements:**
- ✅ **Encryption Algorithm:** Kyber-1024 (key encapsulation) + ChaCha20-Poly1305 (data encryption)
- ✅ **Key Derivation:** Argon2id (memory-hard KDF) with configurable security profiles
- ✅ **Integrity Protection:** BLAKE3 for cryptographic hashing and integrity verification
- ✅ **No Legacy Crypto:** AES, RSA, ECDH prohibited for new deployments

**Argon2id Profiles:**

| Profile | Memory (MB) | Iterations | Parallelism | Use Case |
|---------|------------|------------|-------------|----------|
| **Light** | 64 | 3 | 4 | Development/Testing |
| **Medium** | 256 | 4 | 4 | Standard Deployments |
| **Heavy** | 512 | 5 | 8 | High-Security (recommended) |

**Default:** `ARGON2_PROFILE=heavy`

**Verification:**
```bash
# Check encryption status
cryptsetup status /dev/mapper/userdata

# Verify Kyber-1024 KEM
python3 -c "from crypto.pq import PostQuantumVolume; print(PostQuantumVolume.verify_algorithm())"
```

---

### 3.4 Panic-Wipe & Kill-Switch Behavior

**Requirements:**
- ✅ **Panic Gesture:** Multi-touch gesture triggers immediate data wipe
- ✅ **Duress PIN:** Secondary unlock code activates decoy profile
- ✅ **Radio Kill Switch:** Physical or software kill for cellular/Wi-Fi/Bluetooth
- ✅ **Session Key Destruction:** RAM encryption keys wiped on panic trigger

**Panic Gesture Configuration:**
```python
# /data/data/com.termux/files/home/QWAMOS/security/panic/gesture_config.py
PANIC_GESTURE = "five_finger_triple_tap"  # Customizable
WIPE_PASSES = 3  # DoD 5220.22-M standard
WIPE_TARGETS = ["userdata", "sdcard", "cache"]
```

**Kill Switch Behavior:**
- **Level 1:** Disable radios (airplane mode)
- **Level 2:** Disable baseband processor (kernel module unload)
- **Level 3:** Full power-off (battery disconnect if hardware-supported)

**Testing:**
```bash
# Test panic wipe (WARNING: WILL ERASE DATA)
# Only run in isolated test environment
python3 security/panic/test_panic_wipe.py --dry-run
```

---

## 4. VM & Isolation Hardening

### 4.1 Required VM Policies

**Dom0 (Control Domain):**
- ✅ **Minimal Attack Surface:** No user applications, no network drivers
- ✅ **Policy Enforcement:** Xen-style VM isolation policies
- ✅ **Resource Limits:** CPU/memory quotas enforced per VM
- ❌ **No Direct Internet:** Dom0 has NO network access (Gateway VM only)

**Gateway VM (Network Proxy):**
- ✅ **Tor/I2P Mandatory:** ALL traffic routed through anonymity networks
- ✅ **Firewall Default-Deny:** iptables/nftables with DROP default policy
- ✅ **DNS Leak Prevention:** DNS queries over Tor or DNSCrypt only
- ✅ **No Persistent Storage:** Gateway VM runs from ephemeral ramdisk

**Workstation VM (User Environment):**
- ✅ **No Direct Network:** Network access ONLY through Gateway VM proxy
- ✅ **Read-Only Root:** Immutable root filesystem (overlayfs with tmpfs)
- ✅ **AppArmor/SELinux:** Mandatory access control enabled
- ✅ **No Sudo/Root Access:** User runs as unprivileged account

**Trusted UI VM (Display/Input):**
- ✅ **Input Sanitization:** Keyboard input filtered for exploits
- ✅ **Framebuffer Isolation:** GPU-accelerated rendering isolated from workstation
- ✅ **No Network Access:** Trusted UI has zero network connectivity

---

### 4.2 Default VM Communication Policies

**Inter-VM Communication Matrix:**

| Source VM | Destination VM | Allowed Protocol | Firewall Rule |
|-----------|---------------|------------------|---------------|
| Workstation | Gateway | HTTP/HTTPS proxy | ACCEPT on 8118, 9050 |
| Gateway | Tor/I2P | Onion/I2P routing | ACCEPT on 9050, 7657 |
| Trusted UI | Workstation | Display protocol | ACCEPT on Unix socket |
| Dom0 | All VMs | Control messages | ACCEPT on qrexec |
| Workstation | Dom0 | **DENY** | DROP all |
| Workstation | Trusted UI | **DENY** | DROP all |

**Implementation:**
```bash
# /data/data/com.termux/files/home/QWAMOS/network/firewall/vm_policies.sh

# Workstation → Gateway (HTTP proxy only)
iptables -A FORWARD -s 192.168.100.0/24 -d 192.168.200.1 -p tcp --dport 8118 -j ACCEPT
iptables -A FORWARD -s 192.168.100.0/24 -d 192.168.200.1 -p tcp --dport 9050 -j ACCEPT

# Default DENY all other inter-VM traffic
iptables -P FORWARD DROP
```

---

## 5. Network Hardening

### 5.1 Default Firewall Stance

**Requirements:**
- ✅ **Default DROP:** All incoming connections dropped by default
- ✅ **Egress Filtering:** Outbound connections limited to Gateway VM proxies
- ✅ **No IPv6:** IPv6 disabled unless explicitly required and hardened
- ✅ **Port Knocking Disabled:** No dynamic port opening mechanisms

**iptables Configuration:**
```bash
# Set default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

---

### 5.2 DNS Leakage Prevention

**Requirements:**
- ✅ **No System DNS Resolvers:** /etc/resolv.conf points to Tor DNS or DNSCrypt
- ✅ **DNS-over-Tor:** All DNS queries proxied through Tor SOCKS (port 9050)
- ✅ **DNSSEC Validation:** DNSCrypt-proxy configured with DNSSEC enforcement
- ❌ **No Google DNS:** 8.8.8.8, 8.8.4.4 blocked via firewall

**Configuration:**
```bash
# /etc/resolv.conf
nameserver 127.0.0.1  # DNSCrypt-proxy listening on localhost

# DNSCrypt-proxy config
dnscrypt-proxy -config /etc/dnscrypt-proxy/dnscrypt-proxy.toml
```

**DNS Leak Testing:**
```bash
# Run DNS leak test
curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip

# Verify no leaks
tcpdump -i wlan0 port 53 -n  # Should show NO DNS queries on physical interface
```

---

### 5.3 Baseband/Radio Usage Policies

**Requirements:**
- ✅ **Baseband Isolation:** Cellular modem isolated in separate VM (future enhancement)
- ✅ **Airplane Mode Default:** Radios disabled by default on boot
- ✅ **IMEI/IMSI Protection:** Baseband firmware prevented from leaking identifiers
- ⚠️ **No SMS/Voice:** SMS and voice calls disabled or heavily restricted (high-risk)

**Radio Kill Switch:**
```bash
# Software kill switch
echo 0 > /sys/devices/platform/soc/soc:bluetooth/rfkill/rfkill0/state
echo 0 > /sys/devices/platform/soc/soc:wlan/rfkill/rfkill1/state
echo 0 > /sys/devices/platform/soc/soc:modem/rfkill/rfkill2/state

# Hardware kill switch (if supported)
# GPIO pin control to physically disable baseband power
```

---

## 6. Cryptography & Key Management

### 6.1 Required Algorithms and Key Lengths

**Symmetric Encryption:**
- ✅ **Approved:** ChaCha20-Poly1305 (256-bit keys)
- ❌ **Prohibited:** AES-CBC (padding oracle attacks), AES-GCM (nonce reuse risks)

**Post-Quantum Key Encapsulation:**
- ✅ **Approved:** Kyber-1024 (NIST ML-KEM Level 5)
- ❌ **Prohibited:** RSA, ECDH (vulnerable to quantum computers)

**Digital Signatures:**
- ✅ **Approved:** Ed448 (current), Dilithium (future)
- ❌ **Prohibited:** RSA-PSS, ECDSA (quantum-vulnerable)

**Hashing & Integrity:**
- ✅ **Approved:** BLAKE3 (primary), SHA-3 (secondary)
- ⚠️ **Legacy Only:** SHA-256 (for compatibility with existing tools only)
- ❌ **Prohibited:** MD5, SHA-1

**Key Derivation:**
- ✅ **Approved:** Argon2id (memory-hard, GPU-resistant)
- ❌ **Prohibited:** PBKDF2, bcrypt, scrypt (weaker than Argon2id)

---

### 6.2 Key Storage Practices

**Requirements:**
- ✅ **Hardware-Backed Storage:** Use ARM TrustZone (StrongBox/Keymaster) where available
- ✅ **No Plaintext Keys:** Keys never stored unencrypted on disk
- ✅ **Key Rotation:** Master keys rotated every 12 months (recommended)
- ✅ **Secure Deletion:** Keys wiped with 3-pass overwrite on deletion

**TrustZone Integration:**
```python
# Example: Store key in TrustZone
from android.security.keystore import AndroidKeyStore

keystore = AndroidKeyStore()
keystore.generate_key(
    alias="qwamos_master_key",
    algorithm="ChaCha20-Poly1305",
    key_size=256,
    user_authentication_required=True,
    strongbox_backed=True  # Force hardware backing
)
```

**Key Backup:**
- ❌ **No Cloud Backup:** Keys NEVER uploaded to cloud services
- ✅ **Offline Backup:** Paper backup of recovery phrase (BIP39-style mnemonic)
- ✅ **Shamir Secret Sharing:** Split key into N-of-M shares for distributed backup

---

### 6.3 No Legacy Algorithms

**Explicit Prohibitions:**
- ❌ AES-128, AES-192 (use ChaCha20 instead)
- ❌ RSA-2048, RSA-4096 (quantum-vulnerable)
- ❌ ECDH P-256, P-384 (quantum-vulnerable)
- ❌ 3DES, Blowfish, RC4 (broken or obsolete)

**Exception Process:**
If a legacy algorithm is absolutely required (e.g., interoperability with external system):
1. Document justification in `docs/CRYPTO_EXCEPTIONS.md`
2. Implement as temporary bridge with migration plan
3. Isolate usage to dedicated VM with no access to sensitive data
4. Schedule deprecation within 12 months

---

## 7. Logging & Telemetry

### 7.1 Default Logging Behavior

**Requirements:**
- ✅ **Local Logging Only:** All logs stored on-device, never transmitted
- ✅ **No Telemetry:** Zero analytics, crash reports, or usage data sent externally
- ✅ **Audit Trails:** Security-relevant events logged with timestamps
- ✅ **Log Rotation:** Logs rotated daily, compressed, and encrypted

**Logged Events:**
- Authentication attempts (success/failure)
- VM start/stop/crash events
- Firewall rule violations
- Cryptographic operations (key generation, encryption/decryption)
- Panic gesture activations
- ML threat detection alerts

**Log Retention:**
- **Security Logs:** 90 days
- **System Logs:** 30 days
- **Debug Logs:** 7 days

---

### 7.2 No Unauthorized Telemetry

**Prohibited:**
- ❌ Google Analytics, Firebase Analytics
- ❌ Crash reporting (Crashlytics, Sentry)
- ❌ A/B testing frameworks
- ❌ Push notification services (Firebase Cloud Messaging)
- ❌ Usage statistics

**Verification:**
```bash
# Check for network connections to analytics domains
tcpdump -i any -n | grep -E "google-analytics|firebase|crashlytics"

# Review Android manifest for unauthorized permissions
grep -r "INTERNET" AndroidManifest.xml

# Audit code for telemetry libraries
grep -r "analytics\|telemetry\|tracking" --include="*.java" --include="*.py"
```

---

## 8. Update & Patch Management

### 8.1 Update Delivery Channels

**Approved Sources:**
- ✅ **GitHub Releases:** https://github.com/Dezirae-Stark/QWAMOS/releases
- ✅ **Tor Onion Mirror:** (to be established)
- ❌ **Unapproved:** Google Play Store, third-party app stores

**Update Verification:**
```bash
# Download release
wget https://github.com/Dezirae-Stark/QWAMOS/releases/download/v1.1.0/QWAMOS-v1.1.0.tar.gz

# Verify GPG signature
gpg --verify QWAMOS-v1.1.0.tar.gz.sig QWAMOS-v1.1.0.tar.gz

# Verify checksum
sha256sum -c QWAMOS-v1.1.0-SHA256SUMS.txt
```

---

### 8.2 Safe Update Process

**Requirements:**
- ✅ **Signature Verification:** All updates signed with Ed448 key
- ✅ **Incremental Updates:** A/B partition updates with rollback capability
- ✅ **Backup Before Update:** Automated backup of user data before applying update
- ⚠️ **No Auto-Update:** Manual approval required (auto-update opt-in only)

**Update Procedure:**
1. **Download:** Fetch update package from trusted source
2. **Verify:** Check GPG signature and SHA-256 checksum
3. **Backup:** Create encrypted backup of userdata partition
4. **Install:** Flash update to inactive A/B partition
5. **Test:** Boot into new partition, verify functionality
6. **Commit:** Mark new partition as permanent (or rollback if issues)

---

## 9. Operational Procedures

### 9.1 Role Separation

**Recommended Roles:**
- **Administrator:** System configuration, VM management, updates
- **User:** Daily operations within VMs, no system-level access
- **Auditor:** Read-only access to logs and security events

**Principle of Least Privilege:**
- Users operate in unprivileged Workstation VM
- Administrator access requires separate authentication
- No single account has full Dom0 + VM access

---

### 9.2 Regular Security Reviews

**Required Activities:**

| Activity | Frequency | Responsibility |
|----------|-----------|----------------|
| **Log Review** | Weekly | Administrator |
| **SBOM Audit** | Monthly | Administrator |
| **Vulnerability Scan** | Monthly | Administrator |
| **Firewall Rule Review** | Quarterly | Administrator |
| **Key Rotation** | Annually | Administrator |
| **Full Security Audit** | Annually | External Auditor |

**Log Review Checklist:**
```bash
# Check for failed authentication attempts
grep "authentication failure" /var/log/auth.log

# Review ML threat detection alerts
python3 /data/data/com.termux/files/home/QWAMOS/ai/ml_threat_detection/review_alerts.py

# Analyze firewall drops
journalctl -u nftables --since "7 days ago" | grep DROP
```

---

### 9.3 Incident Response Basics

**Incident Detection:**
- ML Threat Detection alerts trigger investigation
- Unusual network traffic patterns
- Unexpected VM crashes or reboots
- Unauthorized file modifications

**Response Procedure:**
1. **Isolate:** Disconnect network (activate radio kill switch)
2. **Capture:** Take memory dump and disk snapshot
3. **Analyze:** Review logs, forensic audit output
4. **Remediate:** Patch vulnerability, restore from clean backup
5. **Report:** Document incident in `docs/INCIDENT_REPORTS.md`

**Escalation:**
- Critical incidents: Contact security team (qwamos@tutanota.com)
- Suspected nation-state attack: Activate panic wipe if necessary
- Data breach: Follow data breach notification laws

---

## 10. Deviations & Exceptions

### 10.1 Exception Process

In rare cases, operators may need to deviate from this standard. All deviations MUST be:

1. **Documented:** Written justification in `docs/HARDENING_EXCEPTIONS.md`
2. **Risk-Assessed:** Documented security impact and mitigations
3. **Time-Limited:** Expiration date for exception (maximum 12 months)
4. **Approved:** Signed off by Administrator or Security Officer

**Exception Template:**
```markdown
## Exception ID: EXC-2025-001

**Standard Requirement:** 6.1 - No legacy algorithms (AES-256 prohibited)
**Deviation:** Allow AES-256-GCM for compatibility with legacy VPN server
**Justification:** Corporate VPN requires AES-256-GCM; no alternative available
**Risk Assessment:** Low (temporary bridge, isolated to Gateway VM only)
**Mitigation:** Traffic double-encrypted (Kyber-1024 wrapping AES)
**Expiration:** 2026-01-01 (migrate to WireGuard with PQ crypto)
**Approved By:** Dezirae Stark (2025-11-17)
```

---

### 10.2 Audit & Compliance

**Compliance Verification:**
```bash
# Run automated compliance check
python3 tools/compliance_checker.py --standard=hardening_v1.0

# Generate compliance report
python3 tools/compliance_checker.py --report=pdf --output=COMPLIANCE_REPORT.pdf
```

**Expected Output:**
```
QWAMOS Hardening Standard v1.0 Compliance Check
================================================
[PASS] Bootloader lock enabled
[PASS] Full-disk encryption (Kyber-1024)
[PASS] Firewall default-deny policy
[WARN] IPv6 enabled (should be disabled)
[FAIL] Argon2id profile set to 'light' (should be 'heavy')

Overall Compliance: 85% (2 warnings, 1 failure)
```

---

## Appendix A: Quick Reference Checklist

**Initial Deployment:**
- [ ] Verify bootloader lock enabled
- [ ] Enable full-disk encryption (Kyber-1024 + ChaCha20)
- [ ] Configure Argon2id profile to `heavy`
- [ ] Set up panic gesture and duress PIN
- [ ] Disable USB debugging
- [ ] Configure firewall (default DROP)
- [ ] Enable DNS-over-Tor
- [ ] Disable all telemetry
- [ ] Test radio kill switch
- [ ] Configure A/B partition updates
- [ ] Document any exceptions to standard

**Ongoing Maintenance:**
- [ ] Weekly log review
- [ ] Monthly SBOM audit
- [ ] Monthly vulnerability scan
- [ ] Quarterly firewall rule review
- [ ] Annual key rotation
- [ ] Annual external security audit

---

## Appendix B: Compliance Matrix

| Requirement | Priority | Implementation Status | Verification Method |
|-------------|----------|----------------------|---------------------|
| Bootloader Lock | Critical | ✅ Complete | `/proc/cmdline` inspection |
| Full-Disk Encryption | Critical | ✅ Complete | `cryptsetup status` |
| Kyber-1024 KEM | Critical | ✅ Complete | Python test script |
| Firewall Default-Deny | High | ✅ Complete | `iptables -L -v` |
| Panic Gesture | High | ✅ Complete | Test script (dry-run) |
| DNS-over-Tor | High | ✅ Complete | DNS leak test |
| No Telemetry | High | ✅ Complete | Network traffic analysis |
| Hardware Kill Switch | Medium | ⚠️ Partial | GPIO testing |
| Two-Person Review | Medium | ❌ Pending | GitHub branch protection |
| Baseband Isolation | Low | ❌ Future | Phase 12+ |

---

**Document Status:** Active
**Next Review:** 2026-05-17 (6-month review cycle)
**Maintained By:** Dezirae Stark, First Sterling Capital, LLC

---

© 2025 First Sterling Capital, LLC · QWAMOS Project
Licensed under AGPL-3.0
