# Security Model

**[← Back to Home](Home)**

---

## Threat Model

QWAMOS is designed to protect against **targeted surveillance, forensic analysis, and quantum computer attacks** while maintaining usability on mobile devices.

### Adversary Capabilities

**Tier 1: Script Kiddies & Opportunistic Attackers**
- **Capabilities:** Basic malware, phishing, network sniffing
- **QWAMOS Defense:** ✅ VM isolation blocks malware spreading, Tor hides network traffic

**Tier 2: Corporate Surveillance & Stalkerware**
- **Capabilities:** Spyware apps, location tracking, data harvesting
- **QWAMOS Defense:** ✅ Per-app VMs prevent cross-contamination, PQC encryption protects data-at-rest

**Tier 3: Law Enforcement & Border Security**
- **Capabilities:** Device seizure, forensic imaging, password cracking
- **QWAMOS Defense:** ✅ Panic wipe destroys encryption keys, duress passwords show decoy system

**Tier 4: Intelligence Agencies & APTs**
- **Capabilities:** Zero-days, supply chain attacks, quantum computers (future)
- **QWAMOS Defense:** ✅ Reproducible builds detect backdoors, Kyber-1024 resists quantum attacks

**Tier 5: Nation-State with Physical Access**
- **Capabilities:** Hardware implants, evil maid attacks, rubber-hose cryptanalysis
- **QWAMOS Defense:** ⚠️ Limited protection—no system survives torture or hardware compromise

###Out of Scope

QWAMOS **does NOT protect** against:
- ❌ **Physical hardware tampering** (baseband firmware, bootloader exploits)
- ❌ **Coercion/torture** (rubber-hose cryptanalysis)
- ❌ **Unpatched kernel vulnerabilities** (requires timely updates)
- ❌ **User error** (installing malicious apps, weak passphrases)
- ❌ **Signal intelligence** (baseband/cellular tracking if SIM inserted)

---

## How QWAMOS Isolates Apps

### VM-Based Compartmentalization

Each app runs in a **completely isolated virtual machine** with its own:

**Isolated Resources:**
- ✅ **Filesystem:** No shared files between VMs
- ✅ **Network stack:** Separate IP addresses, routing tables
- ✅ **Memory:** VMs cannot access each other's RAM
- ✅ **Processes:** No inter-VM process communication
- ✅ **GPU context:** Separate rendering pipelines
- ✅ **Clipboard:** No shared clipboard (unless explicitly bridged)

**Attack Surface Reduction:**

```
┌────────────────────────────────────────────────────────────┐
│ Traditional Android:                                       │
│                                                            │
│  All apps share same user space → Cross-contamination     │
│  ┌────────┐  ┌────────┐  ┌────────┐                       │
│  │Banking │←→│ Malware│←→│Social  │                       │
│  │  App   │  │  App   │  │  Media │                       │
│  └────────┘  └────────┘  └────────┘                       │
│       ↓           ↓           ↓                            │
│  Shared Android UID (10000) - No real isolation           │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ QWAMOS:                                                    │
│                                                            │
│  Each app in separate VM → Zero cross-contamination       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   VM 1      │  │   VM 2      │  │   VM 3      │       │
│  │┌──────────┐ │  │┌──────────┐ │  │┌──────────┐ │       │
│  ││ Banking  │ │  ││ Malware  │ │  ││ Social   │ │       │
│  ││   App    │ │  ││   App    │ │  ││  Media   │ │       │
│  │└──────────┘ │  │└──────────┘ │  │└──────────┘ │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│         ↓               ↓                 ↓               │
│  Complete hardware/software isolation boundaries         │
│  Malware CANNOT escape VM or attack other VMs            │
└────────────────────────────────────────────────────────────┘
```

### Isolation Enforcement Mechanisms

**Hypervisor-Level:**
- **QEMU:** Full system emulation, complete isolation
- **KVM:** Hardware virtualization extensions, memory isolation via ARM MMU
- **Chroot:** Linux namespace isolation (UID, PID, network, mount)

**Network-Level:**
- **Separate network namespaces** per VM
- **Firewall rules** enforced by iptables
- **Gateway routing** prevents VM-to-VM communication

