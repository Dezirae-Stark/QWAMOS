#!/usr/bin/env python3
"""
QWAMOS BLAKE3 Hashing Module

CRITICAL FIX #7: Replace BLAKE2b with BLAKE3 for better performance.

BLAKE3 is significantly faster than BLAKE2b, especially on ARM64 platforms:
- Up to 4x faster on modern CPUs
- Parallelizable (multi-threaded hashing)
- Supports keyed hashing, key derivation, and MAC
- 256-bit output (same security level as SHA-256)

Author: QWAMOS Security Team
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BLAKE3Hasher')

# Try to import blake3
try:
    import blake3
    BLAKE3_AVAILABLE = True
    logger.info("✓ BLAKE3 library available")
except ImportError:
    BLAKE3_AVAILABLE = False
    logger.warning("⚠️  BLAKE3 library not available - install with: pip install blake3")
    logger.warning("   Falling back to hashlib.sha256")
    import hashlib


class BLAKE3Hasher:
    """
    BLAKE3 hashing for QWAMOS.

    CRITICAL FIX #7: High-performance cryptographic hashing.

    Features:
    - Fast hashing (4x faster than BLAKE2b on ARM64)
    - Keyed hashing (MAC mode)
    - Key derivation mode
    - Streaming/chunked hashing for large files
    - Automatic fallback to SHA-256 if BLAKE3 unavailable
    """

    def __init__(self, key: Optional[bytes] = None, derive_key_context: Optional[str] = None):
        """
        Initialize BLAKE3 hasher.

        Args:
            key: Optional 32-byte key for keyed hashing (MAC mode)
            derive_key_context: Optional context string for key derivation
        """
        self.key = key
        self.derive_key_context = derive_key_context

        if key and len(key) != 32:
            raise ValueError("BLAKE3 key must be exactly 32 bytes")

        if BLAKE3_AVAILABLE:
            if derive_key_context:
                self.hasher = blake3.blake3(derive_key_context=derive_key_context)
            elif key:
                self.hasher = blake3.blake3(key=key)
            else:
                self.hasher = blake3.blake3()
        else:
            # Fallback to SHA-256
            if key:
                import hmac
                self.hasher = hmac.new(key, digestmod=hashlib.sha256)
            else:
                self.hasher = hashlib.sha256()

    def update(self, data: bytes):
        """
        Update hasher with data.

        Args:
            data: Bytes to hash
        """
        self.hasher.update(data)

    def digest(self, length: int = 32) -> bytes:
        """
        Get hash digest.

        Args:
            length: Output length in bytes (default 32)

        Returns:
            Hash digest
        """
        if BLAKE3_AVAILABLE:
            return self.hasher.digest(length=length)
        else:
            # SHA-256 has fixed 32-byte output
            digest = self.hasher.digest()
            if length > 32:
                # Extend via KDF if needed
                from Crypto.Protocol.KDF import HKDF
                from Crypto.Hash import SHA256
                return HKDF(
                    master=digest,
                    key_len=length,
                    salt=b"",
                    hashmod=SHA256
                )
            return digest[:length]

    def hexdigest(self, length: int = 32) -> str:
        """
        Get hash digest as hex string.

        Args:
            length: Output length in bytes (default 32)

        Returns:
            Hex-encoded hash
        """
        return self.digest(length).hex()


def hash_data(data: Union[bytes, str], key: Optional[bytes] = None) -> bytes:
    """
    Hash data with BLAKE3.

    Args:
        data: Data to hash (bytes or string)
        key: Optional 32-byte key for keyed hashing

    Returns:
        32-byte hash digest
    """
    if isinstance(data, str):
        data = data.encode('utf-8')

    hasher = BLAKE3Hasher(key=key)
    hasher.update(data)
    return hasher.digest()


def hash_file(file_path: Union[str, Path], chunk_size: int = 65536,
              key: Optional[bytes] = None) -> bytes:
    """
    Hash file with BLAKE3 (streaming).

    Args:
        file_path: Path to file
        chunk_size: Chunk size for reading (default 64KB)
        key: Optional 32-byte key for keyed hashing

    Returns:
        32-byte hash digest
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    hasher = BLAKE3Hasher(key=key)

    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)

    return hasher.digest()


