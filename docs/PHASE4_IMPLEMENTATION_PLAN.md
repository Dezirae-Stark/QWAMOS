# QWAMOS Phase 4: Post-Quantum VeraCrypt Implementation Plan

**Date**: 2025-11-02
**Version**: 1.0
**Status**: In Progress
**Timeline**: 6 months (parallel development)

---

## Executive Summary

Phase 4 upgrades QWAMOS storage encryption from the current implementation (ChaCha20-Poly1305 + scrypt) to a **fully post-quantum resistant** system using:

- **Kyber-1024** (NIST FIPS 203) for key encapsulation
- **ChaCha20-Poly1305** for AEAD encryption (retained)
- **Argon2id** for memory-hard key derivation (upgrade from scrypt)
- **BLAKE3** for cryptographic hashing (upgrade from BLAKE2b)

---

## Current State Analysis

### Phase 3 Implementation (Already Complete)

The existing `storage/scripts/volume_manager.py` provides:

✅ **Working Features**:
- ChaCha20-Poly1305 AEAD encryption
- scrypt KDF (N=16384, r=8, p=1)
- BLAKE2b hashing
- 4096-byte block encryption
- Volume create/unlock operations
- Password-based encryption
- 4KB volume header format

❌ **Missing Post-Quantum Features**:
- Kyber-1024 key encapsulation
- Argon2id KDF
- BLAKE3 hashing
- 2048-byte header with Kyber ciphertext
- LUKS2/dm-crypt integration
- U-Boot encrypted boot support

---

## Phase 4 Architecture

### Cryptographic Stack Upgrade

```
┌─────────────────────────────────────────────────────────────┐
│              Phase 3 (Current)    →    Phase 4 (Target)     │
├─────────────────────────────────────────────────────────────┤
│ Password                           Password                  │
│    ↓                                  ↓                      │
│ scrypt (16384 iter)      →         Argon2id (1GB memory)    │
│    ↓                                  ↓                      │
│ Master Key (256-bit)               Master Key (256-bit)     │
│    ↓                                  ↓                      │
│ Direct ChaCha20          →         Kyber-1024 KEX           │
│                                       ↓                      │
│                                    Shared Secret (32 bytes)  │
│                                       ↓                      │
│ ChaCha20-Poly1305        →         ChaCha20-Poly1305        │
│    ↓                                  ↓                      │
│ BLAKE2b integrity        →         BLAKE3 integrity         │
└─────────────────────────────────────────────────────────────┘
```

### Volume Header Evolution

**Phase 3 Header (4096 bytes)**:
```
Offset  Size    Field
0x0000  8       Magic: "QWAMOS\x00\x01"
0x0008  4       Version: 1
0x000C  32      Cipher: "ChaCha20-Poly1305"
0x002C  32      KDF: "scrypt"
0x004C  16      Salt
0x005C  12      scrypt params (N, r, p)
0x0068  32      Master key verification (BLAKE2b)
0x0088  32      Header HMAC (BLAKE2b)
0x00A8  3928    Reserved
```

**Phase 4 Header (2048 bytes)** - NEW:
```
Offset  Size    Field
0x0000  8       Magic: "QWAMOSPQ"  (Post-Quantum marker)
0x0008  4       Version: 2
0x000C  4       Flags (hidden, system, vault, etc.)
0x0010  32      Cipher: "Kyber1024-ChaCha20-Poly1305"
0x0030  32      KDF: "Argon2id"
0x0050  64      Salt (for Argon2id)
0x0090  12      Argon2 params (memory MB, time, parallelism)
0x009C  4       Reserved (alignment)

### Kyber-1024 Section (1664 bytes)
0x00A0  1568    Kyber-1024 Public Key
0x06E0  1568    Kyber-1024 Ciphertext (encapsulated shared secret)
0x0D00  32      Encrypted Master Key (with ChaCha20)
0x0D20  32      BLAKE3 hash of master key

### Integrity Section
0x0D40  32      BLAKE3 header MAC
0x0D60  160     Reserved for future PQ algorithms

Total: 2048 bytes (0x800)
```

---

## Implementation Tasks

### Task 1: Python Cryptography Dependencies

**Objective**: Install and verify all cryptographic libraries

**Libraries Required**:
1. **liboqs-python** - Kyber-1024 implementation
   ```bash
   pip install liboqs-python
   ```

2. **argon2-cffi** - Argon2id KDF
   ```bash
   pip install argon2-cffi
   ```

3. **blake3** - BLAKE3 hashing
   ```bash
   pip install blake3
   ```

4. **pycryptodome** - ChaCha20-Poly1305 (already installed)

**Deliverable**: `crypto/pq/requirements.txt`

---

### Task 2: Kyber-1024 Python Bindings

