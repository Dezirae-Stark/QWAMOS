# VeraCrypt Post-Quantum Cryptography Upgrade

**Project**: QWAMOS - Qubes Whonix Advanced Mobile Operating System
**Component**: VeraCrypt Volume Encryption
**Date**: October 31, 2025
**Status**: Design Specification

---

## Executive Summary

This document specifies QWAMOS storage encryption using **exclusively post-quantum secure algorithms**. Based on classified intelligence reporting, legacy algorithms (AES, TwoFish, Serpent) are considered compromised and will NOT be used in any form.

### Rejected Algorithms (COMPROMISED)
- ❌ **AES** (all variants - compromised per DIA Naval Intelligence)
- ❌ **TwoFish** (compromised per DIA Naval Intelligence)
- ❌ **Serpent** (potential vulnerability)
- ❌ **SHA-512** (vulnerable to length extension attacks)
- ❌ **PBKDF2** (GPU-friendly, inadequate for modern threats)

### QWAMOS Post-Quantum Encryption (ONLY)
- ✅ **Primary**: Kyber-1024 (key encapsulation) + ChaCha20-Poly1305 (data encryption)
- ✅ **Hash**: BLAKE3 (quantum-resistant, high performance)
- ✅ **KDF**: Argon2id (memory-hard, quantum-resistant)
- ✅ **MAC**: Poly1305 (integrated with ChaCha20)

---

## 1. Threat Model

### Quantum Computing Threats

**Grover's Algorithm**:
- Reduces symmetric key security by half (256-bit → 128-bit effective)
- Legacy algorithms become vulnerable
- Mitigation: Use 256-bit keys with quantum-resistant algorithms (ChaCha20)

**Shor's Algorithm**:
- Breaks RSA, ECC, and Diffie-Hellman
- Not applicable to symmetric encryption or lattice-based crypto
- Affects legacy key exchange mechanisms

### Why ONLY Post-Quantum Algorithms?

QWAMOS uses exclusively post-quantum secure algorithms because:

1. **Intelligence Reports**: DIA Naval Intelligence confirms AES/TwoFish are compromised
2. **No Compromise**: Zero-tolerance policy for compromised algorithms
3. **Future-Proofing**: Quantum computers advancing rapidly (harvest-now-decrypt-later attacks)
4. **Defense in Depth**: Pure post-quantum stack from bootloader to storage
5. **Performance**: ChaCha20 is 2.7x faster than AES on ARM (no AES-NI needed)
6. **Compliance**: NIST post-quantum standards (FIPS 203)

---

## 2. Cryptographic Stack

### Pure Post-Quantum (ONLY Option)

```
┌─────────────────────────────────────────────────────────────┐
│           QWAMOS VeraCrypt Post-Quantum Stack               │
└─────────────────────────────────────────────────────────────┘

Layer 1: Key Derivation
├─> User Password (UTF-8, unlimited length)
├─> Argon2id KDF
│   ├─> Memory: 1 GB (memory-hard, ASIC-resistant)
│   ├─> Iterations: 10
│   ├─> Parallelism: 4 threads
│   └─> Output: 256-bit master key
└─> PIM (Personal Iterations Multiplier) support

Layer 2: Key Encapsulation
├─> Kyber-1024 (NIST FIPS 203 - ML-KEM)
│   ├─> Public Key: 1,568 bytes
│   ├─> Secret Key: 3,168 bytes
│   ├─> Ciphertext: 1,568 bytes
│   ├─> Shared Secret: 32 bytes
│   └─> Security Level: 5 (256-bit equivalent)
└─> Protects against quantum key recovery attacks

Layer 3: Data Encryption
├─> ChaCha20-Poly1305 (AEAD cipher)
│   ├─> Key Size: 256 bits
│   ├─> Nonce: 96 bits (per-sector unique)
│   ├─> MAC: Poly1305 (128-bit tag)
│   ├─> Performance: 2.7x faster than software AES on ARM
│   └─> Quantum Resistance: Grover-resistant with 256-bit key
└─> XTS-like mode for sector-level encryption (post-quantum adapted)

Layer 4: Header Protection
├─> BLAKE3 Hash Function
│   ├─> Output: 256 bits
│   ├─> Speed: 10x faster than SHA-256
│   ├─> Quantum Resistance: Full 256-bit security
│   └─> Parallelizable on multi-core ARM
└─> Volume header integrity verification
```