**Filesystem-Level:**
- **Encrypted disk images** (one per VM)
- **No shared mount points** between VMs
- **Copy-on-write snapshots** (instant rollback)

---

## Encryption Stack

### Post-Quantum Cryptography

**Why Post-Quantum?**

Traditional cryptography (RSA, ECC) is vulnerable to **Shor's algorithm** running on quantum computers:

| Algorithm | Classical Security | Quantum Security |
|-----------|-------------------|------------------|
| **RSA-2048** | ✅ Secure (2^112) | ❌ Broken (~hours) |
| **ECC-256** | ✅ Secure (2^128) | ❌ Broken (~hours) |
| **Kyber-1024** | ✅ Secure (2^128) | ✅ Secure (2^254) |

**QWAMOS PQC Stack:**

```
┌────────────────────────────────────────────────────────────┐
│ Layer 1: Key Encapsulation Mechanism (KEM)                │
│                                                            │
│  Algorithm: Kyber-1024 (NIST FIPS 203)                    │
│  Security: 254-bit post-quantum security                  │
│  Purpose: Establish shared secret resistant to quantum    │
│           computers                                        │
│                                                            │
│  Public Key Size:  1568 bytes                             │
│  Private Key Size: 3168 bytes                             │
│  Ciphertext Size:  1568 bytes                             │
│  Shared Secret:    256 bits                               │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ Layer 2: Authenticated Encryption with Associated Data    │
│                                                            │
│  Algorithm: ChaCha20-Poly1305 (RFC 8439)                  │
│  Security: 256-bit symmetric security                     │
│  Purpose: Encrypt VM disk images with authentication      │
│                                                            │
│  Key Size:   256 bits (from Kyber shared secret)          │
│  Nonce Size: 96 bits (random, unique per operation)       │
│  MAC Size:   128 bits (Poly1305 authenticator)            │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ Layer 3: Cryptographic Hashing                            │
│                                                            │
│  Algorithm: BLAKE3                                         │
│  Security: 256-bit collision resistance                   │
│  Purpose: Integrity verification, key derivation          │
│                                                            │
│  Output Size: 256 bits                                    │
│  Speed: ~3 GB/s (on ARM64)                                │
└────────────────────────────────────────────────────────────┘
```

### Encryption Process Flow

**VM Creation:**
1. User provides strong passphrase
2. Argon2id derives 256-bit key from passphrase
3. Kyber-1024 generates public/private keypair
4. Public key stored unencrypted (safe to disclose)
5. Private key encrypted with Argon2id-derived key
6. VM disk image encrypted with ChaCha20-Poly1305

**VM Access:**
1. User enters passphrase
2. Argon2id derives key (verify against stored salt)
3. Decrypt Kyber private key
4. Kyber decapsulates ciphertext → shared secret
5. ChaCha20-Poly1305 decrypts VM disk image
6. BLAKE3 verifies integrity

**Key Rotation (Every 90 Days):**
1. Generate new Kyber keypair
2. Re-encrypt VM disk with new key
3. Securely delete old private key (7-pass overwrite)
4. Update keyring with new public key

### Forward Secrecy

QWAMOS implements **perfect forward secrecy** for VM disks:

- **Ephemeral keys:** New Kyber keypair generated for each session
- **Session-only decryption:** Private keys held in RAM, never written to disk
- **Automatic key deletion:** Keys wiped from memory on VM shutdown

**Benefit:** Compromising one session doesn't expose past sessions.

---

## Network Anonymization

### Tor Integration

**Tor Circuit Isolation:**

Each VM gets its own **isolated Tor circuit** to prevent correlation:

```
VM 1 (Browser)
    ↓
Tor Circuit 1: Guard 1 → Middle 1 → Exit 1
    ↓
Internet (appears as IP A)

VM 2 (Messaging)
    ↓
Tor Circuit 2: Guard 2 → Middle 2 → Exit 2
    ↓
Internet (appears as IP B)

VM 3 (Development)
    ↓
Tor Circuit 3: Guard 3 → Middle 3 → Exit 3
    ↓
Internet (appears as IP C)
```

**Circuit Configuration:**
```
SOCKSPort 9050 IsolateClientAddr IsolateSOCKSAuth IsolateDestAddr IsolateDestPort
```

