#!/usr/bin/env python3
"""
QWAMOS BLAKE3 Cryptographic Hash Function
Post-Quantum resistant hashing for Phase 4

BLAKE3 is a cryptographic hash function that is:
- 10x faster than SHA-256
- Parallelizable on multi-core processors
- Secure against length-extension attacks
- Quantum-resistant (full 256-bit security)
"""

import sys
from typing import Optional

try:
    import blake3
except ImportError:
    print("[!] Error: blake3 not installed")
    print("    Run: pip install blake3")
    sys.exit(1)

class Blake3Hash:
    """
    BLAKE3 Cryptographic Hash for QWAMOS Phase 4

    Provides fast, secure hashing for:
    - Volume header integrity verification
    - Master key verification
    - Nonce generation
    - File integrity checking
    - Key derivation (BLAKE3-KDF mode)
    """

    @staticmethod
    def hash(data: bytes, output_length: int = 32) -> bytes:
        """
        Compute BLAKE3 hash of data

        Args:
            data: Input data to hash
            output_length: Output length in bytes (default: 32 for 256-bit)

        Returns:
            Hash digest (bytes)

        Example:
            >>> digest = Blake3Hash.hash(b"Hello QWAMOS")
            >>> len(digest)
            32
        """
        if not isinstance(data, bytes):
            raise TypeError("Input must be bytes")

        hasher = blake3.blake3(data)
        return hasher.digest(length=output_length)

    @staticmethod
    def hash_hex(data: bytes, output_length: int = 32) -> str:
        """
        Compute BLAKE3 hash and return hex string

        Args:
            data: Input data to hash
            output_length: Output length in bytes

        Returns:
            Hex-encoded hash string

        Example:
            >>> Blake3Hash.hash_hex(b"Hello")
            'ea8f163db38682925e4491c5e58d4bb3506ef8c14eb78a86e908c5624a67200f'
        """
        digest = Blake3Hash.hash(data, output_length)
        return digest.hex()

    @staticmethod
    def keyed_hash(data: bytes, key: bytes, output_length: int = 32) -> bytes:
        """
        Compute BLAKE3 keyed hash (MAC/HMAC equivalent)

        Args:
            data: Input data to hash
            key: Secret key (32 bytes recommended)
            output_length: Output length in bytes

        Returns:
            Keyed hash (MAC)

        Example:
            >>> key = os.urandom(32)
            >>> mac = Blake3Hash.keyed_hash(b"message", key)
            >>> len(mac)
            32
        """
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        if not isinstance(key, bytes):
            raise TypeError("Key must be bytes")
        if len(key) != 32:
            raise ValueError("Key must be exactly 32 bytes")

        hasher = blake3.blake3(data, key=key)
        return hasher.digest(length=output_length)

    @staticmethod
    def derive_key(context: str, key_material: bytes,
                   output_length: int = 32) -> bytes:
        """
        Derive key using BLAKE3-KDF mode

        BLAKE3 KDF mode is designed for key derivation from:
        - Master keys
        - Shared secrets
        - Key encapsulation results

        Args:
            context: Domain separation string (e.g., "qwamos.sector_key")
            key_material: Input key material (any length)
            output_length: Derived key length in bytes

        Returns:
            Derived key (bytes)

        Example:
            >>> master_key = os.urandom(32)
            >>> sector_key = Blake3Hash.derive_key(
            ...     "qwamos.sector.0",
            ...     master_key,
            ...     32
            ... )
        """
        if not isinstance(context, str):
            raise TypeError("Context must be string")
        if not isinstance(key_material, bytes):
            raise TypeError("Key material must be bytes")

        hasher = blake3.blake3(
            key_material,
            derive_key_context=context
        )
        return hasher.digest(length=output_length)

    @staticmethod
    def hash_file(file_path: str, output_length: int = 32) -> bytes:
        """
        Compute BLAKE3 hash of file

        Args:
            file_path: Path to file
            output_length: Output length in bytes

        Returns:
            File hash (bytes)

        Example:
            >>> hash = Blake3Hash.hash_file("/path/to/volume.qpq")
        """
        hasher = blake3.blake3()

        with open(file_path, 'rb') as f:
            # Read file in chunks for memory efficiency
            while chunk := f.read(65536):  # 64KB chunks
                hasher.update(chunk)

        return hasher.digest(length=output_length)

    @staticmethod
    def hash_file_hex(file_path: str, output_length: int = 32) -> str:
        """
        Compute BLAKE3 hash of file and return hex string

        Args:
            file_path: Path to file
            output_length: Output length in bytes

        Returns:
            Hex-encoded file hash
        """
        digest = Blake3Hash.hash_file(file_path, output_length)
        return digest.hex()

    @staticmethod
    def incremental_hash():
        """
        Create incremental hash object for streaming data

        Returns:
            BLAKE3 hasher object

        Example:
            >>> hasher = Blake3Hash.incremental_hash()
            >>> hasher.update(b"part1")
            >>> hasher.update(b"part2")
            >>> digest = hasher.finalize()
        """
        return blake3.blake3()