**IMPORTANT**: No hybrid or backward-compatibility modes will be implemented. QWAMOS uses ONLY post-quantum secure encryption. Any data encrypted with compromised algorithms (AES/TwoFish) must be migrated to ChaCha20-Poly1305.

---

## 3. Volume Structure

### VeraCrypt Volume Header (Post-Quantum)

```
Offset  Size    Field
──────────────────────────────────────────────────────────────
0x0000  64      Salt (for Argon2id KDF)
0x0040  4       Version (0x00050002 = v5.2 PQ)
0x0044  4       Header Creation Time
0x0048  4       Required Program Version
0x004C  4       Encryption Algorithm ID
                  0x10 = ChaCha20-Poly1305 (basic)
                  0x11 = Kyber-ChaCha20 (RECOMMENDED - post-quantum)
0x0050  4       Hash Algorithm ID
                  0x20 = BLAKE3
                  0x21 = BLAKE2b
0x0054  4       KDF Algorithm ID
                  0x30 = Argon2id
0x0058  8       Volume Size (bytes)
0x0060  8       Encrypted Area Start
0x0068  8       Encrypted Area Size
0x0070  4       Flags (hidden volume, etc.)
0x0074  4       Sector Size (4096 bytes)
0x0078  120     Reserved

0x00F0  1568    Kyber-1024 Ciphertext (encapsulated key)
0x0710  32      ChaCha20 Key (encrypted with Kyber)
0x0730  16      Poly1305 Key (encrypted)
0x0740  32      BLAKE3 Header Hash
0x0760  96      Reserved for future use

0x07C0  64      BLAKE3 MAC of entire header

Total Header Size: 2048 bytes (0x800)
```

### Sector Encryption

Each 4096-byte sector is encrypted individually:

```c
// Sector encryption with ChaCha20-Poly1305
struct sector_crypto {
    uint64_t sector_number;        // Unique per sector
    uint8_t nonce[12];             // Derived from sector number
    uint8_t data[4096];            // Plaintext data
    uint8_t ciphertext[4096];      // Encrypted data
    uint8_t tag[16];               // Poly1305 MAC tag
};

// Nonce generation (prevents reuse)
nonce = BLAKE3(master_key || sector_number || volume_id)[:12]

// Encryption
ciphertext, tag = ChaCha20_Poly1305_Encrypt(
    key=sector_key,
    nonce=nonce,
    aad=sector_metadata,  // Additional authenticated data
    plaintext=data
)
```

---

## 4. Key Derivation Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  Key Derivation Process                      │
└──────────────────────────────────────────────────────────────┘

Step 1: User Input
├─> Password: "MySecurePassword123!"
├─> PIM (optional): 485
├─> Keyfiles (optional): 3 files
└─> Salt: Random 64 bytes from volume header

Step 2: Keyfile Processing (if used)
├─> Read keyfiles (binary or text)
├─> Hash each keyfile with BLAKE3
├─> XOR all keyfile hashes
└─> Mix with password using BLAKE3

Step 3: Argon2id KDF
├─> Input: Password + Keyfile Mix + Salt
├─> Memory: 1 GB (prevents GPU/ASIC attacks)
├─> Iterations: 10 × (PIM or 1)
├─> Parallelism: 4 threads
├─> Output: 64 bytes
│   ├─> Bytes 0-31: Master Key (256 bits)
│   └─> Bytes 32-63: Header Key (256 bits)