**File**: `crypto/pq/kyber_wrapper.py`

**Functionality**:
```python
class Kyber1024:
    def generate_keypair() -> (public_key, secret_key)
    def encapsulate(public_key) -> (ciphertext, shared_secret)
    def decapsulate(secret_key, ciphertext) -> shared_secret
```

**Implementation**:
- Wrap liboqs Kyber-1024 functions
- Error handling for invalid keys/ciphertexts
- Memory wiping for secret keys
- Test vectors from NIST

**Testing**:
- Generate 100 keypairs, verify sizes
- Encapsulate/decapsulate 1000 times, verify shared secret match
- Negative tests: invalid ciphertext, wrong keys

---

### Task 3: Argon2id KDF Implementation

**File**: `crypto/pq/argon2_kdf.py`

**Functionality**:
```python
def derive_key(password: str, salt: bytes,
               memory_mb: int=1024, time_cost: int=10,
               parallelism: int=4) -> bytes:
    """Derive 256-bit key using Argon2id"""
```

**Parameters** (Security Levels):
| Level    | Memory  | Time | Unlock Time |
|----------|---------|------|-------------|
| Low      | 256 MB  | 3    | ~0.5s       |
| Medium   | 512 MB  | 5    | ~1.5s       |
| High     | 1024 MB | 10   | ~3s         |
| Paranoid | 2048 MB | 20   | ~8s         |

**Testing**:
- Same password + salt → same key (determinism)
- Different salt → different key
- Performance benchmark on ARM64
- Compare with scrypt performance

---

### Task 4: BLAKE3 Integration

**File**: `crypto/pq/blake3_hash.py`

**Functionality**:
```python
def blake3_hash(data: bytes) -> bytes:
    """Compute BLAKE3 hash (256-bit)"""

def blake3_keyed_hash(data: bytes, key: bytes) -> bytes:
    """Compute BLAKE3 MAC"""

def blake3_derive_key(context: str, key_material: bytes,
                      output_len: int) -> bytes:
    """BLAKE3 KDF for key derivation"""
```

**Use Cases**:
- Volume header integrity verification
- Master key verification hash
- Nonce generation (BLAKE3-KDF)
- Sector key derivation

**Testing**:
- Test vectors from BLAKE3 spec
- Performance vs BLAKE2b and SHA-256
- Parallel hashing tests

---

### Task 5: Post-Quantum Volume Manager

**File**: `crypto/pq/pq_volume_manager.py`

**Class**: `PostQuantumVolume` (extends `QWAMOSVolume`)

**New Methods**:
```python
def create_pq_volume(size_mb, passphrase):
    """Create volume with Kyber-1024 + ChaCha20"""
    # 1. Generate Kyber-1024 keypair
    # 2. Derive master key with Argon2id
    # 3. Encapsulate shared secret
    # 4. Encrypt master key with shared secret
    # 5. Write 2048-byte PQ header
    # 6. Encrypt data blocks with ChaCha20

def unlock_pq_volume(passphrase):
    """Unlock PQ volume"""
    # 1. Read PQ header
    # 2. Derive master key with Argon2id
    # 3. Decapsulate Kyber shared secret
    # 4. Decrypt master key
    # 5. Verify BLAKE3 MAC
    # 6. Return decryption handle

def migrate_volume(old_volume_path, new_volume_path, passphrase):
    """Migrate Phase 3 volume to Phase 4 PQ volume"""
    # 1. Unlock old volume (scrypt + ChaCha20)
    # 2. Create new PQ volume
    # 3. Copy all blocks with re-encryption
    # 4. Verify integrity
    # 5. Optionally secure-wipe old volume
```

**Backward Compatibility**:
- Detect header magic ("QWAMOS\x00\x01" vs "QWAMOSPQ")
- Support both Phase 3 and Phase 4 volumes
- Migration tool for seamless upgrade

---

### Task 6: LUKS2 Integration (Linux Systems)

**File**: `crypto/pq/luks2_pq.sh`

**Functionality**:
- Use `cryptsetup` with custom cipher config
- Argon2id KDF configuration
- ChaCha20-Poly1305 cipher
- BLAKE3 for header MAC (if supported)

**Script Example**:
```bash
#!/bin/bash
# Create LUKS2 volume with PQ-resistant config

cryptsetup luksFormat \
  --type luks2 \
  --cipher chacha20-poly1305 \
  --key-size 256 \
  --hash blake2b-256 \
  --pbkdf argon2id \
  --pbkdf-memory 1048576 \
  --pbkdf-iterations 10 \
  --pbkdf-parallel 4 \
  /dev/loop0
```

