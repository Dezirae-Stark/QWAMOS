# Kyber-1024 Key Wrapping Implementation Plan

## Overview

This document outlines the implementation of Kyber-1024 Key Encapsulation Mechanism (KEM) for wrapping ChaCha20 symmetric keys used in QWAMOS encrypted storage.

## Key Wrapping vs Key Encapsulation

### Traditional Key Wrapping (e.g., AES-KWP)
1. Generate symmetric data encryption key (DEK)
2. Encrypt DEK with another symmetric key (KEK)
3. Store wrapped DEK

**Problem**: KEK must be stored somewhere, vulnerable to quantum attacks

### Kyber KEM Approach
1. Generate Kyber-1024 key pair (public/secret)
2. Store secret key in secure hardware (StrongBox)
3. Use public key to encapsulate random shared secret
4. Derive ChaCha20 key from shared secret
5. Store Kyber ciphertext in volume header

**Advantage**: Secret key never leaves secure hardware, public key operations quantum-safe

## Kyber-1024 Workflow

### Key Generation (One-Time Setup)

```python
from oqs import KEM

# Generate Kyber-1024 key pair
kem = KEM("Kyber1024")
public_key = kem.generate_keypair()  # 1568 bytes
secret_key = kem.export_secret_key()  # 3168 bytes

# Store secret_key in Android StrongBox
store_in_strongbox("vm_master_secret", secret_key)

# Public key can be stored anywhere (not secret)
save_to_file("vm_public.key", public_key)
```

### Encapsulation (Encrypting New Volume)

```python
# Load public key
public_key = load_from_file("vm_public.key")

# Generate random shared secret
kem = KEM("Kyber1024")
ciphertext, shared_secret = kem.encap_secret(public_key)

# ciphertext: 1568 bytes (store in volume header)
# shared_secret: 32 bytes (ephemeral, used immediately)

# Derive ChaCha20 key from shared secret
from hashlib import blake2b
chacha_key = blake2b(shared_secret, digest_size=32,
                     salt=volume_salt,
                     person=b"QWAMOS_PQC_V1").digest()

# Securely erase shared_secret
memzero(shared_secret)

# Use chacha_key for disk encryption
# Store ciphertext in volume header
```

### Decapsulation (Mounting Existing Volume)

```python
# Load Kyber ciphertext from volume header
ciphertext = read_volume_header()["kyber_ciphertext"]  # 1568 bytes

# Retrieve secret key from StrongBox
secret_key = retrieve_from_strongbox("vm_master_secret")

# Decapsulate to recover shared secret
kem = KEM("Kyber1024")
shared_secret = kem.decap_secret(ciphertext, secret_key)

# Derive same ChaCha20 key
chacha_key = blake2b(shared_secret, digest_size=32,
                     salt=volume_salt,
                     person=b"QWAMOS_PQC_V1").digest()

# Securely erase shared_secret
memzero(shared_secret)

# Use chacha_key to decrypt disk
```

## Security Properties

### Quantum Resistance

**Kyber-1024 Security Level**: NIST Level 5
- Classical bit security: ≥230 bits
- Quantum bit security: ≥233 bits
- Resistant to Shor's algorithm (doesn't apply to lattice problems)
- Resistant to Grover's algorithm (affects symmetric crypto only)

**Attack Scenarios**:
1. **Adversary captures ciphertext**: Cannot derive shared secret without secret key
2. **Adversary steals public key**: Expected, public key is not secret
3. **Adversary performs quantum attack**: Kyber lattice problem remains hard

### Forward Secrecy

**Key Rotation Strategy**:

```
Time T0: Generate Kyber key pair (SK1, PK1)
         Encapsulate → Ciphertext1 → ChaCha Key1
         Encrypt data with Key1

Time T1: Generate new Kyber key pair (SK2, PK2)
         Re-encapsulate → Ciphertext2 → ChaCha Key2
         Re-encrypt data with Key2
         Securely delete SK1, Key1, Ciphertext1

Result: Data encrypted at T0 cannot be decrypted at T1+
        Even if SK2 is compromised, old data remains safe
```

**Rotation Frequency**: Every 90 days (recommended)

## Implementation Details

### Library Selection

**Option 1: liboqs (Open Quantum Safe)**

```c
#include <oqs/oqs.h>

OQS_KEM *kem = OQS_KEM_new("Kyber1024");
uint8_t public_key[OQS_KEM_kyber_1024_length_public_key];
uint8_t secret_key[OQS_KEM_kyber_1024_length_secret_key];

OQS_KEM_keypair(kem, public_key, secret_key);

// Encapsulation
uint8_t ciphertext[OQS_KEM_kyber_1024_length_ciphertext];
uint8_t shared_secret[OQS_KEM_kyber_1024_length_shared_secret];
OQS_KEM_encaps(kem, ciphertext, shared_secret, public_key);

// Decapsulation
OQS_KEM_decaps(kem, shared_secret, ciphertext, secret_key);

OQS_KEM_free(kem);
```