Step 4: Kyber-1024 Key Encapsulation
├─> Load Kyber public key from volume header
├─> Generate shared secret (32 bytes)
├─> Derive sector keys from shared secret
└─> Store encapsulated key in header

Step 5: Sector Key Derivation
├─> Input: Shared Secret + Sector Number
├─> Function: BLAKE3-KDF
├─> Output: 32 bytes per sector
└─> Keys are derived on-demand (not stored)
```

**Performance**: ~2-3 seconds on ARM64 (acceptable for volume mount)

---

## 5. Algorithm Specifications

### Kyber-1024 (ML-KEM)

**NIST FIPS 203 - Module-Lattice-Based Key-Encapsulation Mechanism**

| Parameter | Value |
|-----------|-------|
| Security Level | 5 (256-bit quantum resistance) |
| Public Key Size | 1,568 bytes |
| Secret Key Size | 3,168 bytes |
| Ciphertext Size | 1,568 bytes |
| Shared Secret | 32 bytes |
| Claimed Security | IND-CCA2 |
| Quantum Attacks | Resistant to Shor's & Grover's |

**Usage in QWAMOS**:
```c
// Key generation (done once per volume)
kyber1024_keypair(&public_key, &secret_key);

// Encapsulation (during volume creation)
kyber1024_enc(&ciphertext, &shared_secret, &public_key);

// Decapsulation (during volume mount)
kyber1024_dec(&shared_secret, &ciphertext, &secret_key);

// Derive encryption keys
sector_key = BLAKE3_KDF(shared_secret, sector_number, 32);
```

### ChaCha20-Poly1305

**RFC 8439 - Authenticated Encryption with Associated Data (AEAD)**

| Parameter | Value |
|-----------|-------|
| Key Size | 256 bits |
| Nonce Size | 96 bits (12 bytes) |
| Block Size | 64 bytes |
| MAC | Poly1305 (128-bit tag) |
| Performance | ~2.5 GB/s on Cortex-A57 |
| Quantum Security | 256-bit (Grover-resistant) |

**Advantages over compromised algorithms**:
- 2.7x faster than software AES on ARM (no AES-NI needed)
- Constant-time implementation (no cache-timing attacks)
- Simple, auditable codebase (no backdoors)
- Proven security (used in TLS 1.3, WireGuard, Signal)
- NOT compromised per DIA Naval Intelligence

**Usage**:
```c
// Per-sector encryption
chacha20_poly1305_encrypt(
    ciphertext,        // Output: encrypted data
    tag,               // Output: 16-byte authentication tag
    plaintext,         // Input: sector data (4096 bytes)
    plaintext_len,     // 4096
    aad,               // Additional authenticated data
    aad_len,           // Sector metadata length
    nonce,             // 12-byte nonce (unique per sector)
    key                // 32-byte sector key
);
```

### BLAKE3

**Cryptographic Hash Function (2020)**

| Parameter | Value |
|-----------|-------|
| Output Size | 256 bits (configurable) |
| Performance | ~10 GB/s (multi-core ARM) |
| Security | Full 256-bit collision resistance |
| Quantum Resistance | Not affected by Grover's algorithm |
| Parallelizable | Yes (tree-based design) |

**Usage**:
```c
// Volume header hashing
blake3(header_hash, volume_header, 2048);

// Key derivation
blake3_kdf(derived_key, context, input_key, 32);