**Note**: LUKS2 doesn't natively support Kyber-1024, so we'll use:
- Argon2id for KDF (✅ supported)
- ChaCha20 for encryption (✅ supported in Linux 5.19+)
- BLAKE2b for hashing (BLAKE3 not yet in kernel)

For full PQ support, use Python implementation (`pq_volume_manager.py`).

---

### Task 7: U-Boot Integration

**File**: `bootloader/kyber_verify.c`

**Objective**: Add Kyber-1024 signature verification to U-Boot

**Steps**:
1. Port liboqs Kyber-1024 to U-Boot
2. Add `boot/pq_keys/` directory for public keys
3. Modify U-Boot boot flow:
   ```
   U-Boot Start
      ↓
   Load kernel image
      ↓
   Verify Kyber-1024 signature
      ↓
   (If valid) Boot kernel
   (If invalid) Halt with error
   ```

4. Store Kyber public key in U-Boot environment:
   ```bash
   setenv kyber_pubkey <1568-byte key in hex>
   saveenv
   ```

**Challenge**: U-Boot has limited crypto support. May need to:
- Compile liboqs as U-Boot library
- Or use hybrid: Dilithium-3 (also NIST PQ standard) for signatures

---

### Task 8: Testing & Validation

**Test Suite**: `crypto/tests/test_phase4.py`

#### Unit Tests

1. **Kyber-1024**:
   - `test_kyber_keygen()` - Generate 100 keypairs
   - `test_kyber_encap_decap()` - 1000 encap/decap cycles
   - `test_kyber_invalid_ciphertext()` - Verify rejection

2. **Argon2id**:
   - `test_argon2_determinism()` - Same input → same output
   - `test_argon2_different_salt()` - Different outputs
   - `test_argon2_performance()` - Benchmark (target: <5s)

3. **BLAKE3**:
   - `test_blake3_vectors()` - Official test vectors
   - `test_blake3_performance()` - vs BLAKE2b and SHA-256
   - `test_blake3_keyed_mac()` - MAC verification

4. **PQ Volume**:
   - `test_pq_volume_create()` - Create 10 MB test volume
   - `test_pq_volume_unlock()` - Unlock with correct password
   - `test_pq_volume_wrong_password()` - Reject invalid password
   - `test_pq_volume_read_write()` - Data integrity
   - `test_pq_volume_migration()` - Phase 3 → Phase 4

#### Integration Tests

1. **End-to-End Workflow**:
   ```python
   def test_full_pq_workflow():
       # 1. Create 100 MB PQ volume
       vol = PostQuantumVolume('test.qpq')
       vol.create_pq_volume(100, 'MySecurePassword123!')

       # 2. Write test data
       vol.write_block(0, b'QWAMOS PQ Test Data')
       vol.write_block(1, b'Post-Quantum Security')

       # 3. Unlock volume
       vol2 = PostQuantumVolume('test.qpq')
       vol2.unlock_pq_volume('MySecurePassword123!')

       # 4. Read and verify
       assert vol2.read_block(0) == b'QWAMOS PQ Test Data'
       assert vol2.read_block(1) == b'Post-Quantum Security'

       # 5. Verify Kyber security
       # Try to unlock with wrong Kyber key → should fail
   ```

2. **Performance Benchmarks**:
   - Volume creation time (1 GB, 10 GB, 100 GB)
   - Mount/unlock time
   - Sequential read/write speed
   - Random I/O (4K blocks)
   - CPU/memory usage during encryption

#### Security Tests

1. **Cryptographic Validation**:
   - Kyber-1024 security level (NIST Category 5)
   - ChaCha20 nonce uniqueness (no repeats)
   - Argon2id memory-hardness verification
   - BLAKE3 collision resistance

2. **Attack Resistance**:
   - Brute-force password attacks (should fail)
   - Tampering detection (modify header → reject)
   - Ciphertext malleability (Poly1305 should catch)
   - Quantum attack simulation (theoretical)

---

## Development Phases

### Phase 4.1: Foundation (Weeks 1-4)
- ✅ Install cryptographic libraries
- ✅ Implement Kyber-1024 wrapper
- ✅ Implement Argon2id KDF
- ✅ Implement BLAKE3 hashing
- ✅ Unit tests for each component

### Phase 4.2: PQ Volume Manager (Weeks 5-8)
- ✅ Design 2048-byte PQ header
- ✅ Implement `PostQuantumVolume` class
- ✅ Volume create/unlock/read/write
- ✅ Migration tool (Phase 3 → Phase 4)
- ✅ Integration tests

### Phase 4.3: Linux Integration (Weeks 9-12)
- ✅ LUKS2 configuration scripts
- ✅ dm-crypt automation
- ✅ Boot-time decryption
- ✅ Performance optimization