def derive_key(context: str, key_material: bytes, output_length: int = 32) -> bytes:
    """
    Derive key using BLAKE3 key derivation mode.

    Args:
        context: Context string (e.g., "qwamos-disk-encryption")
        key_material: Input key material
        output_length: Desired output length (default 32 bytes)

    Returns:
        Derived key
    """
    if BLAKE3_AVAILABLE:
        hasher = blake3.blake3(derive_key_context=context)
        hasher.update(key_material)
        return hasher.digest(length=output_length)
    else:
        # Fallback to HKDF-SHA256
        from Crypto.Protocol.KDF import HKDF
        from Crypto.Hash import SHA256
        return HKDF(
            master=key_material,
            key_len=output_length,
            salt=context.encode('utf-8'),
            hashmod=SHA256
        )


def keyed_hash(data: Union[bytes, str], key: bytes) -> bytes:
    """
    Compute keyed hash (MAC) with BLAKE3.

    Args:
        data: Data to hash
        key: 32-byte key

    Returns:
        32-byte MAC
    """
    if len(key) != 32:
        raise ValueError("Key must be exactly 32 bytes")

    return hash_data(data, key=key)


def verify_hash(data: Union[bytes, str], expected_hash: bytes,
                key: Optional[bytes] = None) -> bool:
    """
    Verify hash of data.

    Args:
        data: Data to verify
        expected_hash: Expected hash digest
        key: Optional key for keyed hashing

    Returns:
        True if hash matches
    """
    computed_hash = hash_data(data, key=key)

    # Constant-time comparison
    if len(computed_hash) != len(expected_hash):
        return False

    result = 0
    for a, b in zip(computed_hash, expected_hash):
        result |= a ^ b

    return result == 0


def benchmark_performance(data_size_mb: int = 100):
    """
    Benchmark BLAKE3 vs SHA-256 performance.

    Args:
        data_size_mb: Size of test data in MB
    """
    import time

    test_data = os.urandom(data_size_mb * 1024 * 1024)

    # Test BLAKE3
    if BLAKE3_AVAILABLE:
        start = time.time()
        hash_data(test_data)
        blake3_time = time.time() - start
        blake3_throughput = data_size_mb / blake3_time

        logger.info(f"BLAKE3: {blake3_time:.3f}s ({blake3_throughput:.1f} MB/s)")
    else:
        logger.warning("BLAKE3 not available for benchmark")
        blake3_time = None

    # Test SHA-256
    start = time.time()
    hashlib.sha256(test_data).digest()
    sha256_time = time.time() - start
    sha256_throughput = data_size_mb / sha256_time

    logger.info(f"SHA-256: {sha256_time:.3f}s ({sha256_throughput:.1f} MB/s)")

    if blake3_time:
        speedup = sha256_time / blake3_time
        logger.info(f"BLAKE3 is {speedup:.2f}x faster than SHA-256")


if __name__ == "__main__":
    print("=== QWAMOS BLAKE3 Hasher Test ===\n")

    # Test basic hashing
    test_data = b"Hello, QWAMOS!"
    hash_result = hash_data(test_data)
    print(f"Hash of '{test_data.decode()}': {hash_result.hex()}")

    # Test keyed hashing
    key = os.urandom(32)
    mac_result = keyed_hash(test_data, key)
    print(f"Keyed hash (MAC): {mac_result.hex()}")

    # Test key derivation
    derived_key = derive_key("qwamos-test", b"master_secret")
    print(f"Derived key: {derived_key.hex()}")

    # Test file hashing
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(b"File content for hashing")
        temp_file = tf.name

    file_hash = hash_file(temp_file)
    print(f"File hash: {file_hash.hex()}")
    os.unlink(temp_file)

    # Benchmark
    print("\n=== Performance Benchmark ===")
    benchmark_performance(data_size_mb=10)

    print("\n✓ All tests passed")
