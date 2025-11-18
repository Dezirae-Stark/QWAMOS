# Phase XIII: Post-Quantum Storage Subsystem

## Overview

Phase XIII implements a complete post-quantum cryptography (PQC) storage subsystem using Kyber-1024 for key encapsulation and ChaCha20-Poly1305 for authenticated encryption. All VM disk images, configuration files, and user data will be encrypted with quantum-resistant algorithms, ensuring long-term confidentiality even against future quantum computer attacks.

## Goals

1. **Full PQC Encryption**: Replace all classical crypto (AES) with post-quantum alternatives
2. **Kyber-Wrapped Keys**: Use Kyber-1024 KEM to protect ChaCha20 symmetric keys
3. **Per-VM Isolation**: Each VM has independent encryption keys (defense in depth)
4. **Transparent Operation**: Encryption/decryption handled automatically by storage layer
5. **Performance**: Maintain <10% overhead compared to unencrypted storage

## Planned Design

### Architecture Components

**PQC Key Management**
- Kyber-1024 key pairs for each VM and user vault
- Hierarchical key derivation from master seed
- Secure key storage in Android StrongBox/TEE
- Key rotation mechanism for forward secrecy

**Encrypted Filesystem Layer**
- dm-crypt integration with custom cipher chain
- ChaCha20-Poly1305 for bulk encryption (AEAD)
- BLAKE3 for integrity verification
- Virtual block device layer (transparent to upper layers)

**Storage Backend**
- LUKS2-like container format (custom implementation)
- Sparse file support for efficient space usage
- Snapshot capability for VM backups
- Compression (optional): zstd before encryption

### Encryption Flow

```
[User Data]
   ↓
[BLAKE3 Hash] → Integrity Tag
   ↓
[ChaCha20-Poly1305 Encrypt] ← Symmetric Key (256-bit)
   ↓                                ↑
[Encrypted Data]                    |
   ↓                      [Kyber-1024 KEM Encapsulate]
[Write to Disk]                     ↑
                          [Public Key from StrongBox]
```

### Security Properties

- **Quantum Resistance**: Kyber-1024 provides ~AES-256 equivalent security against quantum attacks
- **Authenticated Encryption**: ChaCha20-Poly1305 prevents tampering
- **Key Isolation**: Compromise of one VM key doesn't affect others
- **Forward Secrecy**: Old encrypted data unrecoverable after key rotation

## Dependencies

### Cryptographic Libraries
- **liboqs** (Open Quantum Safe): Kyber-1024 implementation
- **libsodium**: ChaCha20-Poly1305 and BLAKE3
- **OpenSSL 3.0+**: For compatibility and TLS integration

### Kernel Requirements
- Device Mapper (dm-crypt or custom dm-pqcrypt module)
- Cryptographic API framework
- Block device layer hooks

### Phase Dependencies
- Phase 4 (Post-Quantum Crypto) for liboqs integration
- Phase 3 (Hypervisor) for VM storage backend
- Phase 2 (Kernel) for dm-crypt kernel module

## Implementation Steps

### Step 1: Custom dm-pqcrypt Kernel Module
1. Fork dm-crypt source code
2. Replace AES with ChaCha20-Poly1305 cipher
3. Add Kyber-1024 key unwrapping support
4. Implement BLAKE3 integrity verification
5. Test with cryptsetup-like tool

### Step 2: Key Management Service
1. Generate Kyber-1024 key pairs in StrongBox
2. Implement key derivation hierarchy (master → VM keys)
3. Create key rotation API
4. Secure key zeroization on VM destruction

### Step 3: Encrypted Volume Creation
1. Implement `pqcrypt_create_volume(name, size)` API
2. Format volume with metadata header
3. Store Kyber-encapsulated symmetric key in header
4. Mount volume as block device

### Step 4: VM Integration
1. Update hypervisor to create PQC volumes for each VM
2. Migrate existing VM images to encrypted volumes
3. Implement snapshot functionality
4. Test VM boot from encrypted storage

### Step 5: Performance Optimization
1. Enable hardware acceleration (ARM Crypto Extensions)
2. Implement read-ahead and write-behind caching
3. Optimize Kyber operations (pre-computation)
4. Benchmark I/O throughput

### Step 6: Key Recovery and Backup
1. Implement secure key export (encrypted with user password)
2. Create backup/restore mechanism
3. Emergency key recovery (split key across multiple factors)
4. Test disaster recovery scenarios

## Testing Strategy

### Unit Tests
- Kyber-1024 key generation and encapsulation
- ChaCha20-Poly1305 encryption/decryption
- BLAKE3 integrity verification
- Key derivation functions

### Integration Tests
- Create encrypted volume and mount it
- Write data, unmount, remount, verify data
- Multiple VMs with independent encrypted volumes
- Snapshot creation and restoration

### Performance Tests
- **Throughput**: Sequential read/write (target: ≥400 MB/s)
- **IOPS**: Random 4K read/write (target: ≥10,000 IOPS)
- **Latency**: Average read latency (target: <5ms)
- **CPU Overhead**: Encryption CPU usage (target: <15%)

### Security Tests
- Key isolation (VM1 cannot read VM2's encrypted data)
- Integrity verification (detect tampered encrypted data)
- Quantum attack simulation (Grover's algorithm resistance)
- Side-channel resistance (timing attacks)

### Compatibility Tests
- Migration from existing unencrypted VMs
- Backward compatibility with Phase 4 crypto
- Export/import encrypted volumes
- Cross-device restore (same keys, different device)

## Future Extensions

1. **Hardware Crypto Offload**: Use Snapdragon Crypto Engine for ChaCha20
2. **Compression**: Transparent zstd compression before encryption
3. **Deduplication**: Block-level dedup with encrypted hashes
4. **Cloud Backup**: PQC-encrypted backups to remote storage
5. **Multi-User Access**: Shared volumes with per-user Kyber key wrapping

---

**Status:** Planning - 0% Complete
**Estimated Effort:** 10-14 weeks
**Priority:** Critical (quantum threat timeline: 10-15 years)
**Dependencies:** Phase 4 (liboqs), Phase 3 (hypervisor)

**Last Updated:** 2025-11-17
