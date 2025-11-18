# Post-Quantum Storage Subsystem Design Document

## Executive Summary

QWAMOS Phase XIII implements a quantum-resistant encrypted storage layer using Kyber-1024 for key encapsulation and ChaCha20-Poly1305 for bulk encryption. This protects all VM disk images and user data against future quantum computer attacks while maintaining performance comparable to classical encryption schemes.

## Threat Model

### Adversary Capabilities
- **Harvest Now, Decrypt Later**: Adversary records encrypted data today, decrypts with quantum computer in 10-15 years
- **Quantum Computers**: Shor's algorithm breaks RSA/ECC, Grover's algorithm weakens AES-256 to AES-128 equivalent
- **Physical Access**: Adversary may seize device and attempt offline decryption
- **Side Channels**: Timing attacks, power analysis, electromagnetic emanations

### Protection Goals
- **Long-Term Confidentiality**: Data encrypted today remains secure for 30+ years
- **Integrity**: Detect any tampering with encrypted data (authenticated encryption)
- **Key Isolation**: Compromise of one key doesn't compromise other VMs
- **Forward Secrecy**: Past encrypted data unrecoverable after key rotation

## Cryptographic Primitives

### Kyber-1024 (KEM)

**Security Level**: NIST PQC Level 5 (~AES-256 equivalent against quantum attacks)

**Key Sizes**:
- Public key: 1,568 bytes
- Secret key: 3,168 bytes
- Ciphertext: 1,568 bytes
- Shared secret: 32 bytes

**Performance** (ARM64):
- Key generation: ~500 µs
- Encapsulation: ~600 µs
- Decapsulation: ~700 µs

**Use Case**: Wrap symmetric keys for storage encryption

### ChaCha20-Poly1305 (AEAD)

**Security Level**: 256-bit key, 128-bit authentication tag

**Performance** (ARM64 with NEON):
- Encryption: 800-1200 MB/s
- Decryption: 800-1200 MB/s

**Use Case**: Bulk data encryption (VM disk images)

### BLAKE3 (Hash Function)

**Security Level**: 256-bit output

**Performance** (ARM64):
- Hashing: 3-5 GB/s

**Use Case**: Integrity verification, key derivation

## Storage Container Format

### PQCrypt Volume Header (4 KB)

```
Offset | Size | Field | Description
-------|------|-------|------------
0      | 16   | Magic | "QWAMOS_PQC_V1\0\0"
16     | 8    | Version | Container format version (1)
24     | 8    | Flags | Encryption flags (compression, etc.)
32     | 32   | Volume UUID | Unique identifier
64     | 8    | Data Size | Encrypted data size (bytes)
72     | 8    | Block Size | Cipher block size (typically 4096)
80     | 1568 | Kyber CT | Kyber-1024 ciphertext (wrapped key)
1648   | 32   | Salt | Random salt for key derivation
1680   | 32   | Header Hash | BLAKE3(header[0:1680])
1712   | 2384 | Reserved | Future use (padding to 4096)
```

### Encrypted Data Blocks

Each 4 KB block:
```
[12-byte nonce][Encrypted data (4064 bytes)][16-byte Poly1305 tag][4-byte reserved]
```

**Nonce Construction**: `BLAKE3(volume_uuid || block_number || salt)[0:12]`

## Key Hierarchy

```
[User Password/Biometric]
        ↓
    BLAKE3-KDF
        ↓
[Master Seed (32 bytes)] → Stored in Android StrongBox
        ↓
    BLAKE3-KDF("vm-gateway")
        ↓
[Gateway VM Key (32 bytes)]
        ↓
    Kyber-1024 Encapsulate
        ↓
[Kyber Ciphertext (1568 bytes)] → Stored in volume header
        ↓
    Kyber-1024 Decapsulate
        ↓
[ChaCha20 Key (32 bytes)] → Used for disk encryption
```

## Disk Encryption Layer

### Option 1: Custom dm-pqcrypt Kernel Module

**Advantages**:
- Transparent to filesystem layer
- Kernel-space performance
- Integrates with device mapper stack

**Disadvantages**:
- Requires kernel modification
- Complex maintenance
- Potential security vulnerabilities in kernel module

**Implementation**:
```c
// Simplified dm-pqcrypt target
static int dm_pqcrypt_ctr(struct dm_target *ti, unsigned int argc, char **argv) {
    // Initialize ChaCha20-Poly1305 context
    // Load Kyber-wrapped key from volume header
    // Decapsulate to get symmetric key
}

static int dm_pqcrypt_map(struct dm_target *ti, struct bio *bio) {
    // Encrypt/decrypt bio using ChaCha20-Poly1305
    // Verify Poly1305 tag on reads
}
```