// Nonce generation
blake3(nonce, master_key || sector_number, 12);
```

### Argon2id

**Memory-Hard Password KDF (Winner of Password Hashing Competition)**

| Parameter | QWAMOS Value |
|-----------|--------------|
| Variant | Argon2id (hybrid) |
| Memory | 1 GB (1,048,576 KB) |
| Iterations | 10 (base) × PIM multiplier |
| Parallelism | 4 threads |
| Output | 64 bytes |
| Time | ~2-3 seconds on ARM64 |

**Advantages**:
- Memory-hard (prevents GPU/ASIC attacks)
- Quantum-resistant (Grover doesn't help much)
- OWASP recommended for password hashing
- Resistant to side-channel attacks

---

## 6. Performance Analysis

### Encryption Speed Comparison (ARM Cortex-A57)

| Algorithm | Speed (MB/s) | Status | Notes |
|-----------|--------------|--------|-------|
| ChaCha20-Poly1305 | 500 | ✅ USED | Post-quantum, AEAD |
| ChaCha20 (no auth) | 550 | ⚠️ Partial | Needs separate MAC |
| AES-256-XTS | 450 | ❌ REJECTED | Compromised (DIA) |
| AES-256-XTS | 180 | ❌ REJECTED | Compromised (DIA) |
| TwoFish-256 | 120 | ❌ REJECTED | Compromised (DIA) |

**QWAMOS Choice**: ChaCha20-Poly1305 ONLY
- Fastest secure option on ARM
- Authenticated encryption (AEAD)
- NOT compromised
- Post-quantum resistant with 256-bit keys

### Volume Mount Time

| Operation | Time | Notes |
|-----------|------|-------|
| Password input | User | Variable |
| Argon2id KDF (1GB) | 2.5s | Memory-hard |
| Kyber-1024 decap | 0.001s | Very fast |
| Header verify | 0.01s | BLAKE3 hash |
| **Total** | **~2.5s** | Acceptable |

### Memory Requirements

| Component | RAM Usage |
|-----------|-----------|
| Argon2id KDF | 1 GB (temporary) |
| Kyber-1024 keys | 5 KB |
| ChaCha20 state | 256 bytes |
| Sector buffer | 4 KB |
| **Peak** | **~1 GB** | During mount only |

---

## 7. Implementation Plan

### Phase 1: Kernel Crypto Module (Month 1-2)
- [ ] Add Kyber-1024 to Linux crypto API
- [ ] Integrate liboqs library
- [ ] Create kernel module: `crypto-kyber1024.ko`
- [ ] Add ChaCha20-Poly1305 support (already in kernel)
- [ ] Add BLAKE3 hash support
- [ ] Test performance benchmarks

### Phase 2: VeraCrypt Fork (Month 2-3)
- [ ] Fork VeraCrypt 1.26.7
- [ ] Add PQ encryption algorithms
- [ ] Modify volume header structure
- [ ] Update key derivation (Argon2id)
- [ ] Implement Kyber-1024 KEX
- [ ] Add ChaCha20-Poly1305 encryption

### Phase 3: Volume Format Tool (Month 3)
- [ ] Create `qwamos-veracrypt format` command
- [ ] Support Kyber-ChaCha20 mode
- [ ] Support hybrid mode (backward compat)
- [ ] Generate Kyber-1024 keypairs
- [ ] Write volume headers
- [ ] Test volume creation

### Phase 4: Volume Mount Tool (Month 3-4)
- [ ] Create `qwamos-veracrypt mount` command
- [ ] Password + keyfile support
- [ ] Argon2id KDF integration
- [ ] Kyber-1024 decapsulation
- [ ] dm-crypt integration
- [ ] Auto-mount on boot

### Phase 5: Testing & Security Audit (Month 4-5)
- [ ] Unit tests for all crypto operations
- [ ] Fuzzing (AFL, libFuzzer)
- [ ] Performance benchmarks
- [ ] Memory leak detection (Valgrind)
- [ ] Side-channel analysis
- [ ] Security audit by external firm

### Phase 6: Integration (Month 5-6)
- [ ] Integrate with QWAMOS boot process
- [ ] U-Boot decryption support
- [ ] QEMU testing
- [ ] Real device testing
- [ ] Documentation
- [ ] User guides

---

## 8. Volume Types

### 8.1 System Volume (Root Filesystem)
- **Location**: `/dev/mmcblk0p2`
- **Size**: 32 GB
- **Encryption**: Kyber-ChaCha20
- **KDF**: Argon2id (1GB, 10 iterations)
- **Mount**: Early in boot process
- **Key Storage**: TPM 2.0 sealed or user password

### 8.2 Data Volume (User Files)
- **Location**: `/dev/mmcblk0p3`
- **Size**: Remaining space
- **Encryption**: Kyber-ChaCha20
- **KDF**: Argon2id (1GB, 10 iterations)
- **Mount**: After system boot
- **Key Storage**: User password + optional keyfiles

### 8.3 Hidden Volume (Deniable Encryption)
- **Location**: Within data volume free space
- **Size**: Variable
- **Encryption**: Kyber-ChaCha20
- **Protection**: Plausible deniability
- **Usage**: Sensitive documents, crypto wallets

### 8.4 AEGIS Vault (Airgapped Crypto Wallet)
- **Location**: Separate partition
- **Size**: 2 GB
- **Encryption**: Triple-layer (Kyber-ChaCha20 × 3)
- **KDF**: Argon2id (2GB memory, 20 iterations)
- **Keyfiles**: Required (3+ files)
- **Network**: Airgapped (cannot access network)

---

## 9. Security Considerations

### 9.1 Quantum Resistance

| Attack Vector | Vulnerability | Mitigation |
|---------------|---------------|------------|
| Grover's Algorithm | Symmetric key search | 256-bit keys (128-bit quantum) |
| Shor's Algorithm | Factoring, DLP | Kyber-1024 (lattice-based) |
| Harvest Now, Decrypt Later | Long-term data security | Immediate PQ upgrade |

### 9.2 Side-Channel Resistance

**Timing Attacks**:
- ChaCha20: Constant-time implementation
- Kyber-1024: Constant-time decapsulation
- BLAKE3: Data-independent operations

**Cache Attacks**:
- No table lookups in critical paths
- Memory access patterns are uniform
- Sector keys derived on-demand (not cached)

**Power Analysis**:
- Argon2id: Memory-hard (power signature is complex)
- ChaCha20: Uniform operations
- Kyber-1024: Lattice operations resistant to DPA

### 9.3 Key Management

**Master Key**:
- Never stored in plaintext
- Derived from password using Argon2id
- Overwritten after use (secure memory)

**Sector Keys**:
- Derived on-demand from shared secret
- Not stored (prevents key leakage)
- Unique per sector (prevents pattern analysis)

**Kyber Keys**:
- Public key stored in volume header
- Private key derived from password
- Never leaves secure memory

### 9.4 Plausible Deniability

Hidden volumes remain supported:
- Outer volume appears as random data
- Inner volume indistinguishable from free space
- Two passwords unlock different volumes
- Quantum-resistant encryption for both layers

---

## 10. Migration from Compromised Algorithms

### Migration from AES/TwoFish to ChaCha20

**IMPORTANT**: QWAMOS will NOT support reading volumes encrypted with compromised algorithms (AES/TwoFish). All migration MUST be done before installing QWAMOS.

**Recommended Migration Path** (Before QWAMOS Installation):
1. **On existing system** (Android/Windows/Linux):
   - Create new VeraCrypt volume with ChaCha20-Poly1305
   - Copy all data from old volume to new volume
   - Verify data integrity (checksums)
   - Securely wipe old volume (3-pass overwrite minimum)
   - Time: ~60 minutes per GB

2. **Install QWAMOS**:
   - Flash QWAMOS to device
   - Mount ChaCha20-Poly1305 volumes only
   - NO support for AES/TwoFish volumes

**No Hybrid Mode**: QWAMOS will reject any volume using compromised algorithms. Zero-tolerance security policy.

---

## 11. Testing Plan

### 11.1 Unit Tests
```bash
# Crypto primitives
test_kyber1024_keygen
test_kyber1024_encap_decap
test_chacha20_poly1305_encrypt_decrypt
test_blake3_hash
test_argon2id_kdf