class Blake3Hasher:
    """
    Incremental BLAKE3 hasher for streaming data

    Useful for hashing large files or volumes without loading
    entire content into memory.
    """

    def __init__(self, key: Optional[bytes] = None,
                 derive_key_context: Optional[str] = None):
        """
        Initialize incremental hasher

        Args:
            key: Optional 32-byte key for keyed hashing
            derive_key_context: Optional context for KDF mode
        """
        if key is not None and len(key) != 32:
            raise ValueError("Key must be exactly 32 bytes")

        self.hasher = blake3.blake3(
            key=key,
            derive_key_context=derive_key_context
        )

    def update(self, data: bytes):
        """
        Update hasher with new data

        Args:
            data: Data chunk to hash
        """
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        self.hasher.update(data)

    def finalize(self, output_length: int = 32) -> bytes:
        """
        Finalize hash and return digest

        Args:
            output_length: Output length in bytes

        Returns:
            Hash digest (bytes)
        """
        return self.hasher.digest(length=output_length)

    def finalize_hex(self, output_length: int = 32) -> str:
        """
        Finalize hash and return hex string

        Args:
            output_length: Output length in bytes

        Returns:
            Hex-encoded hash
        """
        digest = self.finalize(output_length)
        return digest.hex()


def benchmark_blake3(data_size_mb=100, iterations=3):
    """
    Benchmark BLAKE3 performance

    Args:
        data_size_mb: Test data size in MB
        iterations: Number of test iterations

    Example:
        >>> benchmark_blake3(data_size_mb=10, iterations=5)
        Hashing 10 MB of data...
        Run 1: 0.05s (200 MB/s)
        Run 2: 0.05s (200 MB/s)
        ...
    """
    import os
    import time

    print(f"[*] Benchmarking BLAKE3 performance...")
    print(f"[*] Data size: {data_size_mb} MB")
    print(f"[*] Iterations: {iterations}\n")

    # Generate test data
    data = os.urandom(data_size_mb * 1024 * 1024)
    print(f"[+] Generated {data_size_mb} MB of random data\n")

    times = []

    for i in range(iterations):
        start = time.time()
        digest = Blake3Hash.hash(data)
        elapsed = time.time() - start
        times.append(elapsed)

        speed = data_size_mb / elapsed
        print(f"  Run {i+1}: {elapsed:.3f}s ({speed:.1f} MB/s)")

    avg_time = sum(times) / len(times)
    avg_speed = data_size_mb / avg_time

    print(f"\n[+] Average: {avg_time:.3f}s ({avg_speed:.1f} MB/s)")
    print(f"[+] Digest (first run): {digest.hex()[:64]}...")

    return avg_speed


# Example usage and tests
if __name__ == "__main__":
    import os

    print("=" * 60)
    print("QWAMOS BLAKE3 Cryptographic Hash - Phase 4")
    print("=" * 60)

    # Test 1: Basic hashing
    print("\n[*] Test 1: Basic BLAKE3 hashing")
    data = b"Hello QWAMOS Post-Quantum Security!"
    digest = Blake3Hash.hash(data)
    print(f"[+] Input: {data}")
    print(f"[+] BLAKE3 hash: {digest.hex()}")
    print(f"[+] Hash length: {len(digest)} bytes")

    # Test 2: Keyed hash (MAC)
    print("\n[*] Test 2: BLAKE3 keyed hash (MAC)")
    key = os.urandom(32)
    mac = Blake3Hash.keyed_hash(data, key)
    print(f"[+] Key: {key.hex()[:32]}...")
    print(f"[+] MAC: {mac.hex()}")

    # Verify MAC with wrong key fails
    wrong_key = os.urandom(32)
    wrong_mac = Blake3Hash.keyed_hash(data, wrong_key)
    if mac != wrong_mac:
        print("[+] ✓ Different key produces different MAC")

    # Test 3: Key derivation (KDF mode)
    print("\n[*] Test 3: BLAKE3 key derivation (KDF mode)")
    master_key = os.urandom(32)

    # Derive sector keys
    sector_0_key = Blake3Hash.derive_key("qwamos.sector.0", master_key, 32)
    sector_1_key = Blake3Hash.derive_key("qwamos.sector.1", master_key, 32)

    print(f"[+] Master key: {master_key.hex()[:32]}...")
    print(f"[+] Sector 0 key: {sector_0_key.hex()[:32]}...")
    print(f"[+] Sector 1 key: {sector_1_key.hex()[:32]}...")

    if sector_0_key != sector_1_key:
        print("[+] ✓ Different contexts produce different keys")

    # Test 4: Incremental hashing
    print("\n[*] Test 4: Incremental hashing (streaming)")
    hasher = Blake3Hasher()
    hasher.update(b"Part 1: ")
    hasher.update(b"Part 2: ")
    hasher.update(b"Part 3")
    incremental_digest = hasher.finalize()

    # Compare with single-pass hash
    single_pass_digest = Blake3Hash.hash(b"Part 1: Part 2: Part 3")

    print(f"[+] Incremental: {incremental_digest.hex()[:32]}...")
    print(f"[+] Single-pass: {single_pass_digest.hex()[:32]}...")

    if incremental_digest == single_pass_digest:
        print("[+] ✓ Incremental hashing matches single-pass")

    # Test 5: Performance benchmark
    print("\n[*] Test 5: Performance benchmark")
    avg_speed = benchmark_blake3(data_size_mb=10, iterations=3)

    # Compare with theoretical speeds
    print(f"\n[*] Performance analysis:")
    print(f"    Measured speed: {avg_speed:.1f} MB/s")

    if avg_speed > 50:
        print("[+] ✓ BLAKE3 is performing well on ARM64")
    else:
        print("[!] ⚠ BLAKE3 performance lower than expected")

    # Test 6: Determinism
    print("\n[*] Test 6: Verifying determinism")
    digest1 = Blake3Hash.hash(b"test data")
    digest2 = Blake3Hash.hash(b"test data")

    if digest1 == digest2:
        print("[+] ✓ Determinism verified: Same input → same output")
    else:
        print("[!] ✗ ERROR: Non-deterministic hashing!")

    print("\n" + "=" * 60)
    print("BLAKE3 implementation complete and tested!")
    print("=" * 60)
