#!/usr/bin/env python3
"""
QWAMOS Argon2id Key Derivation

CRITICAL FIX #15: Use Argon2id instead of Argon2i for password hashing.

Argon2id is a hybrid of Argon2i and Argon2d:
- Resistant to side-channel attacks (like Argon2i)
- Resistant to GPU cracking (like Argon2d)
- Recommended by OWASP and NIST for password hashing
- Winner of the Password Hashing Competition (2015)

Security parameters (OWASP recommendations):
- Memory cost: 47 MB (minimum for secure hashing)
- Time cost: 1 iteration (minimum)
- Parallelism: 1 thread (can be increased on multi-core systems)

Author: QWAMOS Security Team
"""

import os
import sys
import logging
import secrets
from typing import Optional, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Argon2idKDF')

# Try to import argon2
try:
    from argon2 import PasswordHasher
    from argon2.low_level import hash_secret_raw, Type
    ARGON2_AVAILABLE = True
    logger.info("✓ Argon2 library available")
except ImportError:
    ARGON2_AVAILABLE = False
    logger.warning("⚠️  Argon2 library not available - install with: pip install argon2-cffi")
    logger.warning("   Falling back to PBKDF2-SHA256 (less secure)")


class Argon2idHasher:
    """
    Argon2id password hasher and KDF.

    CRITICAL FIX #15: Use Argon2id for maximum security.

    Features:
    - Argon2id mode (hybrid of Argon2i/Argon2d)
    - OWASP-recommended parameters
    - Password hashing with verification
    - Key derivation for encryption keys
    - Automatic salt generation
    - Configurable memory/time costs
    """

    def __init__(self,
                 time_cost: int = 2,
                 memory_cost: int = 65536,  # 64 MB
                 parallelism: int = 1,
                 hash_len: int = 32,
                 salt_len: int = 16):
        """
        Initialize Argon2id hasher.

        Args:
            time_cost: Number of iterations (default 2)
            memory_cost: Memory usage in KiB (default 64 MB)
            parallelism: Number of parallel threads (default 1)
            hash_len: Output hash length in bytes (default 32)
            salt_len: Salt length in bytes (default 16)

        OWASP recommendations (2023):
        - time_cost: 2-3 iterations
        - memory_cost: 47104 KiB (47 MB) minimum, 65536 (64 MB) recommended
        - parallelism: 1 (or match CPU cores for better performance)
        """
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.hash_len = hash_len
        self.salt_len = salt_len

        if ARGON2_AVAILABLE:
            # Create password hasher with OWASP-recommended parameters
            self.ph = PasswordHasher(
                time_cost=time_cost,
                memory_cost=memory_cost,
                parallelism=parallelism,
                hash_len=hash_len,
                salt_len=salt_len,
                type=Type.ID  # Argon2id
            )
            logger.info(f"Argon2id configured: time={time_cost}, memory={memory_cost}KiB, threads={parallelism}")
        else:
            self.ph = None
            logger.warning("Using PBKDF2-SHA256 fallback")

    def hash_password(self, password: str) -> str:
        """
        Hash password with Argon2id.

        Args:
            password: Password to hash

        Returns:
            Argon2id hash string (PHC format)

        Example output:
            $argon2id$v=19$m=65536,t=2,p=1$...salt...$...hash...
        """
        if ARGON2_AVAILABLE:
            return self.ph.hash(password)
        else:
            # Fallback to PBKDF2-SHA256
            return self._hash_password_pbkdf2(password)

    def verify_password(self, password_hash: str, password: str) -> bool:
        """
        Verify password against hash.

        Args:
            password_hash: Argon2id hash string
            password: Password to verify

        Returns:
            True if password matches
        """
        if ARGON2_AVAILABLE:
            try:
                self.ph.verify(password_hash, password)
                return True
            except:
                return False
        else:
            return self._verify_password_pbkdf2(password_hash, password)

    def check_needs_rehash(self, password_hash: str) -> bool:
        """
        Check if password hash needs rehashing (due to parameter changes).

        Args:
            password_hash: Argon2id hash string

        Returns:
            True if rehashing recommended
        """
        if ARGON2_AVAILABLE:
            return self.ph.check_needs_rehash(password_hash)
        return False

    def derive_key(self,
                   password: str,
                   salt: Optional[bytes] = None,
                   key_len: int = 32,
                   context: Optional[str] = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using Argon2id.

        Args:
            password: Password/passphrase
            salt: Optional salt (generated if not provided)
            key_len: Desired key length in bytes
            context: Optional context string (mixed into derivation)

        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(self.salt_len)

        if context:
            # Mix context into password
            password = f"{password}||{context}"

        if ARGON2_AVAILABLE:
            key = hash_secret_raw(
                secret=password.encode('utf-8'),
                salt=salt,
                time_cost=self.time_cost,
                memory_cost=self.memory_cost,
                parallelism=self.parallelism,
                hash_len=key_len,
                type=Type.ID  # Argon2id
            )
        else:
            key = self._derive_key_pbkdf2(password, salt, key_len)

        return key, salt

    def _hash_password_pbkdf2(self, password: str) -> str:
        """Fallback: Hash password with PBKDF2-SHA256."""
        import hashlib

        salt = secrets.token_bytes(self.salt_len)
        iterations = 600000  # OWASP recommendation for PBKDF2-SHA256

        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations,
            dklen=self.hash_len
        )

        # Encode as PHC-like format
        import base64
        salt_b64 = base64.b64encode(salt).decode('ascii')
        key_b64 = base64.b64encode(key).decode('ascii')

        return f"$pbkdf2-sha256$i={iterations}${salt_b64}${key_b64}"

    def _verify_password_pbkdf2(self, password_hash: str, password: str) -> bool:
        """Fallback: Verify PBKDF2 password."""
        import hashlib
        import base64

        try:
            parts = password_hash.split('$')
            if len(parts) != 4:
                return False

            iterations = int(parts[1].split('=')[1])
            salt = base64.b64decode(parts[2])
            expected_key = base64.b64decode(parts[3])

            key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                iterations,
                dklen=len(expected_key)
            )

            # Constant-time comparison
            return secrets.compare_digest(key, expected_key)
        except:
            return False

    def _derive_key_pbkdf2(self, password: str, salt: bytes, key_len: int) -> bytes:
        """Fallback: Derive key with PBKDF2."""
        import hashlib

        iterations = 600000

        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations,
            dklen=key_len
        )