### Option 2: FUSE Userspace Filesystem

**Advantages**:
- No kernel modifications required
- Easier debugging and updates
- Portable across devices

**Disadvantages**:
- Higher overhead (userspace/kernel transitions)
- Lower performance (~40% slower)

**Implementation**: Use libfuse with encryption callback

### Recommended Approach

**Hybrid**: Use dm-pqcrypt for production (performance), FUSE for development/testing

## Performance Optimization

### Hardware Acceleration

**ARM Crypto Extensions** (available on all modern ARM64):
- ChaCha20: Vectorized with NEON instructions
- Poly1305: Optimized with VMULL instruction
- BLAKE3: SIMD-accelerated

**Expected Speedup**: 2-3x over software-only implementation

### Caching Strategy

**Read-Ahead**:
- Decrypt next 16 blocks in background
- Keep decrypted cache of frequently accessed blocks
- LRU eviction policy

**Write-Behind**:
- Batch small writes into full blocks
- Encrypt asynchronously
- Flush on fsync() or timeout

### Block Size Selection

| Block Size | Throughput | Latency | Overhead |
|-----------|------------|---------|----------|
| 512 bytes | Low | Low | High (16-byte tag per 512 bytes = 3.1%) |
| 4 KB | Medium | Medium | Medium (16-byte tag per 4 KB = 0.4%) |
| 64 KB | High | High | Low (16-byte tag per 64 KB = 0.024%) |

**Recommendation**: 4 KB (balance between overhead and latency)

## Security Considerations

### Key Zeroization

All symmetric keys must be securely erased from memory after use:

```c
void secure_zero(void *ptr, size_t len) {
    volatile uint8_t *p = ptr;
    while (len--) *p++ = 0;
}
```

Use `mlock()` to prevent keys from being swapped to disk.

### Side-Channel Resistance

**Timing Attacks**: Use constant-time implementations (libsodium provides this)

**Power Analysis**: Difficult to mitigate on mobile; rely on Android secure element

**Cache Attacks**: Flush sensitive data from cache after use

### Quantum Security Analysis

**Kyber-1024 Security**:
- Classical security: ~230 bits
- Quantum security: ~233 bits (NIST Level 5)
- Grover speedup: Not applicable (lattice-based, not symmetric)

**ChaCha20 Security**:
- Classical: 256 bits
- Quantum (Grover): 128 bits effective
- Recommendation: Acceptable for 30+ year security

## Migration Strategy

### Migrating from Unencrypted VMs

1. Create new PQCrypt volume (same size as VM disk)
2. Boot VM from old unencrypted disk (read-only)
3. Stream copy to encrypted volume
4. Verify integrity (checksums)
5. Swap volumes, delete old unencrypted disk

**Estimated Time**: ~5 minutes per GB at 200 MB/s copy speed

### Migrating from Classical Encryption (AES)

Similar process, but also re-encrypt with PQC keys.

## Testing and Validation

### Cryptographic Tests

1. **Kyber-1024**: NIST KAT (Known Answer Tests) from reference implementation
2. **ChaCha20-Poly1305**: RFC 8439 test vectors
3. **BLAKE3**: Official test vectors from BLAKE3 repo

### Functional Tests

1. Create volume, write data, unmount, mount, verify
2. Power loss simulation (unclean shutdown during write)
3. Corrupted header recovery
4. Key rotation and re-encryption

### Performance Benchmarks

```bash
# Sequential read/write
fio --name=seq_read --rw=read --bs=1M --size=1G --filename=/dev/pqcrypt0

# Random 4K read/write (IOPS test)
fio --name=rand_rw --rw=randrw --bs=4K --size=1G --filename=/dev/pqcrypt0

# CPU overhead
perf stat -e cycles,instructions ./benchmark_pqcrypt
```

### Security Audit

1. Formal verification of key derivation (ProVerif or Tamarin)
2. Fuzzing of volume header parser (AFL, libFuzzer)
3. Side-channel testing (ChipWhisperer for power analysis)
4. Penetration testing (attempt to recover keys from seized device)

## References

- [Kyber NIST Submission](https://pq-crystals.org/kyber/)
- [ChaCha20-Poly1305 RFC 8439](https://tools.ietf.org/html/rfc8439)
- [BLAKE3 Specification](https://github.com/BLAKE3-team/BLAKE3-specs)
- [dm-crypt Documentation](https://gitlab.com/cryptsetup/cryptsetup/-/wikis/DMCrypt)
- [NIST PQC Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
**Status:** Design Phase