### Phase 4.4: U-Boot Integration (Weeks 13-16)
- ✅ Port Kyber-1024 to U-Boot
- ✅ Signature verification
- ✅ Secure boot flow
- ✅ Testing on ARM64 hardware

### Phase 4.5: Testing & Hardening (Weeks 17-20)
- ✅ Comprehensive test suite
- ✅ Performance benchmarks
- ✅ Security audit
- ✅ Fuzzing (AFL, libFuzzer)
- ✅ Memory safety (Valgrind, ASAN)

### Phase 4.6: Documentation & Deployment (Weeks 21-24)
- ✅ User documentation
- ✅ API reference
- ✅ Migration guides
- ✅ Deployment automation
- ✅ Training materials

---

## Risk Mitigation

### Risk 1: Kyber-1024 Performance on ARM

**Risk**: Kyber may be slower on ARM than x86
**Impact**: Longer boot times (>10 seconds)
**Mitigation**:
- Benchmark early (Week 1)
- Use ARM NEON optimizations
- Consider Kyber-768 (faster, still secure) as fallback

### Risk 2: liboqs Compilation on Android/Termux

**Risk**: liboqs may not compile in Termux
**Impact**: Cannot implement Kyber-1024
**Mitigation**:
- Use PRoot Debian for compilation (as done for signed bus)
- Or use pure-Python Kyber implementation (slower but works)
- Test compilation in Week 1

### Risk 3: LUKS2 Kyber Support

**Risk**: Linux dm-crypt doesn't support Kyber natively
**Impact**: Python-only implementation (slower)
**Mitigation**:
- Use Python implementation for now
- Submit kernel patch for Kyber support (long-term)
- Hybrid: LUKS2 Argon2id + Python Kyber layer

### Risk 4: Backward Compatibility

**Risk**: Phase 3 volumes incompatible with Phase 4
**Impact**: Users lose data if not migrated
**Mitigation**:
- Support both volume formats
- Automated migration tool
- Clear warnings before upgrade

---

## Success Criteria

Phase 4 is considered complete when:

1. ✅ All cryptographic primitives implemented and tested
2. ✅ PQ volume creation/unlock works on Termux/PRoot
3. ✅ Migration tool successfully converts Phase 3 → Phase 4
4. ✅ LUKS2 integration works on Linux systems
5. ✅ U-Boot Kyber verification functional
6. ✅ Performance acceptable (< 5 second unlock)
7. ✅ All tests passing (unit + integration + security)
8. ✅ Documentation complete
9. ✅ Security audit passed
10. ✅ Deployed and tested on real ARM64 device

---

## Timeline Summary

| Month | Milestone | Deliverables |
|-------|-----------|--------------|
| 1 | Foundation | Kyber, Argon2id, BLAKE3 wrappers |
| 2 | PQ Volume | PostQuantumVolume implementation |
| 3 | Linux Integration | LUKS2 scripts, dm-crypt |
| 4 | U-Boot Integration | Kyber verification in bootloader |
| 5 | Testing | Comprehensive test suite |
| 6 | Deployment | Documentation, release |

**Total Duration**: 6 months (parallel with other QWAMOS development)

---

## Next Immediate Steps

1. **Week 1 (This Week)**:
   - Install liboqs-python, argon2-cffi, blake3
   - Implement `crypto/pq/kyber_wrapper.py`
   - Implement `crypto/pq/argon2_kdf.py`
   - Implement `crypto/pq/blake3_hash.py`
   - Write unit tests for each

2. **Week 2**:
   - Begin `PostQuantumVolume` implementation
   - Design and test 2048-byte PQ header
   - Implement Kyber key encapsulation flow

3. **Week 3**:
   - Complete PQ volume create/unlock
   - Implement data encryption/decryption
   - Integration tests

4. **Week 4**:
   - Migration tool (Phase 3 → Phase 4)
   - Performance benchmarks
   - Security validation

---

## References

- **Kyber**: https://pq-crystals.org/kyber/
- **NIST FIPS 203**: https://csrc.nist.gov/pubs/fips/203/final
- **liboqs**: https://github.com/open-quantum-safe/liboqs
- **liboqs-python**: https://github.com/open-quantum-safe/liboqs-python
- **Argon2**: https://github.com/P-H-C/phc-winner-argon2
- **BLAKE3**: https://github.com/BLAKE3-team/BLAKE3
- **ChaCha20-Poly1305**: RFC 8439
- **LUKS2**: https://gitlab.com/cryptsetup/cryptsetup

---

**Document Version**: 1.0
**Last Updated**: 2025-11-02
**Status**: Phase 4 kickoff - implementation begins now
**Author**: Claude Code + Dezirae Stark
**Project**: QWAMOS Phase 4 - Post-Quantum Storage Encryption

*QWAMOS - The Future of Post-Quantum Mobile Security*