- **IsolateClientAddr:** Different source VM = different circuit
- **IsolateDestAddr:** Different destination = different circuit
- **Circuit lifetime:** 10 minutes (auto-renewal)

**Hidden Service Support:**
- `.onion` addresses accessible from any VM
- Each VM can host its own hidden service
- Onion authentication (client authorization)

### I2P Integration

**Garlic Routing:**

I2P uses **garlic routing** (multiple messages bundled into single encrypted packet):

```
VM → I2P Router → Garlic Packet (encrypted)
                      ↓
          ┌───────────┴───────────┐
          │  Message 1 (to .i2p)  │
          │  Message 2 (to .i2p)  │
          │  Message 3 (to .i2p)  │
          └───────────────────────┘
                      ↓
             I2P Network (distributed routing)
                      ↓
              Destination .i2p site
```

**I2P Features:**
- **Distributed DHT:** No central directory
- **End-to-end encryption:** All traffic encrypted
- **Unidirectional tunnels:** Inbound and outbound separate
- **Tunnel length:** 3 hops (configurable)

### DNSCrypt

**DNS-over-HTTPS (DoH) with DNSSEC:**

```
VM DNS Query: "check.torproject.org" (plaintext)
         ↓
QWAMOS Gateway intercepts
         ↓
DNSCrypt encrypts query
         ↓
Encrypted DNS over HTTPS → 1.1.1.1 (Cloudflare)
         ↓
DNSSEC-validated response (signed)
         ↓
DNSCrypt decrypts response
         ↓
VM receives: "38.229.70.52" (validated)
```

**Protection Against:**
- ✅ DNS hijacking (DNSSEC signatures verified)
- ✅ ISP DNS logging (encrypted queries)
- ✅ DNS cache poisoning (cryptographic validation)
- ✅ Traffic analysis (query padding)

### Firewall Rules

**Default Deny:**

```bash
# All VMs blocked by default
iptables -P FORWARD DROP

# Explicit allow rules per VM
iptables -A FORWARD -s 10.8.0.2 -d 127.0.0.1 -p tcp --dport 9050 -j ACCEPT  # Tor
iptables -A FORWARD -s 10.8.0.3 -d 127.0.0.1 -p tcp --dport 4444 -j ACCEPT  # I2P

# Block inter-VM communication
iptables -A FORWARD -s 10.8.0.0/24 -d 10.8.0.0/24 -j DROP

# Log all blocked connections
iptables -A FORWARD -j LOG --log-prefix "QWAMOS-BLOCKED: " --log-level 4
```

---

## Known Limitations

### Hardware Limitations

**Baseband Processor:**
- ⚠️ **Cellular modem operates independently** of QWAMOS
- ⚠️ **Cannot be fully isolated** (proprietary firmware)
- ⚠️ **Location tracking** via cell towers persists
- **Mitigation:** Remove SIM card, use airplane mode, Faraday bag

**Bootloader:**
- ⚠️ **Locked bootloaders** prevent custom ROM installation
- ⚠️ **Secure Boot** can block KVM-enabled kernels
- **Mitigation:** Unlock bootloader (if manufacturer allows), verify signatures

**RAM:**
- ⚠️ **Cold boot attacks** can extract encryption keys from RAM
- ⚠️ **Rowhammer** attacks may flip bits in memory
- **Mitigation:** Power off completely (not just screen lock), memory scrambling on panic

### Software Limitations

**Android Kernel:**
- ⚠️ **Vendor-specific patches** may conflict with KVM modules
- ⚠️ **SELinux policies** can block VM operations
- **Mitigation:** Use permissive mode (temporarily), custom kernel

**Performance Overhead:**
- ⚠️ **QEMU (TCG) is slow** (10-20× slower than native)
- ⚠️ **Battery drain** with multiple VMs running
- **Mitigation:** Use KVM hardware acceleration, limit concurrent VMs

**App Compatibility:**
- ⚠️ **Some Android apps require Google Play Services** (not in VMs)
- ⚠️ **DRM-protected apps** may not work in VMs
- **Mitigation:** Use FOSS alternatives, MicroG for limited Google services

### Cryptographic Limitations