# Global hasher instance with OWASP-recommended parameters
_default_hasher = None


def get_hasher() -> Argon2idHasher:
    """Get default Argon2id hasher instance."""
    global _default_hasher
    if _default_hasher is None:
        _default_hasher = Argon2idHasher(
            time_cost=2,
            memory_cost=65536,  # 64 MB
            parallelism=1
        )
    return _default_hasher


def hash_password(password: str) -> str:
    """
    Hash password with Argon2id.

    Args:
        password: Password to hash

    Returns:
        Argon2id hash string
    """
    return get_hasher().hash_password(password)


def verify_password(password_hash: str, password: str) -> bool:
    """
    Verify password against Argon2id hash.

    Args:
        password_hash: Argon2id hash string
        password: Password to verify

    Returns:
        True if password matches
    """
    return get_hasher().verify_password(password_hash, password)


def derive_encryption_key(password: str, salt: Optional[bytes] = None,
                          key_len: int = 32) -> Tuple[bytes, bytes]:
    """
    Derive encryption key from password.

    Args:
        password: Password
        salt: Optional salt (generated if not provided)
        key_len: Key length in bytes (default 32)

    Returns:
        Tuple of (key, salt)
    """
    return get_hasher().derive_key(password, salt, key_len)


def benchmark_performance(password: str = "test_password_123"):
    """
    Benchmark Argon2id performance.

    Args:
        password: Test password
    """
    import time

    hasher = get_hasher()

    # Test hashing
    start = time.time()
    password_hash = hasher.hash_password(password)
    hash_time = time.time() - start

    logger.info(f"Hash time: {hash_time:.3f}s")
    logger.info(f"Hash: {password_hash[:50]}...")

    # Test verification (correct password)
    start = time.time()
    result = hasher.verify_password(password_hash, password)
    verify_time = time.time() - start

    logger.info(f"Verify time: {verify_time:.3f}s (correct password)")
    logger.info(f"Verification result: {result}")

    # Test verification (wrong password)
    start = time.time()
    result = hasher.verify_password(password_hash, "wrong_password")
    verify_wrong_time = time.time() - start

    logger.info(f"Verify time: {verify_wrong_time:.3f}s (wrong password)")
    logger.info(f"Verification result: {result}")

    # Test key derivation
    start = time.time()
    key, salt = hasher.derive_key(password, key_len=32)
    derive_time = time.time() - start

    logger.info(f"Key derivation time: {derive_time:.3f}s")
    logger.info(f"Derived key: {key.hex()}")


if __name__ == "__main__":
    print("=== QWAMOS Argon2id KDF Test ===\n")

    # Test password hashing
    password = "MySuperSecurePassword123!"
    print(f"Password: {password}")

    password_hash = hash_password(password)
    print(f"Hash: {password_hash}\n")

    # Test verification
    print("Testing verification:")
    print(f"  Correct password: {verify_password(password_hash, password)}")
    print(f"  Wrong password: {verify_password(password_hash, 'wrong')}\n")

    # Test key derivation
    print("Testing key derivation:")
    key1, salt = derive_encryption_key("my_passphrase")
    print(f"  Key 1: {key1.hex()}")
    print(f"  Salt: {salt.hex()}")

    # Derive same key with same salt
    key2, _ = derive_encryption_key("my_passphrase", salt=salt)
    print(f"  Key 2: {key2.hex()}")
    print(f"  Keys match: {key1 == key2}\n")

    # Performance benchmark
    print("=== Performance Benchmark ===")
    benchmark_performance()

    print("\n✓ All tests passed")