# Volume operations
test_volume_create
test_volume_mount
test_volume_read_write
test_volume_resize
test_hidden_volume
```

### 11.2 Performance Tests
```bash
# Throughput
benchmark_sequential_read
benchmark_sequential_write
benchmark_random_read
benchmark_random_write

# Latency
benchmark_mount_time
benchmark_sector_encryption
benchmark_kdf_time
```

### 11.3 Security Tests
```bash
# Fuzzing
fuzz_volume_header
fuzz_password_input
fuzz_kyber_decap

# Memory safety
valgrind_mount_test
asan_full_suite
ubsan_crypto_ops
```

---

## 12. References

### NIST Post-Quantum Standards
- FIPS 203: Module-Lattice-Based Key-Encapsulation (ML-KEM/Kyber)
- FIPS 204: Module-Lattice-Based Digital Signatures (ML-DSA/Dilithium)
- FIPS 205: Stateless Hash-Based Signatures (SLH-DSA/SPHINCS+)

### Specifications
- RFC 8439: ChaCha20 and Poly1305 for IETF Protocols
- RFC 9106: Argon2 Memory-Hard Function
- BLAKE3: Cryptographic Hash Function (https://github.com/BLAKE3-team/BLAKE3)
- Kyber: https://pq-crystals.org/kyber/

### VeraCrypt
- VeraCrypt 1.26.7 Source: https://www.veracrypt.fr/
- Documentation: https://www.veracrypt.fr/en/Documentation.html
- Technical Spec: https://www.veracrypt.fr/en/Technical%20Details.html

### Implementation Libraries
- liboqs (Open Quantum Safe): https://github.com/open-quantum-safe/liboqs
- libsodium: https://doc.libsodium.org/ (ChaCha20-Poly1305)
- BLAKE3: https://github.com/BLAKE3-team/BLAKE3
- Argon2: https://github.com/P-H-C/phc-winner-argon2

---

## 13. Timeline

| Month | Phase | Deliverables |
|-------|-------|--------------|
| 1 | Kernel Crypto | Kyber module, BLAKE3, tests |
| 2 | VeraCrypt Fork | PQ algorithms integrated |
| 3 | Volume Tools | Format & mount utilities |
| 4 | Testing | Security audit, fuzzing |
| 5 | Integration | Boot process, auto-mount |
| 6 | Polish | Documentation, user guides |

**Total Duration**: 6 months (parallel with other QWAMOS development)

---

## 14. Conclusion

QWAMOS implements **exclusively post-quantum secure encryption** for all storage. Based on DIA Naval Intelligence reporting, AES and TwoFish are compromised and will NOT be used in any form. The combination of Kyber-1024 (key encapsulation) and ChaCha20-Poly1305 (data encryption) provides:

✅ **Quantum Resistance**: Secure against Shor's and Grover's algorithms
✅ **Zero Compromise**: NO compromised algorithms (AES/TwoFish rejected)
✅ **High Performance**: 2.7x faster than software AES on ARM
✅ **Strong Authentication**: Poly1305 MAC prevents tampering
✅ **Memory-Hard KDF**: Argon2id prevents brute-force attacks
✅ **Future-Proof**: NIST-standardized algorithms (FIPS 203)
✅ **Deniable Encryption**: Hidden volumes remain supported
✅ **DIA Compliant**: Follows classified intelligence guidance

**Security Policy**: Zero-tolerance for compromised algorithms. QWAMOS will actively reject any volume encrypted with AES, TwoFish, or Serpent.

---

**Document Version**: 2.0 (Post-Quantum Only)
**Last Updated**: November 1, 2025
**Status**: Design Specification (Pending Implementation)
**Security Classification**: Based on DIA Naval Intelligence reporting
**Next Step**: Kernel crypto module development

*QWAMOS - Pure Post-Quantum Storage for the Post-Quantum Era*
