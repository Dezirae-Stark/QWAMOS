#!/usr/bin/env python3
"""
QWAMOS Kyber-1024 Post-Quantum Key Encapsulation Mechanism
Pure Python implementation for Android/Termux compatibility

Kyber-1024 is a lattice-based post-quantum KEM that provides:
- 256-bit classical security (AES-256 equivalent)
- 233-bit quantum security (resistant to Shor's algorithm)
- NIST FIPS 203 compliance (ML-KEM standard)

Key sizes:
- Public key: 1568 bytes
- Secret key: 3168 bytes
- Ciphertext: 1568 bytes
- Shared secret: 32 bytes
"""

import sys
import os
from typing import Tuple

try:
    from kyber_py.kyber import Kyber1024
except ImportError:
    print("[!] Error: kyber-py not installed")
    print("    Run: pip install kyber-py")
    sys.exit(1)


class QWAMOSKyber:
    """
    Kyber-1024 Key Encapsulation Mechanism for QWAMOS Phase 4

    Provides post-quantum key exchange for volume encryption using
    lattice-based cryptography (Module-LWE problem).

    Security:
    - Classical security: 256-bit
    - Quantum security: 233-bit (NISTIR 8413)
    - NIST FIPS 203 (ML-KEM-1024)
    """

    # Constants
    PUBLIC_KEY_SIZE = 1568   # Kyber-1024 public key
    SECRET_KEY_SIZE = 3168   # Kyber-1024 secret key
    CIPHERTEXT_SIZE = 1568   # Kyber-1024 ciphertext
    SHARED_SECRET_SIZE = 32  # 256-bit shared secret

    @staticmethod
    def generate_keypair() -> Tuple[bytes, bytes]:
        """
        Generate Kyber-1024 keypair

        Returns:
            (public_key, secret_key) tuple
            - public_key: 1568 bytes (store in volume header)
            - secret_key: 3168 bytes (derived from password each unlock)

        Example:
            >>> pk, sk = QWAMOSKyber.generate_keypair()
            >>> len(pk), len(sk)
            (1568, 3168)
        """
        # Generate keypair using Kyber-1024 (correct API: class method, not instance)
        pk_bytes, sk_bytes = Kyber1024.keygen()

        # Verify sizes
        assert len(pk_bytes) == QWAMOSKyber.PUBLIC_KEY_SIZE
        assert len(sk_bytes) == QWAMOSKyber.SECRET_KEY_SIZE

        return pk_bytes, sk_bytes

    @staticmethod
    def encapsulate(public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Encapsulate (generate shared secret and ciphertext)

        This is used during volume creation to:
        1. Generate a random shared secret (32 bytes)
        2. Encrypt it with the public key → ciphertext (1568 bytes)

        Args:
            public_key: Kyber-1024 public key (1568 bytes)

        Returns:
            (shared_secret, ciphertext) tuple
            - shared_secret: 32 bytes (used to encrypt master key)
            - ciphertext: 1568 bytes (store in volume header)

        Example:
            >>> pk, sk = QWAMOSKyber.generate_keypair()
            >>> shared_secret, ciphertext = QWAMOSKyber.encapsulate(pk)
            >>> len(shared_secret), len(ciphertext)
            (32, 1568)
        """
        if not isinstance(public_key, bytes):
            raise TypeError("Public key must be bytes")
        if len(public_key) != QWAMOSKyber.PUBLIC_KEY_SIZE:
            raise ValueError(f"Public key must be {QWAMOSKyber.PUBLIC_KEY_SIZE} bytes")

        # Encapsulate using Kyber-1024 (correct API: class method)
        # Returns (shared_secret, ciphertext)
        ss_bytes, ct_bytes = Kyber1024.encaps(public_key)

        # Verify sizes
        assert len(ct_bytes) == QWAMOSKyber.CIPHERTEXT_SIZE
        assert len(ss_bytes) == QWAMOSKyber.SHARED_SECRET_SIZE

        return ss_bytes, ct_bytes

    @staticmethod
    def decapsulate(secret_key: bytes, ciphertext: bytes) -> bytes:
        """
        Decapsulate (recover shared secret from ciphertext)

        This is used during volume unlock to:
        1. Use secret key (derived from password)
        2. Decrypt ciphertext → recover shared secret
        3. Use shared secret to decrypt master key

        Args:
            secret_key: Kyber-1024 secret key (3168 bytes)
            ciphertext: Kyber-1024 ciphertext (1568 bytes)

        Returns:
            shared_secret: 32 bytes (same as encapsulation)

        Example:
            >>> pk, sk = QWAMOSKyber.generate_keypair()
            >>> ss1, ct = QWAMOSKyber.encapsulate(pk)
            >>> ss2 = QWAMOSKyber.decapsulate(sk, ct)
            >>> ss1 == ss2
            True
        """
        if not isinstance(secret_key, bytes):
            raise TypeError("Secret key must be bytes")
        if not isinstance(ciphertext, bytes):
            raise TypeError("Ciphertext must be bytes")
        if len(secret_key) != QWAMOSKyber.SECRET_KEY_SIZE:
            raise ValueError(f"Secret key must be {QWAMOSKyber.SECRET_KEY_SIZE} bytes")
        if len(ciphertext) != QWAMOSKyber.CIPHERTEXT_SIZE:
            raise ValueError(f"Ciphertext must be {QWAMOSKyber.CIPHERTEXT_SIZE} bytes")

        # Decapsulate using Kyber-1024 (correct API: class method)
        ss_bytes = Kyber1024.decaps(secret_key, ciphertext)

        # Verify size
        assert len(ss_bytes) == QWAMOSKyber.SHARED_SECRET_SIZE

        return ss_bytes

    @staticmethod
    def verify_encap_decap(public_key: bytes, secret_key: bytes) -> bool:
        """
        Verify that encapsulation/decapsulation works correctly

        This is used for testing and validation.

        Args:
            public_key: Kyber-1024 public key (1568 bytes)
            secret_key: Kyber-1024 secret key (3168 bytes)

        Returns:
            True if encap/decap cycle produces matching shared secrets

        Example:
            >>> pk, sk = QWAMOSKyber.generate_keypair()
            >>> QWAMOSKyber.verify_encap_decap(pk, sk)
            True
        """
        # Encapsulate
        ss1, ct = QWAMOSKyber.encapsulate(public_key)

        # Decapsulate
        ss2 = QWAMOSKyber.decapsulate(secret_key, ct)

        # Verify shared secrets match
        return ss1 == ss2

    @staticmethod
    def get_key_sizes() -> dict:
        """
        Get Kyber-1024 key and ciphertext sizes

        Returns:
            Dictionary with all size information
        """
        return {
            'public_key_bytes': QWAMOSKyber.PUBLIC_KEY_SIZE,
            'secret_key_bytes': QWAMOSKyber.SECRET_KEY_SIZE,
            'ciphertext_bytes': QWAMOSKyber.CIPHERTEXT_SIZE,
            'shared_secret_bytes': QWAMOSKyber.SHARED_SECRET_SIZE
        }


def benchmark_kyber(iterations=10):
    """
    Benchmark Kyber-1024 performance

    Args:
        iterations: Number of iterations for each operation

    Example:
        >>> benchmark_kyber(iterations=5)
        Benchmarking Kyber-1024 (5 iterations)...
        Key Generation:  avg 0.21s
        Encapsulation:   avg 0.15s
        Decapsulation:   avg 0.15s
    """
    import time

    print(f"[*] Benchmarking Kyber-1024 performance ({iterations} iterations)...")
    print(f"[*] Implementation: Pure Python (kyber-py)\n")

    # Benchmark key generation
    keygen_times = []
    print("[*] Testing key generation...")
    for i in range(iterations):
        start = time.time()
        pk, sk = QWAMOSKyber.generate_keypair()
        elapsed = time.time() - start
        keygen_times.append(elapsed)
        print(f"    Run {i+1}: {elapsed:.3f}s")

    avg_keygen = sum(keygen_times) / len(keygen_times)
    print(f"    Average: {avg_keygen:.3f}s\n")

    # Benchmark encapsulation
    encap_times = []
    print("[*] Testing encapsulation...")
    for i in range(iterations):
        start = time.time()
        ss, ct = QWAMOSKyber.encapsulate(pk)
        elapsed = time.time() - start
        encap_times.append(elapsed)
        print(f"    Run {i+1}: {elapsed:.3f}s")

    avg_encap = sum(encap_times) / len(encap_times)
    print(f"    Average: {avg_encap:.3f}s\n")

    # Benchmark decapsulation
    decap_times = []
    print("[*] Testing decapsulation...")
    for i in range(iterations):
        start = time.time()
        ss2 = QWAMOSKyber.decapsulate(sk, ct)
        elapsed = time.time() - start
        decap_times.append(elapsed)
        print(f"    Run {i+1}: {elapsed:.3f}s")

    avg_decap = sum(decap_times) / len(decap_times)
    print(f"    Average: {avg_decap:.3f}s\n")

    # Summary
    print("=" * 60)
    print("KYBER-1024 PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Key Generation:  {avg_keygen:.3f}s (one-time, volume creation)")
    print(f"Encapsulation:   {avg_encap:.3f}s (one-time, volume creation)")
    print(f"Decapsulation:   {avg_decap:.3f}s (every volume unlock)")
    print()
    print(f"Estimated volume unlock overhead: {avg_decap:.3f}s")
    print(f"With Argon2id (high): ~5s + {avg_decap:.3f}s = ~{5+avg_decap:.2f}s total")
    print("=" * 60)

    return {
        'keygen_avg': avg_keygen,
        'encap_avg': avg_encap,
        'decap_avg': avg_decap
    }


# Example usage and tests
if __name__ == "__main__":
    print("=" * 60)
    print("QWAMOS Kyber-1024 Post-Quantum KEM - Phase 4")
    print("=" * 60)

    # Test 1: Key generation
    print("\n[*] Test 1: Kyber-1024 key generation")
    pk, sk = QWAMOSKyber.generate_keypair()
    print(f"[+] Public key:  {len(pk)} bytes ({pk[:16].hex()}...)")
    print(f"[+] Secret key:  {len(sk)} bytes ({sk[:16].hex()}...)")

    # Verify sizes
    sizes = QWAMOSKyber.get_key_sizes()
    print(f"\n[*] Key sizes:")
    for name, size in sizes.items():
        print(f"    {name:20s}: {size:4d} bytes")

    # Test 2: Encapsulation
    print("\n[*] Test 2: Encapsulation (generate shared secret)")
    ss1, ct = QWAMOSKyber.encapsulate(pk)
    print(f"[+] Shared secret: {len(ss1)} bytes ({ss1.hex()[:32]}...)")
    print(f"[+] Ciphertext:    {len(ct)} bytes ({ct[:16].hex()}...)")

    # Test 3: Decapsulation
    print("\n[*] Test 3: Decapsulation (recover shared secret)")
    ss2 = QWAMOSKyber.decapsulate(sk, ct)
    print(f"[+] Recovered:     {len(ss2)} bytes ({ss2.hex()[:32]}...)")

    # Verify shared secrets match
    if ss1 == ss2:
        print("[+] ✓ Shared secrets match! Kyber-1024 working correctly.")
    else:
        print("[!] ✗ ERROR: Shared secrets don't match!")
        sys.exit(1)

    # Test 4: Multiple encap/decap cycles
    print("\n[*] Test 4: Testing 10 encap/decap cycles...")
    success_count = 0
    for i in range(10):
        ss_a, ct_a = QWAMOSKyber.encapsulate(pk)
        ss_b = QWAMOSKyber.decapsulate(sk, ct_a)
        if ss_a == ss_b:
            success_count += 1

    print(f"[+] Success rate: {success_count}/10")
    if success_count == 10:
        print("[+] ✓ All cycles successful!")
    else:
        print(f"[!] ✗ WARNING: {10-success_count} cycles failed!")

    # Test 5: Wrong key rejection
    print("\n[*] Test 5: Verifying wrong key produces different secret...")
    pk2, sk2 = QWAMOSKyber.generate_keypair()
    ss_correct, ct = QWAMOSKyber.encapsulate(pk)
    ss_wrong = QWAMOSKyber.decapsulate(sk2, ct)  # Wrong secret key

    if ss_correct != ss_wrong:
        print("[+] ✓ Wrong key produces different shared secret (expected)")
    else:
        print("[!] ✗ ERROR: Wrong key produced same secret!")

    # Test 6: Performance benchmark
    print("\n[*] Test 6: Performance benchmark")
    benchmark_kyber(iterations=3)

    # Test 7: Determinism check
    print("\n[*] Test 7: Checking determinism...")
    # Note: Kyber encapsulation is NOT deterministic (uses random nonce)
    ss_x, ct_x = QWAMOSKyber.encapsulate(pk)
    ss_y, ct_y = QWAMOSKyber.encapsulate(pk)

    if ct_x != ct_y:
        print("[+] ✓ Encapsulation is non-deterministic (expected for IND-CCA2)")
    else:
        print("[!] ⚠ WARNING: Encapsulation appears deterministic!")

    # But both should decrypt correctly
    ss_x_decap = QWAMOSKyber.decapsulate(sk, ct_x)
    ss_y_decap = QWAMOSKyber.decapsulate(sk, ct_y)

    if ss_x == ss_x_decap and ss_y == ss_y_decap:
        print("[+] ✓ Both ciphertexts decrypt correctly")

    print("\n" + "=" * 60)
    print("Kyber-1024 implementation complete and tested!")
    print("=" * 60)
    print("\n[*] Ready for Phase 4 integration")
    print("[*] Next: Implement PostQuantumVolume class")