**Kyber-1024 Assumptions:**
- ⚠️ **Security relies on** Learning With Errors (LWE) problem hardness
- ⚠️ **Future quantum algorithms** could potentially break LWE
- **Mitigation:** Hybrid encryption (Kyber + classical), algorithm agility

**ChaCha20:**
- ⚠️ **Not quantum-resistant** (but symmetric crypto is quantum-hard)
- ⚠️ **Nonce reuse** breaks security (must be unique)
- **Mitigation:** Automatic nonce generation, strict non-reuse enforcement

**BLAKE3:**
- ⚠️ **Relatively new** (less cryptanalysis than SHA-2)
- **Mitigation:** Dual hashing (BLAKE3 + SHA3) for critical operations

---

## Security Best Practices

### 1. Strong Passphrases

**Minimum Requirements:**
- ✅ 20+ characters
- ✅ Uppercase + lowercase + numbers + symbols
- ✅ No dictionary words
- ✅ No personal information

**Recommended: Diceware**
```
correct-horse-battery-staple-9527-Xylophone!
```

Generate with:
```bash
./crypto/generate_passphrase.sh --words 6 --append-random
```

### 2. Regular Key Rotation

**Rotation Schedule:**
- 🗓️ VM encryption keys: Every 90 days
- 🗓️ Master key: Every 365 days
- 🗓️ Tor circuit: Every 10 minutes (automatic)

**Rotation Command:**
```bash
./crypto/rotate_keys.sh --vm all --schedule 90days
```

### 3. VM Snapshots

**Before Risky Operations:**
```bash
# Snapshot before installing unknown software
./vm/snapshot.sh --vm development --name "before-install"

# Revert if compromised
./vm/revert.sh --vm development --snapshot "before-install"
```

### 4. Disposable VMs

**For One-Time Tasks:**
```bash
# Create disposable VM (auto-deleted after shutdown)
./scripts/create_vm.sh --name temp --disposable

# Use for sensitive operation
./vm/start_vm.sh temp

# Automatically wiped on exit
./vm/stop_vm.sh temp  # VM permanently deleted
```

### 5. Panic Drills

**Practice Emergency Wipe:**
```bash
# Test mode (doesn't actually wipe)
./panic/test_wipe.sh --trigger volume-buttons --dry-run

# Measure wipe time
./panic/benchmark_wipe.sh --level quick
# Output: Quick wipe: 1.2 seconds
```

### 6. Network Auditing

**Monitor Gateway Traffic:**
```bash
# Real-time connection monitoring
./gateway/monitor.sh --live

# Daily audit report
./gateway/audit.sh --date today --output audit-2025-11-18.txt
```

### 7. Update Hygiene

**Weekly Security Updates:**
```bash
# Update QWAMOS
git pull origin master
./scripts/update.sh

# Update VM base images
./vm/update_all.sh --security-only
```

---

## Compliance & Certifications

**QWAMOS aims to meet:**

- ✅ **NIST SP 800-53** (Security controls for federal systems)
- ✅ **NIST FIPS 203** (Kyber-1024 PQC standard)
- ⏳ **Common Criteria EAL4+** (In progress)
- ⏳ **ISO/IEC 15408** (Security evaluation)

**Security Audits:**
- ⏳ **Cure53** (Planned Q1 2026)
- ⏳ **Trail of Bits** (Planned Q2 2026)
- ⏳ **Independent reproducible build verification** (Ongoing)

---

## Reporting Security Issues

**Responsible Disclosure:**

1. **Email:** qwamos@tutanota.com (PGP key in repository)
2. **Subject:** `[SECURITY] Brief description`
3. **Include:**
   - Detailed description
   - Steps to reproduce
   - Affected versions
   - Proposed fix (if known)

**Response Timeline:**
- Initial response: 48 hours
- Severity assessment: 7 days
- Fix development: 30 days (critical), 90 days (moderate)
- Public disclosure: 90 days after fix release

**Bug Bounty:** Coming Q1 2026 ($500-$5,000 per vulnerability)

---

## Next Steps

- **[Developer Guide](Developer-Guide):** Contribute security improvements
- **[FAQ](FAQ):** Common security questions
- **[Roadmap](Roadmap):** Upcoming security features

---

**[← Back to Home](Home)**