**Option 2: Reference Implementation (C/Python)**

More control, but requires manual integration and testing.

**Recommendation**: Use liboqs for production (well-tested, optimized)

### Android StrongBox Integration

```kotlin
// Android KeyStore API
val keyStore = KeyStore.getInstance("AndroidKeyStore")
keyStore.load(null)

// Generate AES key in StrongBox (for wrapping Kyber secret)
val keyGenerator = KeyGenerator.getInstance(
    KeyProperties.KEY_ALGORITHM_AES,
    "AndroidKeyStore"
)

val builder = KeyGenParameterSpec.Builder(
    "kyber_secret_wrapper",
    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
)
    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
    .setKeySize(256)
    .setIsStrongBoxBacked(true)  // Use secure element

keyGenerator.init(builder.build())
val wrapperKey = keyGenerator.generateKey()

// Wrap Kyber secret key with StrongBox AES key
val cipher = Cipher.getInstance("AES/GCM/NoPadding")
cipher.init(Cipher.ENCRYPT_MODE, wrapperKey)
val wrappedKyberSecret = cipher.doFinal(kyberSecretKey)

// Store wrapped key in persistent storage
```

**Why AES wrapper?**: StrongBox doesn't natively support Kyber, so we wrap Kyber secret with AES (hardware-protected)

### Performance Optimization

**Pre-Compute Public Key Operations**:

```python
# Cache encapsulation results for read-only VMs
cache = {}

def get_or_create_wrapped_key(vm_name):
    if vm_name in cache:
        return cache[vm_name]

    ciphertext, shared_secret = kem.encap_secret(public_key)
    cache[vm_name] = (ciphertext, shared_secret)
    return cache[vm_name]
```

**Lazy Decapsulation**: Only decapsulate when VM is actually accessed

**Batch Key Derivation**: Derive keys for all VMs at boot, cache in RAM

## Error Handling

### Corrupted Ciphertext

```python
try:
    shared_secret = kem.decap_secret(ciphertext, secret_key)
except DecapsulationError:
    # Ciphertext corrupted or tampered
    log.error("Kyber decapsulation failed - volume header corrupted")

    # Attempt recovery from backup header
    ciphertext_backup = read_backup_header()["kyber_ciphertext"]
    shared_secret = kem.decap_secret(ciphertext_backup, secret_key)
```

### Secret Key Loss

If secret key is lost (StrongBox reset, device wipe):
1. **Prevention**: Backup wrapped secret key encrypted with user password
2. **Recovery**: Restore from backup using password
3. **Last Resort**: Volume is unrecoverable (by design)

**User Warning**: "Losing your device password means permanent data loss"

## Testing

### Unit Tests

```python
def test_kyber_keywrap():
    # Generate key pair
    kem = KEM("Kyber1024")
    pk = kem.generate_keypair()
    sk = kem.export_secret_key()

    # Encapsulate
    ct, ss1 = kem.encap_secret(pk)

    # Decapsulate
    ss2 = kem.decap_secret(ct, sk)

    # Shared secrets must match
    assert ss1 == ss2

    # Derive keys
    key1 = blake2b(ss1, digest_size=32).digest()
    key2 = blake2b(ss2, digest_size=32).digest()

    assert key1 == key2
```

### Integration Tests

1. **Volume Creation**: Create volume, encapsulate key, write data
2. **Volume Mounting**: Decapsulate key, read data, verify integrity
3. **Key Rotation**: Re-encapsulate with new key, re-encrypt data
4. **Corruption Recovery**: Corrupt ciphertext, test backup recovery

### NIST KAT Validation

Run Kyber-1024 Known Answer Tests to verify correctness:

```bash
# Download NIST KAT files
wget https://pq-crystals.org/kyber/data/kyber-1024-kat.rsp

# Run validation
./validate_kyber_kat kyber-1024-kat.rsp
```

## Migration Plan

### Phase 1: Parallel Deployment (Weeks 1-2)
- Implement Kyber key wrapping alongside existing AES-based encryption
- Both schemes coexist, user can choose

### Phase 2: Testing (Weeks 3-4)
- Create test VMs with Kyber-wrapped keys
- Benchmark performance
- Security audit

### Phase 3: Migration (Weeks 5-6)
- Automated migration tool to convert AES → Kyber
- Prompt users to migrate existing VMs
- Gradual rollout

### Phase 4: Deprecation (Weeks 7-8)
- Announce AES encryption deprecation timeline
- Require Kyber for new VMs
- Maintain AES support for legacy volumes (read-only)

## References

- [Kyber NIST Submission](https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf)
- [liboqs Documentation](https://github.com/open-quantum-safe/liboqs)
- [BLAKE2 Specification](https://tools.ietf.org/html/rfc7693)
- [Android KeyStore](https://developer.android.com/training/articles/keystore)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
**Author:** QWAMOS Cryptography Team
